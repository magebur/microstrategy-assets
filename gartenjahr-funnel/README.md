# Ebook-Funnel „Das Selbstversorger-Gartenjahr"

selbstversorgen.com · MVP: Lead-Magnet → Ebook (14 €) + Order Bump (7 €) → Danke-Seite mit Affiliate-Empfehlungen.

## Inhalt

```
website/                     Statische Seiten (HTML/CSS, keine externen Fonts/Skripte)
  kalender.html              Opt-in-Seite Lead-Magnet „Aussaatkalender 2027“
  bestaetigen.html           Nach dem Eintragen: „Bitte E-Mail bestätigen“ (Double-Opt-in)
  ebook.html                 Verkaufsseite Ebook (14 €, Hinweis auf Order Bump)
  danke.html                 Danke-Seite nach Kauf (Digistore24-Weiterleitung) + Affiliate
  assets/style.css, cover.svg, cover.png (Social-Media-Vorschau)
material/
  aussaatkalender-2027.html  Quelle Lead-Magnet (2 Seiten A4 quer)
  planer-paket.html          Quelle Order Bump (6 Seiten A4: Deckblatt, Beetplan, Fruchtfolge,
                             Anbauplan, Erntetagebuch, Jahresauswertung)
  email-sequenz.md           Double-Opt-in-Mail + 6 Mails (sofort, Tag 1/3/5/7/10)
  ebook-gliederung.md        Seitenbudget, Kapitelvorlage, Musterkapitel „Januar“
  produkttexte.md            Texte für Digistore24 und Opt-in-Boxen
pdf/
  aussaatkalender-2027.pdf   fertig zum Versand
  planer-paket.pdf           fertig als Bump-Produkt
```

PDFs neu erzeugen (nach Änderungen an den HTML-Quellen): HTML in Chrome öffnen → Drucken → „Als PDF speichern“, **Hintergrundgrafiken an**, Ränder „Standard“.

## Vor dem Livegang ersetzen

Gelb markierte Stellen (`class="ph"`) und folgende Platzhalter:

| Platzhalter | Datei | Was |
|---|---|---|
| `BREVO-FORMULAR-URL-EINTRAGEN` | kalender.html | Brevo-Formular einbetten (Double-Opt-in an, Weiterleitung → bestaetigen.html) |
| `PRODUKT-ID` (2×) | ebook.html | Digistore24-Bestelllink |
| `FLAECHENRECHNER-URL` | bestaetigen.html | Link zum Flächen-Tool |
| `AFFILIATE-LINK-*`, `[Produktname]`, `[Anbieter]` | danke.html | nur selbst genutzte Produkte |
| `KONTAKT@selbstversorgen.com` | danke.html | echte Kontaktadresse |
| `[PLATZHALTER – eigene Geschichte]`, Autorenfoto | ebook.html | echter Text, echtes Foto |
| `Kálmán [Nachname, Qualifikation]` | ebook.html | Name + Qualifikation des Fachprüfers |
| `30 Tage` Garantie | ebook.html | muss mit der Einstellung in Digistore24 übereinstimmen |
| `[…]` in den Mails | email-sequenz.md | Name, Höhe, Flächenzahlen, Fotos |

## Technische Einrichtung

**Brevo**
1. Listen: `Kalender 2027`, `Warteliste Ebook`, `Newsletter`, `Käufer Gartenjahr`.
2. Attribute: `FIRSTNAME`, `KAEUFER_EBOOK` (Boolean).
3. Formular mit Double-Opt-in; Bestätigungsseite = `bestaetigen.html`.
4. Automation laut `email-sequenz.md` (bis zum Launch nur Mail 0–3).
5. Opt-in-Boxen auf Artikeln und Tool-Ergebnisseiten (Texte in `produkttexte.md`).

**Digistore24**
1. Produkt 1: Ebook, 14 € brutto, Typ „E-Book/Download“.
2. Produkt 2: Planer-Paket, 7 €, als **Order Bump** im Bestellformular von Produkt 1.
3. Danke-Seite (Weiterleitung nach Kauf) = `danke.html`.
4. Garantiezeitraum einstellen = Wert auf der Verkaufsseite.
5. IPN/Integration → Brevo: Käufer bekommen `KAEUFER_EBOOK = true` und landen in `Käufer Gartenjahr`.
6. **Testkauf** mit und ohne Bump (Dezember), inkl. Rückerstattung.

**Hosting:** Die Seiten sind statisch – als Unterseiten von selbstversorgen.com hochladen (z. B. `/kalender/`, `/gartenjahr/`, `/danke-gartenjahr/`). Impressum/Datenschutz verlinken auf die bestehenden Seiten der Hauptdomain. Datenschutzerklärung um Brevo und Digistore24 ergänzen.

## Rechtliches (kurz, keine Rechtsberatung)

- Double-Opt-in ist Pflicht; die Einwilligung im Formular nennt Newsletter **und** Angebote.
- Affiliate-Links sind als Werbung gekennzeichnet (`rel="sponsored"`, Sternchen-Hinweis).
- Keine erfundenen Bewertungen: Leserstimmen erst nach dem Launch und nur mit Einverständnis.
- Keine Google Fonts o. Ä. eingebunden – nur Systemschriften.

## Zeitplan (aus dem Briefing)

- [ ] **Oktober:** Brevo einrichten, Kalender-PDF prüfen lassen und veröffentlichen, Opt-in-Formulare auf Artikel und Tool-Ergebnisse
- [ ] **Oktober:** Fotoarchiv sichten (Autorenfoto, Mail Tag 5, Ebook-Bilder)
- [ ] **November:** Ebook schreiben (Vorlage: `ebook-gliederung.md`), fachliche Prüfung durch Kálmán – Aussaatkalender gleich mitprüfen
- [ ] **Dezember:** Digistore-Produkte + Bump, Verkaufsseite live (noindex bis Launch), Mails 4+5 fertig, Testkauf
- [ ] **Anfang Januar:** Launch-Kampagne an die Warteliste, danach Mails 4+5 in die Automation

## Offene Punkte

- **Fachliche Prüfung:** Die Termine im Aussaatkalender und die Höhenlagen-Faustregel (3–4 Tage pro 100 m) sind Richtwerte und müssen von Kálmán geprüft werden.
- **Flächen-/Ertragszahlen** in Mail 2 sind bewusst offen gelassen – mit Ebook Kapitel 1 abgleichen.
- **Upsell „Vorräte & Konservieren“** (27 €) erst nach echten Käuferzahlen (Phase 2).
