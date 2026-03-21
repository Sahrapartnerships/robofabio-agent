"""Test script for TikTok carousel posting."""
import argparse
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_LEVEL, LOG_FORMAT, MAX_IMAGES_PER_CAROUSEL
from auth import TikTokAuth
from tiktok_poster import TikTokPoster

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def create_test_images(output_dir: Path, count: int = 3) -> list:
    """Create simple test images for testing purposes."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        image_paths = []
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(count):
            # Create a simple colored image with text
            img = Image.new('RGB', (1080, 1920), color=(random.randint(50, 200), 
                                                         random.randint(50, 200), 
                                                         random.randint(50, 200)))
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = f"Test Image {i + 1}"
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Get text bbox
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            position = ((1080 - text_width) // 2, (1920 - text_height) // 2)
            draw.text(position, text, fill=(255, 255, 255), font=font)
            
            # Save
            img_path = output_dir / f"test_image_{i + 1}.jpg"
            img.save(img_path, quality=90)
            image_paths.append(str(img_path))
            logger.info(f"Created test image: {img_path}")
        
        return image_paths
        
    except ImportError:
        logger.error("Pillow not installed. Install with: pip install Pillow")
        return []
    except Exception as e:
        logger.error(f"Error creating test images: {e}")
        return []


import random


async def run_test(args):
    """Run the test posting workflow."""
    
    logger.info("=" * 60)
    logger.info("🚀 TikTok Carousel Poster - Test Script")
    logger.info("=" * 60)
    
    # Prepare images
    image_paths = []
    
    if args.images:
        # Use provided images
        for img_path in args.images:
            path = Path(img_path)
            if path.exists():
                image_paths.append(str(path.resolve()))
            else:
                logger.error(f"Image not found: {img_path}")
                return False
    elif args.create_test_images:
        # Create test images
        test_dir = Path(__file__).parent / "test_images"
        image_paths = create_test_images(test_dir, count=args.image_count)
        if not image_paths:
            logger.error("Failed to create test images. Please provide image paths manually.")
            return False
    else:
        logger.error("No images provided. Use --images to specify images or --create-test-images to generate test images.")
        return False
    
    logger.info(f"Using {len(image_paths)} images:")
    for img in image_paths:
        logger.info(f"  - {img}")
    
    # Initialize poster
    async with TikTokPoster() as poster:
        # Login
        logger.info("\n🔐 Logging in to TikTok...")
        login_success = await poster.auth.login(force=args.force_login)
        
        if not login_success:
            logger.error("❌ Login failed! Please check your credentials and try again.")
            return False
        
        logger.info("✅ Login successful!")
        
        # Prepare post arguments
        post_kwargs = {
            "image_paths": image_paths,
            "caption": args.caption,
            "hashtags": args.hashtags.split(",") if args.hashtags else [],
            "allow_comments": not args.disable_comments,
            "allow_duet": not args.disable_duet,
            "allow_stitch": not args.disable_stitch,
            "who_can_view": args.visibility,
        }
        
        # Add schedule if specified
        if args.schedule:
            schedule_time = datetime.now() + timedelta(minutes=args.schedule_delay)
            post_kwargs["schedule_time"] = schedule_time
            logger.info(f"📅 Scheduling post for: {schedule_time}")
        
        # Post
        logger.info("\n📤 Uploading carousel post...")
        
        if args.retry:
            result = await poster.post_with_retry(
                max_retries=args.max_retries,
                **post_kwargs
            )
        else:
            result = await poster.post_carousel(**post_kwargs)
        
        # Print result
        logger.info("\n" + "=" * 60)
        if result["success"]:
            logger.info("🎉 POST SUCCESSFUL!")
            if result.get("post_url"):
                logger.info(f"🔗 Post URL: {result['post_url']}")
        else:
            logger.error(f"❌ POST FAILED: {result.get('error', 'Unknown error')}")
        logger.info("=" * 60)
        
        return result["success"]


def main():
    """Parse arguments and run test."""
    parser = argparse.ArgumentParser(
        description="Test TikTok carousel posting bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create test images and post
  python test_post.py --create-test-images --caption "My test post!"
  
  # Post with specific images
  python test_post.py --images image1.jpg image2.jpg image3.jpg --caption "Hello!"
  
  # Post with hashtags
  python test_post.py --images *.jpg --caption "Great photos!" --hashtags "photo,art,design"
  
  # Force re-login
  python test_post.py --images image1.jpg --force-login
  
  # Schedule post for 30 minutes later
  python test_post.py --images image1.jpg --schedule --schedule-delay 30
        """
    )
    
    # Image options
    image_group = parser.add_mutually_exclusive_group(required=True)
    image_group.add_argument(
        "--images",
        nargs="+",
        help="Paths to image files for the carousel"
    )
    image_group.add_argument(
        "--create-test-images",
        action="store_true",
        help="Generate test images automatically"
    )
    
    parser.add_argument(
        "--image-count",
        type=int,
        default=3,
        help="Number of test images to create (default: 3, max: 35)"
    )
    
    # Post content
    parser.add_argument(
        "--caption",
        default="Test carousel post! 🎉 #test #automation",
        help="Caption for the post"
    )
    parser.add_argument(
        "--hashtags",
        help="Comma-separated list of hashtags (without #)"
    )
    
    # Post settings
    parser.add_argument(
        "--visibility",
        choices=["public", "friends", "private"],
        default="public",
        help="Post visibility (default: public)"
    )
    parser.add_argument(
        "--disable-comments",
        action="store_true",
        help="Disable comments on the post"
    )
    parser.add_argument(
        "--disable-duet",
        action="store_true",
        help="Disable duets"
    )
    parser.add_argument(
        "--disable-stitch",
        action="store_true",
        help="Disable stitches"
    )
    
    # Scheduling
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Schedule the post instead of posting immediately"
    )
    parser.add_argument(
        "--schedule-delay",
        type=int,
        default=30,
        help="Minutes from now to schedule the post (default: 30)"
    )
    
    # Authentication
    parser.add_argument(
        "--force-login",
        action="store_true",
        help="Force login even if a valid session exists"
    )
    
    # Retry logic
    parser.add_argument(
        "--retry",
        action="store_true",
        help="Enable automatic retry on failure"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Validate image count
    if args.image_count > MAX_IMAGES_PER_CAROUSEL:
        logger.error(f"Image count exceeds maximum of {MAX_IMAGES_PER_CAROUSEL}")
        sys.exit(1)
    
    # Run test
    try:
        success = asyncio.run(run_test(args))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
