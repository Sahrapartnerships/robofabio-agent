# 🧪 TEST BEFORE SEND SYSTEM
**Erstellt:** 2026-03-20  
**Regel:** Nichts wird geschickt ohne vorherige Verifikation.

---

## ✅ UNIVERSAL CHECKLIST

### Für LINKS
- [ ] HTTP Status Code prüfen (sollte 200 sein)
- [ ] Seite lädt tatsächlich (nicht nur Server antwortet)
- [ ] Wichtige Elemente vorhanden (Forms, Buttons, etc.)

### Für CODE / SCRIPTS
- [ ] Lokal getestet?
- [ ] Keine Syntaxfehler?
- [ ] Erwartetes Output?
- [ ] Fehlerbehandlung vorhanden?

### Für DATEIEN / KONFIGURATIONEN
- [ ] Datei existiert?
- [ ] Inhalt ist korrekt?
- [ ] Format gültig? (JSON, YAML, etc.)
- [ ] Pfade sind korrekt?

### Für BEFEHLE / KOMMANDOS
- [ ] Befehl ausprobiert?
- [ ] Erwartetes Ergebnis?
- [ ] Keine gefährlichen Operationen (rm, dd, etc.)?

### Für INFORMATIONEN / RECHERCHE
- [ ] Quelle verifiziert?
- [ ] Daten aktuell?
- [ ] Mehrere Quellen gecheckt (bei wichtigen Dingen)?

---

## 🔧 AUTOMATISIERTE TESTS

### Link Checker (automatisch)
```bash
# Vor jedem Link-Share
curl -s -o /dev/null -w "%{http_code}" URL
# Muss 200 zurückgeben
```

### Code Syntax Check
```bash
# Python
python3 -m py_compile script.py

# JSON
python3 -c "import json; json.load(open('file.json'))"

# YAML
python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"
```

### File Exists Check
```bash
# Vor jedem Datei-Path
test -f /path/to/file && echo "EXISTS" || echo "MISSING"
```

---

## 🚨 ESCALATION

**Wenn Test FAILT:**
1. Nicht senden
2. Problem fixen
3. Erneut testen
4. Erst dann senden

**Wenn ich nicht testen kann:**
- Explizit sagen: "Das habe ich nicht testen können weil..."
- Nicht als fertig/verifiziert markieren

---

## 📝 LOGGING

**Jede Sendung dokumentieren:**
- Was wurde geschickt?
- Was wurde getestet?
- War das Ergebnis?
- Timestamp

**Ziel:** Nachvollziehbarkeit und Vertrauen wiederaufbauen.

---

## 💬 ANTWORT TEMPLATE

**Vor dem Senden immer fragen:**
> "Habe ich das getestet?"
> 
> Wenn ja → Senden  
> Wenn nein → Testen oder nicht senden

**Nach dem Test:**
> "✅ Getestet: [Was] - Ergebnis: [OK/Fail]"

---

*System aktiviert ab: Sofort*  
*Violation Consequence: Keine Sendung, bis getestet*
