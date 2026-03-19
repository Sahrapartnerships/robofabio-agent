# Errors Log

Format: [ERR-YYYYMMDD-XXX] skill_or_command_name

## Einträge

### [ERR-20260318-001] Trading Bot Deactivation

**Logged**: 2026-03-18T15:20:00Z  
**Priority**: high  
**Status**: resolved  
**Area**: infra

### Summary
Trading Bots wurden nicht vollständig gestoppt - liefen als Systemd Services, nicht nur als tmux/Prozesse.

### Error
User meldete: "es kommen immer noch bot startet nachrichten" trotz tmux-Kill.

### Context
- Dachte Bot läuft nur in tmux
- Tatsächlich: Systemd Services (`polymarket-api.service`, `polymarket-bot.service`) waren aktiv
- Services starteten Bots automatisch neu

### Fix
```bash
systemctl stop polymarket-api.service polymarket-bot.service
systemctl disable polymarket-api.service polymarket-bot.service
rm -f /etc/systemd/system/polymarket-*.service
systemctl daemon-reload
```

### Metadata
- Reproducible: no
- Related Files: /etc/systemd/system/polymarket-*.service
- Lesson: Bei "Bot ausschalten" immer prüfen: tmux, screen, systemd, cronjobs

---

### [ERR-20260318-002] Fal.ai API Parameter

**Logged**: 2026-03-18T05:00:00Z  
**Priority**: medium  
**Status**: resolved  
**Area**: backend

### Summary
Fal.ai API call failed wegen falschem `image_size` Parameter.

### Error
```
HTTP 422: image_size sollte 'portrait_4_3' sein, nicht '3:4'
```

### Fix
Korrekte Werte: 'square_hd', 'square', 'portrait_4_3', 'portrait_16_9', 'landscape_4_3', 'landscape_16_9'

### Metadata
- Reproducible: yes
- Related Files: image_generator.py
- Lesson: Immer API-Doku checken vor dem Coden

---

### [ERR-20260318-003] AI Bild Prompt-Adhärenz

**Logged**: 2026-03-18T05:15:00Z  
**Priority**: medium  
**Status**: resolved  
**Area**: frontend

### Summary
AI generierte Bild trotzdem mit Handy, obwohl Prompt "NO phones visible anywhere" enthielt.

### Error
Slide 2 zeigte Mutter mit Handy beim Frühstück, obwohl Tipp "Kein Handy vor dem Frühstück" war.

### Fix
Prompt präzisiert: "mother showing a calendar or planner to the child" statt nur "no phones"

### Metadata
- Reproducible: yes
- Related Files: tiktok carousel generation
- Lesson: Bei AI-Generierung negative Constraints oft nicht ausreichend - positive Beschreibung besser

---
