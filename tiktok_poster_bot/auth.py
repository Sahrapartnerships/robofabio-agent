"""Authentication and session management for TikTok."""
import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from playwright.async_api import Page, Browser, async_playwright, BrowserContext

from config import (
    TIKTOK_LOGIN_URL,
    TIKTOK_URL,
    SESSION_STORAGE_FILE,
    SESSION_EXPIRY_DAYS,
    HEADLESS,
    BROWSER_TYPE,
    SLOW_MO,
    DEFAULT_TIMEOUT,
    NAVIGATION_TIMEOUT,
    VIEWPORT,
    USER_AGENT,
    SCREENSHOTS_DIR,
    SAVE_SCREENSHOTS,
    DEBUG_MODE,
    DELAYS,
)

logger = logging.getLogger(__name__)


class TikTokAuth:
    """Handles TikTok authentication and session management."""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Initialize browser."""
        logger.info("Starting browser...")
        self._playwright = await async_playwright().start()
        
        browser_kwargs = {
            "headless": HEADLESS,
            "slow_mo": SLOW_MO,
        }
        
        if BROWSER_TYPE == "firefox":
            self.browser = await self._playwright.firefox.launch(**browser_kwargs)
        elif BROWSER_TYPE == "webkit":
            self.browser = await self._playwright.webkit.launch(**browser_kwargs)
        else:
            self.browser = await self._playwright.chromium.launch(**browser_kwargs)
        
        logger.info(f"Browser started: {BROWSER_TYPE}")

    async def close(self):
        """Close browser and cleanup."""
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Browser closed")

    def _random_delay(self, min_sec: float = None, max_sec: float = None):
        """Generate a random delay."""
        min_sec = min_sec or DELAYS["min"]
        max_sec = max_sec or DELAYS["max"]
        return random.uniform(min_sec, max_sec)

    async def _random_sleep(self, min_sec: float = None, max_sec: float = None):
        """Sleep for a random duration."""
        await asyncio.sleep(self._random_delay(min_sec, max_sec))

    async def create_context(self, storage_state: Optional[Path] = None) -> BrowserContext:
        """Create a new browser context with optional storage state."""
        context_options = {
            "viewport": VIEWPORT,
            "user_agent": USER_AGENT,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "permissions": ["geolocation"],
        }
        
        if storage_state and storage_state.exists():
            logger.info(f"Loading storage state from {storage_state}")
            context_options["storage_state"] = str(storage_state)
        
        self.context = await self.browser.new_context(**context_options)
        
        # Add stealth scripts if enabled
        if True:  # Always use basic stealth
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
        
        self.page = await self.context.new_page()
        self.page.set_default_timeout(DEFAULT_TIMEOUT)
        self.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
        
        return self.context

    def _get_session_file(self, username: Optional[str] = None) -> Path:
        """Get session file path for a username."""
        if username:
            return SESSION_STORAGE_FILE.parent / f"tiktok_session_{username}.json"
        return SESSION_STORAGE_FILE

    def is_session_valid(self, username: Optional[str] = None) -> bool:
        """Check if a saved session exists and is not expired."""
        session_file = self._get_session_file(username)
        
        if not session_file.exists():
            logger.info(f"No session file found at {session_file}")
            return False
        
        # Check file age
        file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
        if file_age > timedelta(days=SESSION_EXPIRY_DAYS):
            logger.info(f"Session expired ({file_age.days} days old)")
            return False
        
        logger.info(f"Session file found and valid ({file_age.days} days old)")
        return True

    async def save_session(self, username: Optional[str] = None):
        """Save current session state."""
        if not self.context:
            logger.error("No context to save")
            return
        
        session_file = self._get_session_file(username)
        storage_state = await self.context.storage_state(path=str(session_file))
        logger.info(f"Session saved to {session_file}")

    async def check_logged_in(self) -> bool:
        """Check if currently logged in to TikTok."""
        if not self.page:
            return False
        
        try:
            # Navigate to TikTok
            await self.page.goto(TIKTOK_URL, wait_until="domcontentloaded")
            await self._random_sleep(2, 4)
            
            # Check for login indicators
            # Look for "Following" feed or profile link
            login_indicators = [
                '[data-e2e="following-feed"]', 
                '[data-e2e="profile-icon"]',
                '[data-e2e="nav-profile"]',
                'a[href*="/@"]',
                '.tiktok-avatar',
            ]
            
            for selector in login_indicators:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        logger.info(f"Login detected via {selector}")
                        return True
                except:
                    continue
            
            # Alternative: check for login button
            login_button = await self.page.query_selector('[data-e2e="top-login-button"], [data-e2e="login-button"]')
            if login_button:
                logger.info("Not logged in - login button found")
                return False
            
            logger.info("Login status unclear, assuming not logged in")
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    async def handle_2fa(self) -> bool:
        """Handle 2FA if prompted. Returns True if 2FA was handled."""
        logger.info("Checking for 2FA prompt...")
        
        try:
            # Common 2FA selectors
            two_fa_selectors = [
                'input[name="verifyCode"]',
                'input[placeholder*="code" i]',
                'input[placeholder*="verification" i]',
                '[data-e2e="verify-code-input"]',
                'text=Enter verification code',
                'text=Verify',
                'text=Two-factor',
                'text=2FA',
            ]
            
            found_2fa = False
            for selector in two_fa_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        found_2fa = True
                        logger.info(f"2FA prompt detected: {selector}")
                        break
                except:
                    continue
            
            if not found_2fa:
                logger.info("No 2FA prompt detected")
                return False
            
            if SAVE_SCREENSHOTS:
                await self.page.screenshot(path=str(SCREENSHOTS_DIR / "2fa_prompt.png"))
            
            logger.warning("=" * 60)
            logger.warning("2FA REQUIRED!")
            logger.warning("Please enter the verification code on the opened page.")
            logger.warning(f"You have {DEFAULT_TIMEOUT // 1000} seconds...")
            logger.warning("=" * 60)
            
            # Wait for user to complete 2FA
            await self.page.wait_for_load_state("networkidle", timeout=DEFAULT_TIMEOUT * 2)
            await self._random_sleep(3, 5)
            
            # Check if still on 2FA page
            for selector in two_fa_selectors[:4]:  # Check input selectors
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    logger.warning("Still on 2FA page - user may not have completed it")
                    return False
                except:
                    pass
            
            logger.info("2FA appears to be completed")
            return True
            
        except Exception as e:
            logger.error(f"Error handling 2FA: {e}")
            return False

    async def login_manual(self) -> bool:
        """Open login page and wait for user to manually log in."""
        logger.info("Opening TikTok login page...")
        
        if not self.page:
            await self.create_context()
        
        try:
            # Navigate to login page
            await self.page.goto(TIKTOK_LOGIN_URL, wait_until="domcontentloaded")
            await self._random_sleep(3, 5)
            
            if SAVE_SCREENSHOTS:
                await self.page.screenshot(path=str(SCREENSHOTS_DIR / "login_page.png"))
            
            logger.warning("=" * 60)
            logger.warning("MANUAL LOGIN REQUIRED!")
            logger.warning("Please log in to TikTok on the opened browser window.")
            logger.warning("The script will wait for you to complete the login.")
            logger.warning("=" * 60)
            
            # Wait for navigation after login
            max_wait = 300  # 5 minutes max wait
            waited = 0
            check_interval = 5
            
            while waited < max_wait:
                await asyncio.sleep(check_interval)
                waited += check_interval
                
                if await self.check_logged_in():
                    logger.info("Login successful!")
                    await self._random_sleep(2, 3)
                    await self.save_session()
                    return True
                
                # Check for 2FA
                if await self.handle_2fa():
                    if await self.check_logged_in():
                        await self.save_session()
                        return True
            
            logger.error("Login timeout - user did not complete login in time")
            return False
            
        except Exception as e:
            logger.error(f"Error during manual login: {e}")
            if DEBUG_MODE:
                import traceback
                logger.error(traceback.format_exc())
            return False

    async def login(self, username: Optional[str] = None, force: bool = False) -> bool:
        """Login to TikTok, using saved session if available."""
        session_file = self._get_session_file(username)
        
        # Try to use existing session
        if not force and self.is_session_valid(username):
            logger.info("Attempting to use saved session...")
            await self.create_context(storage_state=session_file)
            
            if await self.check_logged_in():
                logger.info("Successfully logged in using saved session!")
                return True
            else:
                logger.info("Saved session invalid, proceeding with manual login...")
        
        # Manual login
        await self.create_context()
        return await self.login_manual()

    async def logout(self):
        """Logout and clear session."""
        if self.page:
            try:
                # Navigate to settings and logout
                await self.page.goto(f"{TIKTOK_URL}/setting", wait_until="domcontentloaded")
                await self._random_sleep(2, 3)
                
                # Click logout if available
                logout_selectors = [
                    '[data-e2e="logout-button"]',
                    'text=Log out',
                    'text=Logout',
                ]
                
                for selector in logout_selectors:
                    try:
                        btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if btn:
                            await btn.click()
                            await self._random_sleep(2, 3)
                            logger.info("Logged out successfully")
                            break
                    except:
                        continue
                        
            except Exception as e:
                logger.error(f"Error during logout: {e}")
        
        # Clear session files
        session_file = self._get_session_file()
        if session_file.exists():
            session_file.unlink()
            logger.info(f"Session file removed: {session_file}")


async def test_auth():
    """Test authentication."""
    logging.basicConfig(level=logging.INFO)
    
    auth = TikTokAuth()
    async with auth:
        success = await auth.login()
        if success:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")


if __name__ == "__main__":
    asyncio.run(test_auth())
