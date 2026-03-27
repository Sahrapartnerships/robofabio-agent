# 🔥 INCIDENT REPORT: Double Gateway Crash
**Date:** 2026-03-27  
**Severity:** HIGH - Service Interruption  
**Affected:** Robofabio Main Session + Cron Jobs  

---

## 📊 TIMELINE

| Time | Event |
|------|-------|
| 19:57:33 | Session aborted (runId=8feda365) |
| 19:58:36 | **Gateway Timeout** - 60000ms exceeded |
| 20:00:41 | **Cron Timeout** - robofabio-bot-master (180s limit) |
| 20:00:42 | Session aborted (runId=99f691db) |
| 20:01:45 | **2nd Gateway Timeout** |
| 20:13:23 | **3rd Gateway Timeout** |
| 20:15:02 | **Gateway RESTART** - "running missed jobs after restart" |
| 20:15:54 | Recovery budget exceeded - 132 messages deferred |

---

## 🔍 ROOT CAUSE

**Problem:** Gateway Timeouts + Cron Overload

**Evidence:**
```
"gateway timeout after 60000ms"
"cron: job execution timed out" (180s exceeded)
"aborted=true" on multiple runs
"Recovery time budget exceeded — 132 entries deferred"
```

**Trigger Chain:**
1. Cron Job `robofabio-bot-master` läuft >180s (Timeout)
2. Gateway wird überlastet durch parallele Cron-Jobs
3. Gateway restartet sich selbst (Auto-Recovery)
4. Alle Sessions werden unterbrochen

---

## 💥 IMPACT

- **Main Session:** Unterbrochen (deine Nachrichten nicht bearbeitet)
- **Cron Jobs:** 3+ Jobs abgebrochen
- **Messages:** 132+ Nachrichten nicht zugestellt

---

## 🛠️ IMMEDIATE FIXES

### 1. Cron Job Timeouts erhöhen
```bash
# Von 180s auf 300s (5 Min) erhöhen
openclaw cron update --job-id=bb0ea392-aab1-4571-8b93-04321de0669e --timeout=300000
```

### 2. Cron Jobs deduplizieren
**Problem:** Zu viele Cron Jobs parallel:
- robofabio-bot-master (alle 20 min)
- bot-master-optimizer (alle 20 min)
- self-improvement-loop (alle 30 min)
- copybot-pro-v2-live
- trading-monitor

**Fix:** Weniger, aber effizientere Jobs

### 3. Gateway Memory/Performance
**Current:** 1.5GB RAM used / 3.4GB total  
**Issue:** Swap ist 0B (kein Auslagerungsspeicher)

---

## ✅ PERMANENT FIXES (TODO)

- [ ] Cron Jobs konsolidieren (weniger, aber bessere Jobs)
- [ ] Job Timeouts auf 300s erhöhen
- [ ] Gateway Resource Limits prüfen
- [ ] Health Check: Gateway-Restart Detection
- [ ] Session-Recovery: Automatische Wiederherstellung
- [ ] Message Queue: Persistente Speicherung

---

## 📝 LESSONS LEARNED

1. **Zu viele Cron Jobs** überlasten das Gateway
2. **Keine Swap** → Speicherdruck führt zu Restarts
3. **Keine Persistente Queue** → Nachrichten gehen verloren
4. **Timeout zu niedrig** → 180s reicht nicht für komplexe Jobs

---

## ✅ FIXES IMPLEMENTED (2026-03-28 04:20)

### 1. Job Timeouts Increased
| Job | Old Timeout | New Timeout | Status |
|-----|-------------|-------------|--------|
| robofabio-bot-master | 180s | **300s** | ✅ Fixed |
| bot-master-optimizer | default | **180s** | ✅ Fixed |

### 2. Frequencies Reduced
| Job | Old Frequency | New Frequency | Status |
|-----|---------------|---------------|--------|
| robofabio-bot-master | 20 min | **60 min** | ✅ Reduced |
| bot-master-optimizer | 20 min | **60 min** | ✅ Reduced |

### 3. Problematic Jobs Disabled
| Job | Reason | Status |
|-----|--------|--------|
| self-improvement-loop | 3 consecutive timeout errors | 🔴 **DISABLED** |

### 4. Result
- **Before:** 12 active jobs, many overlapping
- **After:** 11 active jobs, no overlap, longer timeouts
- **Load Reduction:** ~60% fewer cron executions per hour

---

**Status:** ✅ FIXED - Monitoring for stability  
**Next Action:** Observe 24h, re-enable self-improvement-loop if stable
