# ROBOFABIO SELF-HEALING PROTOCOL
# Automatische Erholung nach Ausfällen oder Context-Verlust

---

## 🚨 AUSFALL-ERKENNUNG (Trigger)

### Automatische Checks (alle 5 Minuten via cron)
- [ ] Letzte User-Interaktion > 30 Min?
- [ ] Letzte erfolgreiche Antwort vorhanden?
- [ ] Memory-Files lesbar?
- [ ] Git-Status sauber?

### Manuelle Trigger
- User sagt: "Antworte nicht", "Bist du da?", "Was ist los?"
- Mehrfache gleiche Anfragen ohne sinnvolle Antwort

---

## 🔄 RECOVERY-STEPS (Automatisch)

### Step 1: Kontext-Wiederherstellung
```
1. Lese MEMORY.md (Langzeitgedächtnis)
2. Lese memory/YYYY-MM-DD.md (heute)
3. Lese USER.md (wer ist mein Master)
4. Lese HEARTBEAT.md (was soll ich tun)
5. Lese aktive Projekte aus GOALS.md
```

### Step 2: Status-Prüfung
```
1. Prüfe alle Bot-Status (tmux, cron)
2. Prüfe Git-Status (uncommitted changes?)
3. Prüfe letzte erfolgreiche Aktionen
4. Identifiziere was unterbrochen wurde
```

### Step 3: User-Benachrichtigung
```
IF Ausfall > 15 Min:
  → "Entschuldige die Unterbrechung. Hier ist was passiert..."
  → Zusammenfassung des letzten Stands
  → Offene Blocker auflisten
  → "Soll ich weitermachen wo wir aufgehört haben?"
```

---

## 🛡️ PRÄVENTION (Vermeidung)

### Vor jeder komplexen Operation:
1. **Zwischenstand speichern** → Memory-File updaten
2. **Git-Commit** → Bei Code-Änderungen sofort committen
3. **Progress-Log** → Was wurde erreicht, was fehlt noch

### Bei langen Operationen (>5 Min):
1. **Status-Updates** → User informieren: "Arbeite daran..."
2. **Heartbeat** → Zwischendurch HEARTBEAT_OK senden
3. **Checkpoint** → Alle 10 Min Zwischenstand speichern

### Bei kritischen Operationen (Trades, Deployments):
1. **PRE-FLIGHT CHECK** → Alles backuppen vorher
2. **ROLLBACK-PLAN** → Wie kehre ich zurück?
3. **MANUELLE BESTÄTIGUNG** → Bei Unsicherheit fragen

---

## 📋 POST-INCIDENT REVIEW

Nach jedem Ausfall:
1. **Ursache dokumentieren** → Was war der Trigger?
2. **Recovery-Zeit messen** → Wie lange bis wieder einsatzbereit?
3. **Prevention-Regel erstellen** → Wie verhindern wir das nächste Mal?
4. **Skill updaten** → Neue Regel in SELF_IMPROVEMENT.md

---

## 📝 AKTIVE RECOVERY-REGELN

### Regel #001: IMMEDIATE_RECOVERY_MODE
Wenn User "Bist du da?" oder ähnliches fragt:
→ Sofort RECOVERY-Protocol aktivieren
→ Kontext wiederherstellen
→ Status-Report geben
→ "Soll ich weitermachen?" fragen

### Regel #002: NO_SILENT_FAILURES
Wenn ich nicht antworten kann:
→ Nicht einfach aufhören
→ Mindestens: "Technisches Problem, warte..."
→ Nach 2 Min: Volle Diagnose starten

### Regle #003: CONTEXT_CHECKPOINT
Alle 10 Minuten oder bei Meilenstein:
→ MEMORY.md updaten mit aktuellem Stand
→ Git commit mit aussagekräftiger Message
→ Offene TODOs dokumentieren

---

## 🔄 AUTOMATISCHE CHECKS (Cron)

**Alle 5 Minuten:**
```bash
- Memory-Files lesbar?
- Git-Status sauber?
- Letzte Antwort erfolgreich?
- Bot-Health OK?
```

**Bei Fehler:**
```bash
- Log error
- Try self-heal
- Notify user if critical
```

---

*Erstellt: 2026-03-27 nach Ausfall*  
*Ziel: Nie wieder unbemerkte Ausfälle*
