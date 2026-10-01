# E-Mail-Sequenz nach Opt-in (Brevo)

6 Mails in 10 Tagen. Platzhalter in Brevo-Syntax: `{{ contact.FIRSTNAME | default : "Hallo" }}`.
Alles in `[eckigen Klammern]` vor dem Einsatz ersetzen.

## Wichtig: Timing bis zum Launch

Wer sich im Oktober–Dezember einträgt, würde an Tag 7 ein Ebook angeboten bekommen, das es noch nicht gibt. Darum:

| Zeitraum | Automation |
|---|---|
| **Bis Launch (Okt–Dez)** | Nur Mail 0–3 laufen automatisch. Danach Kontakt in Liste „Warteliste Ebook“. |
| **Launch (Anfang Januar)** | Mail 4 + 5 als **Kampagne** an die Warteliste (z. B. Di 05.01. und Fr 08.01.2027). |
| **Ab Launch** | Mail 4 + 5 in die Automation hängen → volle 10-Tage-Sequenz für alle Neuen. |

Käufer (Digistore24-IPN bzw. Zapier/Make → Brevo-Attribut `KAEUFER_EBOOK = true`) werden aus Mail 4/5 ausgeschlossen.

---

## Mail 00 – Double-Opt-in (Brevo-Bestätigungsmail)

**Betreff:** Bitte bestätigen: Dein Aussaatkalender 2027
**Vorschautext:** Ein Klick – dann ist der Kalender da.

> Hallo {{ contact.FIRSTNAME | default : "" }},
>
> schön, dass du dabei bist! Bitte bestätige kurz deine E-Mail-Adresse – danach schicke ich dir sofort den Aussaatkalender 2027.
>
> **[Button: Ja, Anmeldung bestätigen]**
>
> Du hast dich nicht angemeldet? Dann ignoriere diese Mail einfach.
>
> [Dein Name] von selbstversorgen.com

---

## Mail 0 – Sofort: Kalender-Download + Vorstellung

**Betreff:** Hier ist dein Aussaatkalender 2027 🌱
**Vorschautext:** Plus: der wichtigste Tipp, bevor du ihn aufhängst.

> {{ contact.FIRSTNAME | default : "Hallo" }},
>
> hier ist er – dein Aussaatkalender 2027:
>
> **[Button: Kalender herunterladen (PDF)]**
>
> Druck ihn aus und häng ihn dorthin, wo du ihn siehst. Bei mir hängt er an der Innenseite der Schuppentür.
>
> **Bevor du loslegst, ein Tipp:** Schau dir Seite 2 an. Die Termine auf Seite 1 gelten für mittlere Lagen. Liegt dein Garten höher oder in einer Frostsenke, verschiebst du sie – die Tabelle dort zeigt dir, um wie viel. Ich gärtnere selbst [im Allgäu auf ca. ___ m] und weiß, wie frustrierend es ist, wenn im April die Bücher „jetzt säen!“ rufen und draußen noch Schnee liegt.
>
> **Kurz zu mir:** Ich bin [Name] und betreibe selbstversorgen.com. [1–2 Sätze: seit wann du gärtnerst, wie groß der Garten ist, welcher Anteil des Gemüses selbst angebaut wird.] Mein Ziel: dass mehr Familien einen echten Teil ihres Essens selbst anbauen – nicht als Hobby nebenbei, sondern mit Plan.
>
> In den nächsten Tagen bekommst du ein paar Mails von mir mit dem, was ich gern vor meinem ersten Selbstversorger-Jahr gewusst hätte. Morgen geht’s um den Fehler, den fast alle im ersten Jahr machen.
>
> Bis morgen
> [Name]
>
> PS: Antworte gern auf diese Mail und erzähl mir, wo dein Garten liegt und wie groß er ist. Ich lese jede Antwort.

---

## Mail 1 – Tag 1: Der häufigste Anfängerfehler

**Betreff:** Der Fehler, den ich im ersten Jahr gemacht habe
**Vorschautext:** Er kostet dich nicht die Ernte – sondern die Lust.

> {{ contact.FIRSTNAME | default : "Hallo" }},
>
> im ersten Jahr wollte ich alles auf einmal: zwölf Beete, 25 Gemüsearten, Hochbeet, Frühbeet, Kräuterspirale. Im Mai sah es großartig aus.
>
> Im Juli war ich durch. Jeden Abend zwei Stunden gießen, die Schnecken waren schneller als ich, und die Hälfte der Beete war zugewuchert. [An eigene Erfahrung anpassen.]
>
> **Der häufigste Fehler ist nicht, zu wenig zu wissen. Es ist, zu viel auf einmal anzufangen.**
>
> Was besser funktioniert:
>
> 1. **Klein starten, aber richtig.** Lieber 30 m², die du im Griff hast, als 150 m², die dich im Juli überrollen.
> 2. **Wenige Kulturen, dafür in ordentlicher Menge.** Fünf bis acht Gemüsearten, die deine Familie wirklich isst – nicht 25, von denen du je drei Pflanzen hast.
> 3. **Pflegeleichtes zuerst.** Kartoffeln, Zwiebeln, Bohnen, Mangold, Zucchini, Kürbis verzeihen viel. Sellerie, Blumenkohl und Auberginen können warten.
> 4. **Jedes Jahr erweitern.** Wer im zweiten Jahr 50 % mehr Fläche bewirtschaftet, bleibt dabei. Wer im ersten Jahr alles will, hört oft im zweiten auf.
>
> **Deine Aufgabe für heute (5 Minuten):** Schreib auf einen Zettel die fünf Gemüsesorten, die bei euch am meisten gegessen werden. Mit denen fängst du an.
>
> Übermorgen rechnen wir aus, wie viel Fläche du dafür wirklich brauchst.
>
> [Name]

---

## Mail 2 – Tag 3: Wie viel Fläche du wirklich brauchst

**Betreff:** Wie viel m² braucht eine Familie?
**Vorschautext:** Die ehrliche Antwort – und ein Rechner, der sie für dich ausrechnet.

> {{ contact.FIRSTNAME | default : "Hallo" }},
>
> „Wie viel Fläche brauche ich, um meine Familie zu versorgen?“ – das ist die Frage, die ich am häufigsten bekomme. Die ehrliche Antwort: **Es kommt darauf an, was „versorgen“ heißt.**
>
> - **Frisches Sommergemüse** (Salat, Zucchini, Tomaten, Bohnen, Kräuter): Dafür reichen oft schon [___ m²] pro Person.
> - **Ein guter Teil des Jahresbedarfs an Gemüse** inklusive Lagergemüse: eher [___ m²] pro Person.
> - **Mit Kartoffeln** steigt der Bedarf deutlich – die brauchen viel Platz.
>
> *[Zahlen vor Versand mit Kálmán abstimmen und mit dem Ebook, Teil 1, Kapitel 1 abgleichen.]*
>
> Viel wichtiger als die Gesamtfläche ist aber die Rechnung **pro Gemüse**: Wie viel esst ihr davon pro Woche – und wie viel erntest du realistisch pro m²? Genau das rechnet der Flächenrechner auf selbstversorgen.com für dich aus:
>
> **[Button: Zum Flächenrechner]**
>
> **Deine Aufgabe:** Nimm die fünf Sorten von vorgestern und gib sie in den Rechner ein. Dann weißt du, ob dein Garten reicht – oder wo du Schwerpunkte setzen musst.
>
> In ein paar Tagen zeige ich dir, wie das bei uns im Garten aussieht.
>
> [Name]

---

## Mail 3 – Tag 5: Eigene Geschichte + Fotos

**Betreff:** So sieht es bei uns aus (mit Fotos)
**Vorschautext:** Ein Blick in meinen Garten – auch in die Ecken, die nicht so schön sind.

> *Diese Mail lebt von echten Fotos und einer echten Geschichte. Gerüst zum Füllen:*
>
> {{ contact.FIRSTNAME | default : "Hallo" }},
>
> heute mal kein Tipp, sondern ein Blick über den Zaun.
>
> **[Foto 1: Garten im Überblick – idealerweise Sommer]**
> Das ist unser Garten. [Größe, Lage, Höhe, seit wann.]
>
> **[Foto 2: Ein Misserfolg]**
> [Was ist schiefgegangen? Z. B. Spätfrost, Kohlhernie, Schneckenjahr. Was hast du daraus gelernt?] – Ehrliche Fehler schaffen mehr Vertrauen als perfekte Beete.
>
> **[Foto 3: Vorratsregal / Keller / Einmachgläser]**
> Und dafür machen wir das alles: [Was habt ihr eingelagert? Wie lange reicht es?]
>
> **Was sich verändert hat:** [2–3 Sätze: Wie sich Essen, Einkaufen, Familie verändert haben, seit ihr selbst anbaut.]
>
> Das Wichtigste, was ich gelernt habe: **Ein guter Plan im Januar spart im Juli die Hälfte der Arbeit.** Darum habe ich alles, was ich weiß, in eine Reihenfolge gebracht – Monat für Monat. Mehr dazu in zwei Tagen.
>
> [Name]

---

## Mail 4 – Tag 7: Ebook-Angebot

**Betreff:** Dein ganzes Gartenjahr – Monat für Monat
**Vorschautext:** Das Ebook ist da. Für 14 €.

> {{ contact.FIRSTNAME | default : "Hallo" }},
>
> der Aussaatkalender sagt dir, **wann** du säst. Aber die Fragen, die mir am häufigsten gestellt werden, sind andere:
>
> - Wie viel muss ich anbauen, damit es für die Familie reicht?
> - Welches Beet belege ich wann womit?
> - Was mache ich mit 20 kg Tomaten im August?
> - Was muss im März passieren, damit ich im Dezember noch Gemüse habe?
>
> Darauf antwortet mein Ebook **„Das Selbstversorger-Gartenjahr“**:
>
> ✔ **Teil 1 – Der Plan vor der Saat:** Flächenbedarf, Standort und Höhenlage, Fruchtfolge, Mischkultur, Boden, Saatgut
> ✔ **Teil 2 – Januar bis Dezember:** jedes Monatskapitel mit Aussaat, Pflege, Ernte, Haltbarmachen, typischen Fehlern und einer Checkliste
> ✔ **Teil 3 – Zum Nachschlagen:** Aussaattabelle für über 40 Gemüsearten, Mischkulturtabelle, Schädlinge, Beispielplan für 30 m²
>
> Ca. 90 Seiten, fachlich geprüft von [Kálmán …], als PDF sofort zum Download.
>
> **Preis: 14 €.**
>
> **[Button: Ebook ansehen]** → Link zur Verkaufsseite (mit UTM: `?utm_source=brevo&utm_medium=email&utm_campaign=launch&utm_content=mail4`)
>
> Im Bestellformular kannst du für 7 € das **Planer-Paket** dazunehmen: Beetplan, Anbauplan und Erntetagebuch zum Ausdrucken.
>
> Und falls es dir nicht hilft: [30 Tage] Geld zurück, ohne Begründung.
>
> [Name]
>
> PS: Wenn du gerade jetzt im Januar planst, ist das genau der richtige Moment. Kapitel „Januar“ ist das erste im Gartenjahr-Teil – du kannst heute damit anfangen.

---

## Mail 5 – Tag 10: Erinnerung + konkreter Nutzen

**Betreff:** Was im Februar schon auf die Fensterbank muss
**Vorschautext:** Und warum der Januar der wichtigste Gartenmonat ist.

> {{ contact.FIRSTNAME | default : "Hallo" }},
>
> kurze Erinnerung, weil die Zeit drängt: **Paprika, Chili und Knollensellerie** werden schon im Februar vorgezogen. Wer im Januar keinen Plan hat, sät sie zu spät oder gar nicht – und erntet im September grüne Paprika.
>
> Im Ebook „Das Selbstversorger-Gartenjahr“ findest du für genau diese Wochen:
>
> - die **Januar-Checkliste**: Bedarf berechnen, Beetplan zeichnen, Saatgut sichten und bestellen, Anzucht vorbereiten
> - die **Februar-Checkliste**: was wann auf die Fensterbank kommt – und was noch warten muss
> - den **Beispielplan für 30 m²**, falls du im ersten Jahr bist und nicht bei null anfangen willst
>
> **[Button: Ebook für 14 € holen]**
>
> Ein Kaffee und ein Stück Kuchen – dafür hast du einen Plan für das ganze Jahr.
>
> Danach lasse ich dich mit Angeboten in Ruhe – es geht weiter mit Tipps zum Gartenjahr.
>
> [Name]
>
> PS: Fragen zum Ebook? Antworte einfach auf diese Mail.

---

## Nach der Sequenz

- Kontakt in die Liste **„Newsletter“** verschieben (z. B. 2× im Monat: „Was jetzt im Garten dran ist“ – passt zu den Monatskapiteln).
- Käufer in eine eigene Liste **„Käufer Gartenjahr“** → später Zielgruppe für den Upsell „Vorräte & Konservieren“ (Phase 2).
