# Credentials & API Tokens

**Dokumentation erstellt:** 2026-03-15
**Letzte Aktualisierung:** 2026-03-15
**WICHTIG:** Token-Werte sind niemals in diesem File enthalten - nur Referenzen zu sicheren Speicherorten.

---

## 🔐 Token-Übersicht

### GitHub
- **Datei:** `~/.github-credentials`
- **Account:** Sahrapartnerships
- **Email:** sahra.partnerships@gmail.com
- **User:** sahra-partnerships
- **Scopes:** repo, workflow, read:org, gist, write:packages
- **Status:** ✅ Aktiv
- **Login:** `gh auth login --with-token`

### Vercel
- **Datei:** `~/.vercel-credentials`
- **Account:** sahrapartnerships-4831
- **Team:** sahras-projects-d912b90e
- **Team-Slug:** sahras-projects-d912b90e
- **CLI Version:** 50.32.5
- **Status:** ✅ Aktiv
- **Verfügbare Befehle:**
  - `vercel list` - Alle Deployments
  - `vercel deploy` - Projekt deployen
  - `vercel logs [url]` - Logs anzeigen
  - `vercel env` - Umgebungsvariablen
  - `vercel domains` - Domains verwalten
- **Nutzen:** `vercel --token $VERCEL_TOKEN [command]`

### Railway
- **Datei:** `~/.railway-credentials`
- **Tokens:** 2 API tokens konfiguriert
- **Projects:** Noch keine erstellt
- **Status:** ⚠️ Tokens gültig, keine Projekte
- **CLI:** `railway` (v4.31.0)
- **Login erforderlich:** `railway login` (interaktiv)

---

## 🔒 Sicherheitsprotokoll

### Hard Boundaries
- Token-Werte werden **NIEMALS** in Chat oder Memory angezeigt
- Token-Werte werden **NIEMALS** kopiert oder verschoben
- Token-Werte werden **NUR** aus den sicheren Dateien gelesen

### Erlaubte Operationen
- ✅ Bestätigen, dass Token existieren
- ✅ Dateipfade anzeigen
- ✅ Verbindungsstatus prüfen
- ✅ Automation mit Token durchführen (ohne Werte zu loggen)

### Verbotene Operationen
- ❌ Token-Werte anzeigen
- ❌ Token in Chat/Output echon
- ❌ Token an andere Orte kopieren
- ❌ Token in Logs speichern

---

## 📂 Zugehörige Dateien

| Service | Pfad | Typ |
|---------|------|-----|
| GitHub | `~/.github-credentials` | Shell Export |
| Vercel | `~/.vercel-credentials` | Markdown |
| Railway | `~/.railway-credentials` | Config |
| Registry | `~/life/2_Areas/Security/credentials-registry.md` | Übersicht |

---

## 🚀 Verwendung für Deployment

### GitHub
```bash
gh auth login --with-token <<< "$GITHUB_TOKEN"
gh repo create user/repo --public
```

### Vercel
```bash
# Direkt mit Token
vercel --token $VERCEL_TOKEN --yes

# Oder exportiert
export VERCEL_TOKEN=$(cat ~/.vercel-credentials | grep Token)
vercel deploy
```

### Railway
```bash
# Login erforderlich (nicht automatisch)
railway login
railway init --name projekt-name
```

---

*Dieses Dokument enthält KEINE sensiblen Daten - nur Referenzen.*
