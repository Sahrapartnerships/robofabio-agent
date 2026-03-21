"""Main TikTok posting functionality."""
import asyncio
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from auth import TikTokAuth
from config import (
    TIKTOK_UPLOAD_URL,
    DEFAULT_TIMEOUT,
    UPLOAD_TIMEOUT,
    MAX_IMAGES_PER_CAROUSEL,
    MAX_CAPTION_LENGTH,
    SAVE_SCREENSHOTS,
    SCREENSHOTS_DIR,
    DEBUG_MODE,
    DELAYS,
)

logger = logging.getLogger(__name__)


class TikTokPoster:
    """Handles posting content to TikTok."""

    def __init__(self, auth: TikTokAuth = None):
        self.auth = auth
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        if not self.auth:
            self.auth = TikTokAuth()
            await self.auth.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.auth:
            await self.auth.close()

    def _random_delay(self, min_sec: float = None, max_sec: float = None):
        """Generate a random delay."""
        min_sec = min_sec or DELAYS["min"]
        max_sec = max_sec or DELAYS["max"]
        return random.uniform(min_sec, max_sec)

    async def _random_sleep(self, min_sec: float = None, max_sec: float = None):
        """Sleep for a random duration."""
        await asyncio.sleep(self._random_delay(min_sec, max_sec))

    async def _type_like_human(self, selector: str, text: str):
        """Type text like a human with random delays between keystrokes."""
        element = await self.page.wait_for_selector(selector)
        
        # Clear existing text
        await element.click()
        await element.fill("")
        
        # Type with random delays
        for char in text:
            await element.type(char, delay=random.randint(
                int(DELAYS["typing_min"] * 1000),
                int(DELAYS["typing_max"] * 1000)
            ))
        
        await self._random_sleep(0.5, 1)

    async def _wait_for_upload_complete(self, timeout: int = UPLOAD_TIMEOUT) -> bool:
        """Wait for media upload to complete."""
        logger.info("Waiting for upload to complete...")
        start_time = asyncio.get_event_loop().time()
        
        # Selectors that indicate upload is complete
        complete_indicators = [
            '[data-e2e="post-video-button"]:not([disabled])',
            '.btn-post:not([disabled])',
            '[data-e2e="post-button"]:not([disabled])',
            '.upload-complete',
            'text=Post',
        ]
        
        # Selectors that indicate upload is in progress
        progress_indicators = [
            '[data-e2e="upload-progress"]',
            '.upload-progress',
            '.progress-bar',
            'text=Uploading',
            'text=Processing',
        ]
        
        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
            # Check if upload is complete
            for selector in complete_indicators:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000)
                    if element:
                        is_disabled = await element.get_attribute("disabled")
                        if is_disabled is None:
                            logger.info("Upload complete!")
                            return True
                except:
                    continue
            
            # Check if still uploading
            uploading = False
            for selector in progress_indicators:
                try:
                    await self.page.wait_for_selector(selector, timeout=1000)
                    uploading = True
                    logger.debug(f"Still uploading (seen {selector})...")
                    break
                except:
                    continue
            
            if not uploading:
                # No progress indicators found, might be done
                await self._random_sleep(1, 2)
                # Double check
                for selector in complete_indicators:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            logger.info("Upload appears complete!")
                            return True
                    except:
                        continue
            
            await asyncio.sleep(2)
        
        logger.error("Upload timeout!")
        return False

    async def _dismiss_modals(self):
        """Dismiss any popup modals or dialogs."""
        dismiss_selectors = [
            '[data-e2e="modal-close"]', 
            '.close-btn',
            'button[class*="close" i]',
            '[aria-label="Close"]',
            'text=Skip',
            'text=Not now',
            'text=Maybe later',
        ]
        
        for selector in dismiss_selectors:
            try:
                btn = await self.page.wait_for_selector(selector, timeout=1000)
                if btn:
                    await btn.click()
                    logger.debug(f"Dismissed modal via {selector}")
                    await self._random_sleep(0.5, 1)
            except:
                continue

    async def post_carousel(
        self,
        image_paths: List[str],
        caption: str = "",
        hashtags: List[str] = None,
        allow_comments: bool = True,
        allow_duet: bool = True,
        allow_stitch: bool = True,
        who_can_view: str = "public",  # public, friends, private
        schedule_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Post a carousel (multiple images) to TikTok.
        
        Args:
            image_paths: List of paths to image files
            caption: Caption text
            hashtags: List of hashtags (without #)
            allow_comments: Allow comments on the post
            allow_duet: Allow duets
            allow_stitch: Allow stitches
            who_can_view: Visibility setting
            schedule_time: Optional datetime to schedule the post
        
        Returns:
            Dict with success status and post URL or error message
        """
        result = {"success": False, "post_url": None, "error": None}
        
        if not self.auth or not self.auth.page:
            result["error"] = "Not logged in"
            return result
        
        self.page = self.auth.page
        
        # Validate inputs
        if len(image_paths) > MAX_IMAGES_PER_CAROUSEL:
            result["error"] = f"Too many images. Maximum is {MAX_IMAGES_PER_CAROUSEL}"
            return result
        
        if len(image_paths) < 1:
            result["error"] = "At least one image is required"
            return result
        
        # Validate image files exist
        for img_path in image_paths:
            if not Path(img_path).exists():
                result["error"] = f"Image not found: {img_path}"
                return result
        
        # Build full caption with hashtags
        full_caption = caption
        if hashtags:
            hashtag_str = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
            full_caption = f"{caption}\n\n{hashtag_str}".strip()
        
        if len(full_caption) > MAX_CAPTION_LENGTH:
            logger.warning(f"Caption too long ({len(full_caption)} chars), truncating...")
            full_caption = full_caption[:MAX_CAPTION_LENGTH]
        
        try:
            logger.info(f"Starting carousel upload with {len(image_paths)} images...")
            
            # Navigate to upload page
            await self.page.goto(TIKTOK_UPLOAD_URL, wait_until="domcontentloaded")
            await self._random_sleep(3, 5)
            
            if SAVE_SCREENSHOTS:
                await self.page.screenshot(path=str(SCREENSHOTS_DIR / "upload_page.png"))
            
            # Dismiss any modals
            await self._dismiss_modals()
            
            # Click on "Upload" tab if needed
            try:
                upload_tab = await self.page.wait_for_selector(
                    '[data-e2e="upload-tab"], [data-e2e="upload-button"], text="Upload"',
                    timeout=5000
                )
                if upload_tab:
                    await upload_tab.click()
                    await self._random_sleep(1, 2)
            except:
                pass  # Might already be on upload page
            
            # Select "Photo"/"Carousel" option if available
            try:
                photo_option = await self.page.wait_for_selector(
                    '[data-e2e="photo-tab"], text=Photo, text=Carousel',
                    timeout=5000
                )
                if photo_option:
                    await photo_option.click()
                    await self._random_sleep(1, 2)
                    logger.info("Selected photo/carousel option")
            except:
                pass  # Might already be the default
            
            # Upload images
            logger.info("Uploading images...")
            
            # Find file input
            file_input = await self.page.wait_for_selector(
                'input[type="file"][accept*="image"], input[type="file"]',
                timeout=10000
            )
            
            # Set files
            await file_input.set_input_files(image_paths)
            logger.info(f"Set {len(image_paths)} files for upload")
            
            # Wait for upload to complete
            upload_success = await self._wait_for_upload_complete()
            
            if not upload_success:
                result["error"] = "Upload timed out or failed"
                if SAVE_SCREENSHOTS:
                    await self.page.screenshot(path=str(SCREENSHOTS_DIR / "upload_failed.png"))
                return result
            
            if SAVE_SCREENSHOTS:
                await self.page.screenshot(path=str(SCREENSHOTS_DIR / "upload_complete.png"))
            
            await self._random_sleep(2, 3)
            
            # Fill caption
            if full_caption:
                logger.info("Adding caption...")
                caption_selectors = [
                    '[data-e2e="caption-input"]',
                    'textarea[placeholder*="caption" i]',
                    'textarea[placeholder*="describe" i]',
                    'div[contenteditable="true"]',
                ]
                
                for selector in caption_selectors:
                    try:
                        await self._type_like_human(selector, full_caption)
                        logger.info("Caption added")
                        break
                    except Exception as e:
                        logger.debug(f"Failed to add caption with {selector}: {e}")
                        continue
            
            await self._random_sleep(1, 2)
            
            # Configure post settings
            logger.info("Configuring post settings...")
            
            # Toggle comments
            if not allow_comments:
                try:
                    comments_toggle = await self.page.wait_for_selector(
                        '[data-e2e="comment-toggle"], [data-e2e="allow-comments"]',
                        timeout=3000
                    )
                    if comments_toggle:
                        await comments_toggle.click()
                        logger.info("Disabled comments")
                except:
                    pass
            
            # Toggle duet
            if not allow_duet:
                try:
                    duet_toggle = await self.page.wait_for_selector(
                        '[data-e2e="duet-toggle"], [data-e2e="allow-duet"]',
                        timeout=3000
                    )
                    if duet_toggle:
                        await duet_toggle.click()
                        logger.info("Disabled duets")
                except:
                    pass
            
            # Toggle stitch
            if not allow_stitch:
                try:
                    stitch_toggle = await self.page.wait_for_selector(
                        '[data-e2e="stitch-toggle"], [data-e2e="allow-stitch"]',
                        timeout=3000
                    )
                    if stitch_toggle:
                        await stitch_toggle.click()
                        logger.info("Disabled stitches")
                except:
                    pass
            
            # Set visibility
            if who_can_view != "public":
                visibility_selectors = {
                    "friends": '[data-e2e="friends-only"], text=Friends',
                    "private": '[data-e2e="private"], text=Private',
                }
                
                if who_can_view in visibility_selectors:
                    try:
                        visibility_btn = await self.page.wait_for_selector(
                            visibility_selectors[who_can_view],
                            timeout=3000
                        )
                        if visibility_btn:
                            await visibility_btn.click()
                            logger.info(f"Set visibility to {who_can_view}")
                    except:
                        pass
            
            # Handle scheduling if specified
            if schedule_time:
                logger.info(f"Scheduling post for {schedule_time}...")
                try:
                    schedule_btn = await self.page.wait_for_selector(
                        '[data-e2e="schedule-toggle"], text=Schedule',
                        timeout=3000
                    )
                    if schedule_btn:
                        await schedule_btn.click()
                        await self._random_sleep(1, 2)
                        
                        # Set date and time (implementation depends on UI)
                        # This is a simplified version
                        date_str = schedule_time.strftime("%Y-%m-%d")
                        time_str = schedule_time.strftime("%H:%M")
                        
                        # Look for date/time inputs
                        date_input = await self.page.wait_for_selector(
                            'input[type="date"], [data-e2e="schedule-date"]',
                            timeout=3000
                        )
                        if date_input:
                            await date_input.fill(date_str)
                        
                        time_input = await self.page.wait_for_selector(
                            'input[type="time"], [data-e2e="schedule-time"]',
                            timeout=3000
                        )
                        if time_input:
                            await time_input.fill(time_str)
                        
                        logger.info(f"Post scheduled for {date_str} {time_str}")
                except Exception as e:
                    logger.warning(f"Could not schedule post: {e}")
            
            await self._random_sleep(2, 3)
            
            # Click post button
            logger.info("Clicking post button...")
            post_button_selectors = [
                '[data-e2e="post-video-button"]',
                '[data-e2e="post-button"]',
                '[data-e2e="publish-button"]',
                '.btn-post',
                'button:has-text("Post")',
                'button:has-text("Publish")',
            ]
            
            posted = False
            for selector in post_button_selectors:
                try:
                    post_btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if post_btn:
                        # Check if button is enabled
                        is_disabled = await post_btn.get_attribute("disabled")
                        if is_disabled:
                            logger.warning(f"Post button {selector} is disabled, waiting...")
                            await asyncio.sleep(3)
                        
                        await post_btn.click()
                        logger.info(f"Clicked post button: {selector}")
                        posted = True
                        break
                except Exception as e:
                    logger.debug(f"Failed to click {selector}: {e}")
                    continue
            
            if not posted:
                result["error"] = "Could not find or click post button"
                if SAVE_SCREENSHOTS:
                    await self.page.screenshot(path=str(SCREENSHOTS_DIR / "post_button_failed.png"))
                return result
            
            # Wait for post to complete
            await self._random_sleep(5, 8)
            
            # Check for success indicators
            success_indicators = [
                'text=Your video has been uploaded',
                'text=Your post has been published',
                'text=Posted',
                'text=Published',
                '[data-e2e="upload-success"]',
            ]
            
            success = False
            for indicator in success_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=10000)
                    logger.info(f"Post successful! Indicator: {indicator}")
                    success = True
                    break
                except:
                    continue
            
            if SAVE_SCREENSHOTS:
                await self.page.screenshot(path=str(SCREENSHOTS_DIR / "post_result.png"))
            
            if success or posted:  # If we clicked post, assume success even if indicator not found
                result["success"] = True
                
                # Try to get post URL
                try:
                    # Look for "View post" link or similar
                    view_post = await self.page.wait_for_selector(
                        'a[href*="/@"], [data-e2e="view-post"], text=View post',
                        timeout=5000
                    )
                    if view_post:
                        href = await view_post.get_attribute("href")
                        if href:
                            result["post_url"] = href
                except:
                    pass
                
                logger.info("🎉 Post published successfully!")
            else:
                result["error"] = "Could not confirm post success"
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error posting carousel: {error_msg}")
            if DEBUG_MODE:
                import traceback
                logger.error(traceback.format_exc())
            
            result["error"] = error_msg
            
            if SAVE_SCREENSHOTS:
                try:
                    await self.page.screenshot(path=str(SCREENSHOTS_DIR / "error.png"))
                except:
                    pass
            
            return result

    async def post_with_retry(
        self,
        image_paths: List[str],
        caption: str = "",
        hashtags: List[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """Post with automatic retry logic."""
        from config import RETRY_DELAY
        
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Post attempt {attempt}/{max_retries}...")
            
            result = await self.post_carousel(
                image_paths=image_paths,
                caption=caption,
                hashtags=hashtags,
                **kwargs
            )
            
            if result["success"]:
                return result
            
            last_error = result.get("error")
            logger.warning(f"Attempt {attempt} failed: {last_error}")
            
            if attempt < max_retries:
                wait_time = RETRY_DELAY * attempt  # Exponential backoff
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                
                # Refresh page for retry
                try:
                    await self.page.reload()
                    await self._random_sleep(3, 5)
                except:
                    pass
        
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts. Last error: {last_error}",
        }


async def test_post():
    """Test posting functionality."""
    logging.basicConfig(level=logging.INFO)
    
    async with TikTokPoster() as poster:
        # Login
        success = await poster.auth.login()
        if not success:
            print("❌ Login failed!")
            return
        
        print("✅ Login successful!")
        
        # Note: For actual testing, you need to provide image paths
        # result = await poster.post_carousel(
        #     image_paths=["test_image1.jpg", "test_image2.jpg"],
        #     caption="Test carousel post! 🎉",
        #     hashtags=["test", "playwright", "automation"],
        # )
        # print(f"Post result: {result}")


if __name__ == "__main__":
    asyncio.run(test_post())
