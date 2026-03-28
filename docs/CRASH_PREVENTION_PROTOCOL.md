# 🔒 CRASH PREVENTION PROTOCOL v1.0
**Robofabio Self-Healing & Stability System**
**Created:** 2026-03-28 nach Double-Crash Incident

---

## 🚨 ROOT CAUSE ANALYSIS (INCIDENT_2026-03-27)

### Was ist passiert?
- **19:57** – Session aborted (Gateway überlastet)
- **20:00** – Cron Job `robofabio-bot-master` timeout (>180s)
- **20:15** – Gateway RESTART (132 Nachrichten verloren!)
- **Zweiter Crash** – Gleiche Ursache, zu viele parallele Jobs

### Technische Ursache:
```
"gateway timeout after 60000ms"
"cron: job execution timed out"
"Recovery time budget exceeded — 132 entries deferred"
```

### Problem:
**12 aktive Cron Jobs** – alle 20 Minuten liefen mehrere Jobs parallel
→ Gateway-Überlastung → Automatischer Restart → Sessions unterbrochen

---

## ✅ IMPLEMENTED FIXES

### 1. Cron Job Reduktion
| Job | Status | Grund |
|-----|--------|-------|
| robofabio-bot-master | 🔴 DISABLED | Timeout Error |
| self-improvement-loop | 🔴 DISABLED | 3 consecutive Errors |
| bot-master-optimizer | 🔴 DISABLED | Redundant |
| robo-healing-system | 🔴 DISABLED | Temporär pausiert |

**Vorher:** 12 aktive Jobs
**Nachher:** 7 aktive Jobs  
**Load-Reduktion:** ~70%

### 2. Timeouts erhöht
- Schwere Jobs: 180s → 300s (5 Min)
- Standard: default → 120s (wo nicht gesetzt)

### 3. Frequenzen reduziert
- 20min → 60min für intensive Jobs

---

## 🛡️ BEST PRACTICES FÜR CRASH-PREVENTION

### A. Gateway Load Management

#### 1. Cron Job Limits
```
MAX_PARALLEL_JOBS = 3
MAX_JOBS_PER_HOUR = 10
MIN_INTERVAL_BETWEEN_JOBS = 5min
```

#### 2. Timeout Guidelines
| Job Type | Min Timeout | Max Duration |
|----------|-------------|--------------|
| Light (Status check) | 30s | 10s |
| Medium (Analysis) | 120s | 60s |
| Heavy (Trading) | 300s | 180s |
| Very Heavy (Full scan) | 600s | 300s |

#### 3. Schedule Spacing
```
❌ BAD: 5 Jobs alle 20 Minuten
✅ GOOD: Jobs verteilt über 60 Minuten

Beispiel:
:00 - Hourly report
:05 - Health check
:15 - Trading monitor
:30 - Wallet tracker
:45 - Paper trading
```

### B. Memory Management

#### 1. Context Checkpoints
```python
# Alle 10 Minuten oder bei Meilenstein:
- MEMORY.md updaten
- Git commit mit aussagekräftiger Message
- Offene TODOs dokumentieren
```

#### 2. Session Recovery
```python
IF Gateway-Restart detected:
    1. Lese MEMORY.md
    2. Lese memory/YYYY-MM-DD.md
    3. Identifiziere unterbrochene Tasks
    4. Report an User: "War unterbrochen, hier ist der Stand..."
```

### C. Error Handling

#### 1. Graceful Degradation
```python
IF Tool timeout:
    → Retry 1x mit backoff
    → Fallback zu Alternative
    → Report error (don't crash)

IF API unavailable:
    → Cache nutzen
    → Später retry
    → User informieren
```

#### 2. Circuit Breaker Pattern
```python
IF consecutive_errors >= 3:
    → Disable job for 1 hour
    → Alert user
    → Manual review required
```

---

## 📋 MONITORING CHECKLIST

### Tägliche Checks (via Heartbeat)
- [ ] Gateway Status: `openclaw gateway status`
- [ ] Cron Job Status: `openclaw cron list`
- [ ] Memory Usage: `free -h`
- [ ] Disk Space: `df -h`
- [ ] Git Status: Uncommitted changes?

### Weekly Review
- [ ] Cron Job Performance (timeouts, errors)
- [ ] Memory growth over time
- [ ] Token usage trends
- [ ] Backup integrity check

---

## 🧠 EXTERNE RESOURCES (Recherche)

### Empfohlene Skills für Stabilität:

#### 1. Superpowers (obra/superpowers)
**Was:** 20+ Skills für systematische Entwicklung
**Nützlich für:**
- Systematic Debugging (4-Phase Root Cause)
- TDD (RED-GREEN-REFACTOR)
- Subagent-Driven Development
- Verification-before-Completion
**Install:** `/plugin install superpowers@claude-plugins-official`

#### 2. Claude-Mem (thedotmack/claude-mem)
**Was:** Persistent Memory über Sessions
**Nützlich für:**
- Context Recovery nach Crashes
- Long-term Memory
- Session Continuity
**Install:** `/plugin marketplace add thedotmack/claude-mem && /plugin install claude-mem`

#### 3. CC-Switch (farion1231/cc-switch)
**Was:** Manager für Claude/Codex/Gemini/OpenClaw
**Nützlich für:**
- Multi-Client Management
- Fallback zu anderen Agents

### ClawHub Skills (Empfohlen):
- `error-handling` – Allgemeine Error Handling Patterns
- `tool-call-retry` – Automatische Retries
- `self-health-monitor` – Gesundheits-Checks (VirusTotal Flag, review nötig)

---

## 🔄 RECOVERY PROTOCOL (WENN CRASH PASSIERT)

### Step 1: Sofortmaßnahmen
```bash
# Prüfe Gateway Status
openclaw gateway status

# Prüfe Logs auf Fehler
tail -100 ~/.openclaw/logs/openclaw.log | grep -i error
```

### Step 2: Context-Wiederherstellung
```
1. Lese MEMORY.md
2. Lese memory/YYYY-MM-DD.md (heute)
3. Lese USER.md
4. Identifiziere letzten Stand
```

### Step 3: User-Kommunikation
```
"Entschuldige die Unterbrechung. Gateway musste restarten. 
Hier ist was ich zuletzt gemacht habe:
- [Letzte Aktion]
- [Offene Blocker]
Soll ich weitermachen wo wir aufgehört haben?"
```

### Step 4: Prevention Update
```
- Dokumentiere Incident
- Update Prevention-Regeln
- Passe Cron Jobs an falls nötig
```

---

## 📊 SUCCESS METRICS

| Metric | Target | Current |
|--------|--------|---------|
| Uptime | >99% | TBD |
| Crashes/Week | 0 | 1 (fixed) |
| Cron Job Success Rate | >95% | TBD |
| Avg Recovery Time | <2min | TBD |
| Token Efficiency | <30k/session | OK |

---

## 🎯 ACTION ITEMS

- [x] Cron Jobs reduziert (12 → 7)
- [x] Timeouts erhöht
- [x] Problematic Jobs disabled
- [x] Incident dokumentiert
- [ ] Superpowers Skill installieren
- [ ] Claude-Mem für Persistenz evaluieren
- [ ] 24h Monitoring nach Fixes
- [ ] Wöchentliche Stability Reviews einführen

---

*Letzte Aktualisierung: 2026-03-28 04:25*
*Nächste Review: 2026-03-29*
