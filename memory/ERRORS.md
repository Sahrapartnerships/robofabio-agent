# 🚨 ERROR LOG - Recurring Issues & Patterns

**Purpose:** Track errors, root causes, and prevention rules.
**Last Updated:** 2026-03-20

---

## ACTIVE ERRORS (Unfixed Patterns)

### ERR-001: Sending Untested Links
**First Occurrence:** 2026-03-20
**Severity:** HIGH
**Frequency:** 2x (same day)

**What Happened:**
- Generated Zrok tunnel URL without testing HTTP status
- User opened link and saw issues
- Had to iterate multiple times to fix
- User feedback: *"hast du den link getsted? wir hatten ausgeacht du testes immer alles vorher bevor du mir es sendest merk dir das bitte"*

**Root Cause:**
- Skipped verification step due to time pressure
- Assumed tunnel would work without validation
- No automatic HTTP check in workflow

**Prevention Rule (AUTO_MODE.md):**
```
Rule: ALWAYS_TEST_LINKS
Before sending ANY external URL:
1. HTTP GET request to verify 200 status
2. Check content loads correctly
3. Verify clickable format
4. No exceptions
```

**Status:** Rule created ✅ - Must verify compliance

---

### ERR-002: Truncated/Partial URLs
**First Occurrence:** 2026-03-20
**Severity:** MEDIUM
**Frequency:** 1x

**What Happened:**
- Sent link in format that wasn't clickable
- User couldn't open it directly
- User feedback: *"mir immer alle links so senden das ich sie öffnen kann"*

**Root Cause:**
- Link formatting issue (possibly line breaks or truncation)
- Didn't verify link was properly formatted as complete URL

**Prevention Rule (AUTO_MODE.md):**
```
Rule: COMPLETE_URLS_ONLY
- ALWAYS send FULL URLs: https://example.com/full/path
- NEVER truncate with "..." or line breaks in middle
- ALWAYS test: Can I click this?
- Format: Plain text, complete protocol + domain + path
```

**Status:** Rule created ✅ - Monitoring compliance

---

## ERROR TREND

```
Errors per day:
- 2026-03-19: 0
- 2026-03-20: 2 (both link-related)

Trend: ↑ New error type emerged
Focus: Link validation and testing
```

---

**Next Review:** 2026-03-21
**Action Required:** Monitor for link-related errors, verify rules are followed
