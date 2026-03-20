#!/bin/bash
# link-checker.sh - Automatischer Link Tester
# Usage: ./link-checker.sh https://example.com

URL="$1"

if [ -z "$URL" ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ OK - $URL (HTTP $HTTP_CODE)"
    exit 0
else
    echo "❌ FAIL - $URL (HTTP $HTTP_CODE)"
    exit 1
fi
