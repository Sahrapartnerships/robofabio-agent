"""Optional scheduler for delayed TikTok posts."""
import asyncio
import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from config import SCHEDULER_DB_PATH, SCHEDULER_ENABLED

logger = logging.getLogger(__name__)


@dataclass
class ScheduledPost:
    """Represents a scheduled post."""
    id: Optional[int] = None
    image_paths: List[str] = None
    caption: str = ""
    hashtags: List[str] = None
    schedule_time: datetime = None
    status: str = "pending"  # pending, posted, failed, cancelled
    created_at: datetime = None
    posted_at: Optional[datetime] = None
    error_message: Optional[str] = None
    post_url: Optional[str] = None
    allow_comments: bool = True
    allow_duet: bool = True
    allow_stitch: bool = True
    who_can_view: str = "public"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.image_paths is None:
            self.image_paths = []
        if self.hashtags is None:
            self.hashtags = []


class PostScheduler:
    """Schedules and manages TikTok posts."""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or SCHEDULER_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_paths TEXT NOT NULL,
                    caption TEXT,
                    hashtags TEXT,
                    schedule_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    posted_at TIMESTAMP,
                    error_message TEXT,
                    post_url TEXT,
                    allow_comments BOOLEAN DEFAULT 1,
                    allow_duet BOOLEAN DEFAULT 1,
                    allow_stitch BOOLEAN DEFAULT 1,
                    who_can_view TEXT DEFAULT 'public'
                )
            """)
            conn.commit()
        logger.info(f"Scheduler database initialized: {self.db_path}")
    
    def schedule_post(self, post: ScheduledPost) -> int:
        """Add a post to the schedule. Returns the post ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO scheduled_posts 
                (image_paths, caption, hashtags, schedule_time, status, created_at,
                 allow_comments, allow_duet, allow_stitch, who_can_view)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    json.dumps(post.image_paths),
                    post.caption,
                    json.dumps(post.hashtags) if post.hashtags else "[]",
                    post.schedule_time.isoformat() if post.schedule_time else None,
                    post.status,
                    post.created_at.isoformat() if post.created_at else datetime.now().isoformat(),
                    post.allow_comments,
                    post.allow_duet,
                    post.allow_stitch,
                    post.who_can_view,
                )
            )
            conn.commit()
            post_id = cursor.lastrowid
            logger.info(f"Post scheduled with ID: {post_id}")
            return post_id
    
    def get_pending_posts(self) -> List[ScheduledPost]:
        """Get all pending posts scheduled for now or earlier."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            now = datetime.now().isoformat()
            rows = conn.execute(
                """
                SELECT * FROM scheduled_posts 
                WHERE status = 'pending' AND schedule_time <= ?
                ORDER BY schedule_time ASC
                """,
                (now,)
            ).fetchall()
            
            return [self._row_to_post(row) for row in rows]
    
    def get_all_posts(self, status: str = None) -> List[ScheduledPost]:
        """Get all posts, optionally filtered by status."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if status:
                rows = conn.execute(
                    "SELECT * FROM scheduled_posts WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM scheduled_posts ORDER BY created_at DESC"
                ).fetchall()
            
            return [self._row_to_post(row) for row in rows]
    
    def get_post(self, post_id: int) -> Optional[ScheduledPost]:
        """Get a specific post by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM scheduled_posts WHERE id = ?",
                (post_id,)
            ).fetchone()
            
            return self._row_to_post(row) if row else None
    
    def update_post_status(
        self, 
        post_id: int, 
        status: str, 
        error_message: str = None,
        post_url: str = None
    ):
        """Update the status of a scheduled post."""
        with sqlite3.connect(self.db_path) as conn:
            posted_at = datetime.now().isoformat() if status == "posted" else None
            conn.execute(
                """
                UPDATE scheduled_posts 
                SET status = ?, error_message = ?, post_url = ?, posted_at = ?
                WHERE id = ?
                """,
                (status, error_message, post_url, posted_at, post_id)
            )
            conn.commit()
            logger.info(f"Post {post_id} status updated to: {status}")
    
    def cancel_post(self, post_id: int) -> bool:
        """Cancel a pending post."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE scheduled_posts SET status = 'cancelled' WHERE id = ? AND status = 'pending'",
                (post_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM scheduled_posts WHERE id = ?",
                (post_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_post(self, row: sqlite3.Row) -> ScheduledPost:
        """Convert a database row to a ScheduledPost."""
        return ScheduledPost(
            id=row["id"],
            image_paths=json.loads(row["image_paths"]),
            caption=row["caption"] or "",
            hashtags=json.loads(row["hashtags"]) if row["hashtags"] else [],
            schedule_time=datetime.fromisoformat(row["schedule_time"]) if row["schedule_time"] else None,
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            posted_at=datetime.fromisoformat(row["posted_at"]) if row["posted_at"] else None,
            error_message=row["error_message"],
            post_url=row["post_url"],
            allow_comments=bool(row["allow_comments"]),
            allow_duet=bool(row["allow_duet"]),
            allow_stitch=bool(row["allow_stitch"]),
            who_can_view=row["who_can_view"] or "public",
        )
    
    async def run_scheduler(self, check_interval: int = 60):
        """
        Run the scheduler loop, checking for posts to publish.
        
        Args:
            check_interval: Seconds between checks
        """
        from tiktok_poster import TikTokPoster
        
        logger.info("Starting post scheduler...")
        
        async with TikTokPoster() as poster:
            # Initial login
            login_success = await poster.auth.login()
            if not login_success:
                logger.error("Failed to login, scheduler cannot start")
                return
            
            logger.info("Scheduler started, checking for posts every {check_interval}s")
            
            while True:
                try:
                    # Get pending posts
                    pending = self.get_pending_posts()
                    
                    if pending:
                        logger.info(f"Found {len(pending)} post(s) to publish")
                        
                        for post in pending:
                            try:
                                logger.info(f"Publishing post {post.id}: {post.caption[:50]}...")
                                
                                result = await poster.post_carousel(
                                    image_paths=post.image_paths,
                                    caption=post.caption,
                                    hashtags=post.hashtags,
                                    allow_comments=post.allow_comments,
                                    allow_duet=post.allow_duet,
                                    allow_stitch=post.allow_stitch,
                                    who_can_view=post.who_can_view,
                                )
                                
                                if result["success"]:
                                    self.update_post_status(
                                        post.id, 
                                        "posted",
                                        post_url=result.get("post_url")
                                    )
                                    logger.info(f"✅ Post {post.id} published successfully!")
                                else:
                                    self.update_post_status(
                                        post.id,
                                        "failed",
                                        error_message=result.get("error")
                                    )
                                    logger.error(f"❌ Post {post.id} failed: {result.get('error')}")
                                
                                # Wait between posts
                                await asyncio.sleep(10)
                                
                            except Exception as e:
                                self.update_post_status(post.id, "failed", error_message=str(e))
                                logger.error(f"Error publishing post {post.id}: {e}")
                    
                    # Wait before next check
                    await asyncio.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    await asyncio.sleep(check_interval)


def schedule_post_cli():
    """CLI for scheduling posts."""
    import argparse
    from datetime import datetime, timedelta
    
    parser = argparse.ArgumentParser(description="Schedule TikTok posts")
    parser.add_argument("--images", nargs="+", required=True, help="Image paths")
    parser.add_argument("--caption", default="", help="Post caption")
    parser.add_argument("--hashtags", help="Comma-separated hashtags")
    parser.add_argument("--schedule-time", help="ISO format datetime (e.g., 2024-03-21T15:30:00)")
    parser.add_argument("--minutes-from-now", type=int, help="Schedule X minutes from now")
    parser.add_argument("--visibility", default="public", choices=["public", "friends", "private"])
    
    args = parser.parse_args()
    
    # Determine schedule time
    if args.schedule_time:
        schedule_time = datetime.fromisoformat(args.schedule_time)
    elif args.minutes_from_now:
        schedule_time = datetime.now() + timedelta(minutes=args.minutes_from_now)
    else:
        schedule_time = datetime.now() + timedelta(minutes=30)
    
    # Create post
    post = ScheduledPost(
        image_paths=args.images,
        caption=args.caption,
        hashtags=args.hashtags.split(",") if args.hashtags else [],
        schedule_time=schedule_time,
        who_can_view=args.visibility,
    )
    
    # Schedule
    scheduler = PostScheduler()
    post_id = scheduler.schedule_post(post)
    
    print(f"✅ Post scheduled with ID: {post_id}")
    print(f"📅 Scheduled for: {schedule_time}")
    print(f"🖼️  Images: {len(args.images)}")
    print(f"📝 Caption: {args.caption[:50]}...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        schedule_post_cli()
    else:
        # Run scheduler loop
        scheduler = PostScheduler()
        asyncio.run(scheduler.run_scheduler())
