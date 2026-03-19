# Feature Requests

Format: [FEAT-YYYYMMDD-XXX] capability_name

## Einträge

### [FEAT-20260318-001] TikTok Upload Automation

**Logged**: 2026-03-18T05:30:00Z  
**Priority**: high  
**Status**: pending  
**Area**: backend

### Requested Capability
TikTok Karussells automatisch als Drafts hochladen (nicht manuell posten).

### User Context
- 20 Karussells geplant
- Manuelles Hochladen ist zeitaufwändig
- Besser: API-Upload als Draft, User macht finalen Post

### Complexity Estimate
medium

### Suggested Implementation
1. TikTok Developer Account erstellen
2. TikTok API Auth (OAuth)
3. `tiktok_uploader.py` Modul
4. Bilder + Caption + Hashtags → Draft Upload

### Metadata
- Frequency: recurring
- Related Features: carousel_generator.py

---

### [FEAT-20260318-002] Later/Planungstool Integration

**Logged**: 2026-03-18T06:00:00Z  
**Priority**: medium  
**Status**: pending  
**Area**: backend

### Requested Capability
Planungstool mit Tracking-Daten für TikTok.

### User Context
- Tracking ist kritisch (Klicks, Conversions)
- TikTok API gibt keine Link-Click Daten
- Lösung: Later ($18/Monat) für Scheduling + eigenes Dashboard für Conversion-Tracking

### Suggested Implementation
- Later Account einrichten
- Link-in-Bio Tool mit Tracking
- Unser Dashboard für Funnel: Impression → Click → Cart → Purchase

### Metadata
- Frequency: first_time
- Related Features: streamlit_dashboard.py

---

### [FEAT-20260316-001] Stripe Payment Integration

**Logged**: 2026-03-16T10:00:00Z  
**Priority**: high  
**Status**: pending  
**Area**: backend

### Requested Capability
Zahlungsabwicklung für Elternratgeber (19€ Produkt).

### User Context
- Produkt ist fertig (PDF, Landing Page)
- Fehlt: Zahlungsanbindung
- Ziel: Stripe oder PayPal

### Suggested Implementation
1. Stripe Account
2. Checkout Page
3. Webhook für Conversion-Tracking
4. Digital Delivery (PDF nach Zahlung)

### Metadata
- Frequency: first_time
- Related Features: conversion_tracker.py

---
