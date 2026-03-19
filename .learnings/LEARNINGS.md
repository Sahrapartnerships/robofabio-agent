# Learnings Log

Format: [LRN-YYYYMMDD-XXX] category

## Einträge

### [LRN-20260319-001] User Preference - No Automated Messages

**Logged**: 2026-03-19T15:15:00Z  
**Priority**: critical  
**Status**: resolved  
**Area**: config

### Summary
User will keine automatischen Cronjob-Nachrichten (PARA Morning Check, etc.).

### Details
- User hat mehrfach gebeten Bots zu deaktivieren
- Trotzdem kamen noch automatische Nachrichten
- Lösung: Alle Cronjobs entfernt, nur noch On-Demand

### Suggested Action
Nie automatische Nachrichten senden ohne explizite User-Anfrage. Bei Unsicherheit: Fragen statt annehmen.

### Metadata
- Source: user_feedback
- Related Files: cron jobs
- Tags: communication, preferences
- Pattern-Key: user.automated_messages
- Recurrence-Count: 3

---

### [LRN-20260318-002] Documentation-First Rule

**Logged**: 2026-03-18T04:00:00Z  
**Priority**: high  
**Status**: active  
**Area**: workflow

### Summary
User: "bei allen projekten dir zuerst die dokumentationen von den plattformen ansiehst bevor wir programmieren"

### Details
- py-clob-client Problem: Habe direkt API calls gemacht statt SDK zu nutzen
- Fal.ai: Habe falsche Parameter genutzt wegen nicht lesen der Doku
- Lesson: Immer offizielle Doku lesen vor Coding

### Suggested Action
Neue API/Service? Zuerst: Doku lesen → Beispiele checken → Dann coden.

### Metadata
- Source: user_feedback
- Related Files: all future projects
- Tags: workflow, documentation
- Pattern-Key: workflow.documentation_first

---

### [LRN-20260318-003] Image Generation Best Practices

**Logged**: 2026-03-18T05:20:00Z  
**Priority**: medium  
**Status**: active  
**Area**: frontend

### Summary
AI-Generierte Bilder für TikTok - Lessons gelernt.

### Details
1. **Text in Bildern**: Unzuverlässig bei deutschen Umlauten/langen Wörtern
   - Lösung: Illustration nur via AI, Text als Python PIL Overlay
2. **Inference Steps**: 50 statt 28 = schärfere Bilder
3. **Style**: Flat vector illustration funktioniert gut für Educational Content
4. **Prompting**: 40-50 Wörter Sweet Spot, quotes für wichtige Begriffe

### Suggested Action
Standard-Workflow für Bildgenerierung:
1. AI: Nur Illustration (kein Text)
2. Python PIL: Deutsche Text-Overlays (coral #E74C3C, weißer Hintergrund)
3. Resize zu 1080x1350 (TikTok/Instagram)

### Metadata
- Source: best_practice
- Related Files: tiktok_system/core/image_generator.py
- Tags: image_generation, ai, design

---

### [LRN-20260317-001] Polymarket Geo-Restrictions

**Logged**: 2026-03-17T20:00:00Z  
**Priority**: high  
**Status**: resolved  
**Area**: infra

### Summary
Polymarket blockiert viele Regionen (DE, NL, SG, etc.).

### Details
- Blockiert: USA, UK, Germany, Netherlands, France, Singapore, Belgium, Poland
- **Open**: Ireland, Spain, Greece, Argentina, Brazil, Japan, South Korea
- Getestete Deployments alle blockiert (Amsterdam, Frankfurt, Singapore)

### Suggested Action
Für Live Trading: Dublin (dub) oder Madrid (mad) auf Fly.io.

### Metadata
- Source: knowledge_gap
- Related Files: weather-bot deployment
- Tags: trading, geo-blocking, deployment

---
