# TikTok Poster Bot

Automated TikTok carousel posting bot built with Python and Playwright. Supports headless mode, session persistence, 2FA handling, and scheduled posts.

## Features

- ✅ **Login Automation** - Manual login with session persistence
- ✅ **2FA Support** - Handles two-factor authentication
- ✅ **Carousel Posts** - Upload multiple images (up to 35)
- ✅ **Headless Mode** - Run without visible browser
- ✅ **Error Handling** - Robust retry logic
- ✅ **Session Management** - Save and reuse login sessions
- ✅ **Scheduled Posts** - Schedule posts for future dates
- ✅ **Customizable Settings** - Comments, duets, stitches, visibility
- ✅ **CLI Interface** - Easy command-line usage

## Installation

### Prerequisites

- Python 3.8+
- Playwright browsers

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Create environment file (optional):**
```bash
cp .env.example .env
# Edit .env with your settings
```

## Quick Start

### 1. First Login

The first time you run the bot, you'll need to manually log in:

```bash
python cli.py login
```

Or use the test script which handles login automatically:

```bash
python test_post.py --create-test-images --caption "Hello TikTok!"
```

### 2. Post a Carousel

**Using the CLI:**
```bash
# Post immediately
python cli.py post --images photo1.jpg photo2.jpg photo3.jpg \
    --caption "My carousel post!" \
    --hashtags "trending,viral,photography"

# Schedule for later
python cli.py post --images photo1.jpg photo2.jpg \
    --caption "Scheduled post!" \
    --schedule-minutes 60
```

**Using the test script:**
```bash
# Create test images and post
python test_post.py --create-test-images --image-count 5 \
    --caption "My first carousel!" \
    --hashtags "viral,trending,photography"

# Post with your own images
python test_post.py --images photo1.jpg photo2.jpg photo3.jpg \
    --caption "Check out these photos!"
```

### 3. Manage Scheduled Posts

```bash
# List all scheduled posts
python cli.py schedule --list

# Run the scheduler (processes pending posts)
python cli.py schedule --run

# Cancel a scheduled post
python cli.py schedule --cancel 123
```

### 4. Use in Your Code

```python
import asyncio
from tiktok_poster import TikTokPoster

async def main():
    async with TikTokPoster() as poster:
        # Login (uses saved session if available)
        await poster.auth.login()
        
        # Post carousel
        result = await poster.post_carousel(
            image_paths=["image1.jpg", "image2.jpg"],
            caption="My carousel post! 🎉",
            hashtags=["trending", "viral"],
            allow_comments=True,
            who_can_view="public"
        )
        
        if result["success"]:
            print(f"Posted! URL: {result.get('post_url')}")
        else:
            print(f"Failed: {result['error']}")

asyncio.run(main())
```

## CLI Commands

### Login
```bash
python cli.py login              # Login and save session
python cli.py login --force      # Force re-login
```

### Post
```bash
python cli.py post --images img1.jpg img2.jpg img3.jpg \
    --caption "My post!" \
    --hashtags "tag1,tag2,tag3" \
    --visibility public \
    --retries 3

# Schedule post
python cli.py post --images *.jpg \
    --caption "Later!" \
    --schedule-minutes 120
```

### Schedule Management
```bash
python cli.py schedule --list              # List all posts
python cli.py schedule --run               # Run scheduler daemon
python cli.py schedule --cancel 123        # Cancel post ID 123
python cli.py schedule --delete 123        # Delete post ID 123
```

### Logout
```bash
python cli.py logout
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TIKTOK_HEADLESS` | `true` | Run browser in headless mode |
| `TIKTOK_BROWSER` | `chromium` | Browser type (chromium, firefox, webkit) |
| `TIKTOK_TIMEOUT` | `30000` | Default timeout in ms |
| `TIKTOK_MAX_RETRIES` | `3` | Maximum retry attempts |
| `TIKTOK_DELAY_MIN` | `2` | Minimum delay between actions (sec) |
| `TIKTOK_DELAY_MAX` | `5` | Maximum delay between actions (sec) |
| `TIKTOK_LOG_LEVEL` | `INFO` | Logging level |
| `TIKTOK_SCREENSHOTS` | `true` | Save debug screenshots |
| `TIKTOK_DEBUG` | `false` | Enable debug mode |

### Using .env File

Create a `.env` file in the project root:

```env
# Browser Settings
TIKTOK_HEADLESS=false
TIKTOK_BROWSER=chromium
TIKTOK_DEBUG=true

# Timeouts
TIKTOK_TIMEOUT=30000
TIKTOK_UPLOAD_TIMEOUT=300000

# Retry Settings
TIKTOK_MAX_RETRIES=3
TIKTOK_RETRY_DELAY=5

# Logging
TIKTOK_LOG_LEVEL=INFO
TIKTOK_SCREENSHOTS=true
```

## File Structure

```
tiktok_poster/
├── config.py          # Configuration settings
├── auth.py            # Authentication & session management
├── tiktok_poster.py   # Main posting functionality
├── scheduler.py       # Post scheduling (optional)
├── cli.py             # Command-line interface
├── test_post.py       # Test script with CLI
├── README.md          # This file
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
├── .gitignore         # Git ignore rules
└── data/              # Created automatically
    ├── sessions/      # Saved browser sessions
    ├── logs/          # Log files
    └── screenshots/   # Debug screenshots
```

## Usage Examples

### Basic Carousel Post

```bash
python cli.py post \
    --images photo1.jpg photo2.jpg photo3.jpg \
    --caption "My vacation photos!" \
    --hashtags "travel,vacation,summer"
```

### Private Post

```bash
python cli.py post \
    --images *.jpg \
    --caption "Work in progress" \
    --visibility private
```

### Scheduled Post (30 minutes later)

```bash
python cli.py post \
    --images photo1.jpg photo2.jpg \
    --caption "Scheduled post!" \
    --schedule-minutes 30
```

### With Retry Logic

```bash
python cli.py post \
    --images photo1.jpg \
    --caption "Important post" \
    --retries 5
```

### Force Re-login

```bash
python cli.py post \
    --images photo1.jpg \
    --caption "Hello again" \
    --force-login
```

### Schedule a Post with Python

```python
from datetime import datetime, timedelta
from scheduler import PostScheduler, ScheduledPost

scheduler = PostScheduler()

post = ScheduledPost(
    image_paths=["image1.jpg", "image2.jpg"],
    caption="Scheduled from Python!",
    hashtags=["automation", "python"],
    schedule_time=datetime.now() + timedelta(hours=2),
    who_can_view="public",
)

post_id = scheduler.schedule_post(post)
print(f"Scheduled post ID: {post_id}")
```

### Run Scheduler Daemon

```python
from scheduler import PostScheduler
import asyncio

async def main():
    scheduler = PostScheduler()
    await scheduler.run_scheduler(check_interval=60)  # Check every minute

asyncio.run(main())
```

## Session Management

Sessions are automatically saved after successful login and reused for subsequent runs.

### Session Storage
- Location: `data/sessions/tiktok_storage_state.json`
- Expiry: 7 days (configurable via `TIKTOK_SESSION_EXPIRY`)

### Clear Session

To force a new login, either:
1. Use `--force-login` flag
2. Delete the session file: `rm data/sessions/tiktok_storage_state.json`
3. Use `python cli.py login --force`
4. Use `auth.logout()` in code

## API Reference

### TikTokAuth

```python
auth = TikTokAuth()

# Start browser
await auth.start()

# Login (uses saved session or manual login)
success = await auth.login()

# Check if logged in
is_logged_in = await auth.check_logged_in()

# Save session manually
await auth.save_session()

# Logout
await auth.logout()

# Close browser
await auth.close()
```

### TikTokPoster

```python
poster = TikTokPoster(auth)

# Post carousel
result = await poster.post_carousel(
    image_paths=["img1.jpg", "img2.jpg"],
    caption="My post",
    hashtags=["tag1", "tag2"],
    allow_comments=True,
    allow_duet=True,
    allow_stitch=True,
    who_can_view="public",  # public, friends, private
    schedule_time=None,  # datetime object or None
)

# Post with retry
result = await poster.post_with_retry(
    image_paths=["img1.jpg"],
    caption="My post",
    max_retries=3,
)
```

### PostScheduler

```python
from scheduler import PostScheduler, ScheduledPost
from datetime import datetime, timedelta

scheduler = PostScheduler()

# Schedule a post
post = ScheduledPost(
    image_paths=["img1.jpg"],
    caption="Hello!",
    schedule_time=datetime.now() + timedelta(hours=1),
)
post_id = scheduler.schedule_post(post)

# Get pending posts
pending = scheduler.get_pending_posts()

# Update status
scheduler.update_post_status(post_id, "posted", post_url="https://...")

# Cancel post
scheduler.cancel_post(post_id)

# Run scheduler (posts automatically)
await scheduler.run_scheduler(check_interval=60)
```

## Troubleshooting

### Login Issues

**Problem:** Bot can't log in automatically

**Solution:** TikTok requires manual login. The bot will open a browser window for you to log in manually on first run. After that, the session is saved.

### Upload Timeout

**Problem:** "Upload timed out" error

**Solution:** 
- Increase timeout: `TIKTOK_UPLOAD_TIMEOUT=600000`
- Check your internet connection
- Disable headless mode to see what's happening: `TIKTOK_HEADLESS=false`

### Element Not Found

**Problem:** Selectors not finding elements

**Solution:**
- TikTok's UI changes frequently
- Enable debug mode: `TIKTOK_DEBUG=true`
- Check screenshots in `data/screenshots/` to see current state

### Session Expired

**Problem:** "Session expired" message

**Solution:**
- Delete session file: `rm data/sessions/tiktok_storage_state.json`
- Or use `--force-login` flag

### Playwright Not Installed

**Problem:** `playwright` module not found

**Solution:**
```bash
pip install playwright
playwright install chromium
```

## Tips

1. **First Run**: Always run with `TIKTOK_HEADLESS=false` first to see the browser and complete any verification challenges

2. **Rate Limiting**: Use realistic delays between actions. The default delays (2-5 seconds) are usually safe.

3. **Test Mode**: Use `--create-test-images` to quickly test without preparing real images

4. **Screenshots**: Keep `TIKTOK_SCREENSHOTS=true` enabled to debug issues

5. **Multiple Accounts**: Session files are per-username when using `auth.login(username="account_name")`

## Limitations

- TikTok's anti-automation measures may require periodic manual verification
- 2FA requires manual intervention
- Scheduling requires TikTok Creator Center access
- Some features may vary based on account type (personal vs creator vs business)

## License

MIT License - Use at your own risk. Respect TikTok's Terms of Service.

## Disclaimer

This tool is for educational purposes. Using automation on TikTok may violate their Terms of Service. Use responsibly and at your own risk.
