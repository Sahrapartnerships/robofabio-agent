#!/usr/bin/env python3
"""Command-line interface for TikTok Poster Bot."""
import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_LEVEL, LOG_FORMAT
import logging

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
)

from auth import TikTokAuth
from tiktok_poster import TikTokPoster
from scheduler import PostScheduler, ScheduledPost
from datetime import datetime, timedelta


def cmd_login(args):
    """Handle login command."""
    async def do_login():
        async with TikTokAuth() as auth:
            success = await auth.login(force=args.force)
            if success:
                print("✅ Login successful! Session saved.")
            else:
                print("❌ Login failed!")
                sys.exit(1)
    
    asyncio.run(do_login())


def cmd_logout(args):
    """Handle logout command."""
    async def do_logout():
        auth = TikTokAuth()
        await auth.start()
        try:
            await auth.create_context()
            await auth.logout()
            print("✅ Logged out successfully!")
        finally:
            await auth.close()
    
    asyncio.run(do_logout())


def cmd_post(args):
    """Handle post command."""
    async def do_post():
        async with TikTokPoster() as poster:
            # Login
            login_success = await poster.auth.login(force=args.force_login)
            if not login_success:
                print("❌ Login failed!")
                sys.exit(1)
            
            # Prepare hashtags
            hashtags = args.hashtags.split(",") if args.hashtags else []
            
            # Post or schedule
            if args.schedule_minutes:
                # Schedule the post
                from scheduler import PostScheduler, ScheduledPost
                
                post = ScheduledPost(
                    image_paths=args.images,
                    caption=args.caption,
                    hashtags=hashtags,
                    schedule_time=datetime.now() + timedelta(minutes=args.schedule_minutes),
                    who_can_view=args.visibility,
                    allow_comments=not args.disable_comments,
                    allow_duet=not args.disable_duet,
                    allow_stitch=not args.disable_stitch,
                )
                
                scheduler = PostScheduler()
                post_id = scheduler.schedule_post(post)
                
                schedule_time = datetime.now() + timedelta(minutes=args.schedule_minutes)
                print(f"✅ Post scheduled with ID: {post_id}")
                print(f"📅 Will be posted at: {schedule_time}")
            else:
                # Post immediately
                result = await poster.post_with_retry(
                    image_paths=args.images,
                    caption=args.caption,
                    hashtags=hashtags,
                    who_can_view=args.visibility,
                    allow_comments=not args.disable_comments,
                    allow_duet=not args.disable_duet,
                    allow_stitch=not args.disable_stitch,
                    max_retries=args.retries,
                )
                
                if result["success"]:
                    print("🎉 Post successful!")
                    if result.get("post_url"):
                        print(f"🔗 URL: {result['post_url']}")
                else:
                    print(f"❌ Post failed: {result.get('error')}")
                    sys.exit(1)
    
    asyncio.run(do_post())


def cmd_schedule(args):
    """Handle schedule command."""
    async def do_schedule():
        scheduler = PostScheduler()
        
        if args.list:
            # List scheduled posts
            posts = scheduler.get_all_posts()
            
            if not posts:
                print("No scheduled posts found.")
                return
            
            print(f"{'ID':<5} {'Status':<12} {'Schedule Time':<20} {'Caption'}")
            print("-" * 80)
            for post in posts:
                caption = post.caption[:40] + "..." if len(post.caption) > 40 else post.caption
                schedule_str = post.schedule_time.strftime("%Y-%m-%d %H:%M") if post.schedule_time else "N/A"
                print(f"{post.id:<5} {post.status:<12} {schedule_str:<20} {caption}")
        
        elif args.cancel:
            success = scheduler.cancel_post(args.cancel)
            if success:
                print(f"✅ Post {args.cancel} cancelled.")
            else:
                print(f"❌ Could not cancel post {args.cancel} (may already be posted)")
        
        elif args.delete:
            success = scheduler.delete_post(args.delete)
            if success:
                print(f"✅ Post {args.delete} deleted.")
            else:
                print(f"❌ Could not delete post {args.delete}")
        
        elif args.run:
            # Run the scheduler loop
            print("🚀 Starting scheduler (Ctrl+C to stop)...")
            await scheduler.run_scheduler(check_interval=args.interval)
    
    asyncio.run(do_schedule())


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="tiktok-poster",
        description="TikTok Poster Bot - Automated carousel posting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Login to TikTok
  tiktok-poster login

  # Post a carousel
  tiktok-poster post --images img1.jpg img2.jpg --caption "Hello!"

  # Schedule a post for 1 hour later
  tiktok-poster post --images *.jpg --caption "Scheduled!" --schedule-minutes 60

  # List scheduled posts
  tiktok-poster schedule --list

  # Run the scheduler daemon
  tiktok-poster schedule --run
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to TikTok")
    login_parser.add_argument("--force", action="store_true", help="Force re-login")
    login_parser.set_defaults(func=cmd_login)
    
    # Logout command
    logout_parser = subparsers.add_parser("logout", help="Logout and clear session")
    logout_parser.set_defaults(func=cmd_logout)
    
    # Post command
    post_parser = subparsers.add_parser("post", help="Post a carousel")
    post_parser.add_argument("--images", nargs="+", required=True, help="Image files")
    post_parser.add_argument("--caption", default="", help="Post caption")
    post_parser.add_argument("--hashtags", help="Comma-separated hashtags")
    post_parser.add_argument("--visibility", default="public", 
                            choices=["public", "friends", "private"],
                            help="Post visibility")
    post_parser.add_argument("--disable-comments", action="store_true", help="Disable comments")
    post_parser.add_argument("--disable-duet", action="store_true", help="Disable duets")
    post_parser.add_argument("--disable-stitch", action="store_true", help="Disable stitches")
    post_parser.add_argument("--schedule-minutes", type=int, metavar="MIN",
                            help="Schedule post for X minutes from now")
    post_parser.add_argument("--retries", type=int, default=3, help="Max retry attempts")
    post_parser.add_argument("--force-login", action="store_true", help="Force re-login")
    post_parser.set_defaults(func=cmd_post)
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Manage scheduled posts")
    schedule_parser.add_argument("--list", action="store_true", help="List all scheduled posts")
    schedule_parser.add_argument("--cancel", type=int, metavar="ID", help="Cancel a scheduled post")
    schedule_parser.add_argument("--delete", type=int, metavar="ID", help="Delete a post")
    schedule_parser.add_argument("--run", action="store_true", help="Run scheduler daemon")
    schedule_parser.add_argument("--interval", type=int, default=60, help="Check interval (seconds)")
    schedule_parser.set_defaults(func=cmd_schedule)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
