# TikTok API Research Report: Uploading Carousels/Posts Programmatically

**Research Date:** March 20, 2026  
**Scope:** TikTok API feasibility for programmatic carousel/post uploads

---

## 1. Official TikTok API Status

### TikTok Content Posting API (Official)

TikTok **does** have an official **Content Posting API** available through their developer platform, but it comes with significant restrictions:

#### What It Supports:
- ✅ **Video uploads** (MP4, MOV, WebM)
- ✅ **Photo carousels** (up to 35 images per post via API)
- ✅ **Direct publishing** or **upload to drafts**
- ✅ Privacy settings, captions (2,200 chars), hashtags
- ✅ Duet/Stitch toggles, branded content disclosures

#### Key Endpoints:
| Endpoint | Purpose |
|----------|---------|
| `POST /v2/post/publish/video/init/` | Initiate video upload |
| `POST /v2/post/publish/content/init/` | Initiate carousel upload |
| `POST /v2/post/publish/inbox/video/init/` | Upload to drafts |
| `GET /v2/post/publish/status/fetch/` | Check upload status |

#### Technical Specs:
- **Video:** Max 4GB, 3 sec - 10 min, 9:16 aspect ratio
- **Photos:** Max 35 images, 20MB each, JPEG/PNG/WebP
- **Format:** 1080x1920 recommended
- **File transfer:** Chunked upload or PULL_FROM_URL

---

## 2. Requirements & Approval Process

### Strict Requirements:
1. **Business/Developer Account Required**
   - Must register at developers.tiktok.com
   - Personal accounts are NOT eligible

2. **App Approval Process**
   - Submit detailed use-case description
   - Provide video walkthrough of your application
   - Submit privacy policy URL
   - **Timeline:** 1-4 weeks (5-10 business days typical)

3. **Required OAuth Scopes**
   - `video.upload` - Initiate uploads
   - `video.publish` - Publish content
   - `user.info.basic` - Account validation

4. **Token Management**
   - Access tokens expire after **24 hours**
   - Refresh tokens valid for **365 days**
   - Must implement token refresh logic

### Limitations:
- ❌ **No native scheduling** - You must implement your own scheduler
- ❌ **No sound/music selection** - Major limitation for TikTok content
- ❌ **No stickers/effects** - API limitation
- ❌ **Content moderation is MORE aggressive via API** than native app
- ❌ **Account-specific daily posting limits** apply (separate from native app)
- ❌ Cannot delete/edit posts via API (Sprinklr limitation noted)

---

## 3. Rate Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| Per-app rate limit | Varies | Aggregate across all accounts |
| Research API | 1,000 requests/day | For data retrieval, not posting |
| Video uploads | Account-specific | Daily limits enforced per creator |
| Status polling | Recommended backoff | Exponential backoff with jitter |

**Key Headers:**
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

**Important:** For 50+ accounts, you need to partition across multiple API apps to avoid hitting aggregate rate ceilings.

---

## 4. Unofficial/Workaround Methods

### Method A: Browser Automation (Playwright/Selenium)
**GitHub:** `wkaisertexas/tiktok-uploader`

**How it works:**
- Uses Playwright to automate browser interactions
- Relies on session cookies (sessionid) for authentication
- Mimics human upload behavior

**Pros:**
- No API approval needed
- Can add sounds/effects/stickers (anything the web app supports)
- Faster to set up initially

**Cons:**
- ❌ **Violates TikTok ToS** - Risk of account bans
- ❌ Brittle - Breaks when TikTok updates UI
- ❌ Requires headless browser infrastructure
- ❌ Robot detection issues (cat-and-mouse game)

**Code Example:**
```python
pip install tiktok-uploader
playwright install

tiktok-uploader -v video.mp4 -d "Caption here" -c cookies.txt
```

### Method B: Third-Party Unified APIs

These services have already gone through TikTok's approval process:

| Service | Price | Carousel Support | API Access |
|---------|-------|------------------|------------|
| **Upload-Post** | $16/mo | ✅ Yes (up to 35 images) | ✅ REST API |
| **Bundle.social** | Variable | ✅ Yes | ✅ Yes |
| **SocialBee** | $29/mo | ✅ Yes (up to 12 images) | ❌ Dashboard only |
| **Buffer** | $6/channel | ✅ Yes | ❌ No direct API |
| **Hootsuite** | $249/mo | ❌ No carousels | Limited |
| **Publer** | Variable | ✅ Yes | ✅ Yes |

**Upload-Post Example:**
```bash
curl -X POST \
  -H "Authorization: Apikey YOUR_KEY" \
  -F "[email protected]" \
  -F "title=My TikTok Carousel" \
  -F "platform[]=tiktok" \
  https://api.upload-post.com/api/upload
```

---

## 5. Best Approach Summary

### For Production/Multiple Accounts:
**RECOMMENDED: Use a Third-Party Unified API like Upload-Post or Bundle.social**

**Why:**
- Skip the 1-4 week approval process
- No rate limit headaches
- No token refresh management
- No maintenance when TikTok changes their API
- Carousel support included
- Cost-effective ($16-29/mo vs $3,200+ dev cost)

**Cost Comparison:**
| Approach | Setup Time | Monthly Cost | Maintenance |
|----------|------------|--------------|-------------|
| Direct TikTok API | 40-50 hours | $0 + dev cost | 5-10 hrs/mo |
| Upload-Post/Bundle | 30 minutes | $16/mo | None |
| Browser automation | 10-20 hours | Server costs | High (fragile) |

### For One-Off Projects (Low Volume):
**Option 1:** Manual scheduling via SocialBee/Buffer dashboard
**Option 2:** Browser automation (accept the risk)

### For Research/Academic:
**TikTok Research API** - Limited to 1,000 requests/day, strict ToS restrictions

---

## 6. Key Findings on Carousels Specifically

### TikTok Carousel Specs:
- **Native app:** 2-35 images
- **SocialBee API:** Up to 12 images
- **Upload-Post API:** Up to 35 images
- **Format:** JPG/PNG, 9:16 aspect ratio, 1080x1920 recommended
- **Max file size:** 20MB per image

### Important Notes:
- Photo carousel posts CANNOT be scheduled natively in TikTok (Video Scheduler only supports videos)
- Third-party tools are REQUIRED for carousel scheduling
- Music must be included in uploaded video files for carousel posts via API

---

## 7. Conclusion & Recommendation

**FEASIBILITY: ✅ YES, but with caveats**

For automating TikTok carousel uploads, the **best approach** is:

1. **Short-term/Testing:** Use Upload-Post ($16/mo) or similar service with existing API access
   - Instant setup
   - Full carousel support
   - No approval delays

2. **Long-term/Scale:** If you need deep customization, apply for TikTok's official Content Posting API
   - Expect 1-4 week approval
   - Budget 40-50 hours development time
   - Plan for ongoing maintenance

3. **Avoid:** Browser automation for production use
   - Too fragile and risky for business use
   - Violates ToS

**Bottom Line:** Unless you have very specific requirements that third-party APIs can't meet, paying $16-29/month for a service like Upload-Post or Bundle.social is significantly more cost-effective than building direct TikTok API integration (which costs $3,200-4,000 in dev time).

---

## Resources

- TikTok Developer Portal: https://developers.tiktok.com
- Upload-Post: https://upload-post.com
- TikTok Content Posting API Docs: https://developers.tiktok.com/doc/content-posting-api
- Playwright uploader: https://github.com/wkaisertexas/tiktok-uploader
