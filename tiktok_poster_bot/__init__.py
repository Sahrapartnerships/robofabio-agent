"""TikTok Poster Bot - Automated TikTok carousel posting."""

from .config import (
    TIKTOK_URL,
    TIKTOK_LOGIN_URL,
    TIKTOK_UPLOAD_URL,
    HEADLESS,
    MAX_IMAGES_PER_CAROUSEL,
    MAX_CAPTION_LENGTH,
)
from .auth import TikTokAuth
from .tiktok_poster import TikTokPoster

__version__ = "1.0.0"
__all__ = [
    "TikTokAuth",
    "TikTokPoster",
    "TIKTOK_URL",
    "TIKTOK_LOGIN_URL",
    "TIKTOK_UPLOAD_URL",
    "HEADLESS",
    "MAX_IMAGES_PER_CAROUSEL",
    "MAX_CAPTION_LENGTH",
]
