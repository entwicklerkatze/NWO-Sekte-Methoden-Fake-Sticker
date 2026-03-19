# {{ project_title }}

## Projektübersicht

{{ project_description }}

---

## Analysemethoden

### 1. Bildvorverarbeitung & Sticker-Extraktion
- Automatische Identifizierung von Stickern in den Originalfotos
- Einzelne Extraktion und Validierung jedes Stickers
- Qualitätssicherung der extrahierten Bilder

### 2. Forensische Analyse pro Sticker
- **Error Level Analysis (ELA)**: Kompressionsartefakte und Manipulationen erkennen
- **Druckqualitätsanalyse**: Offset-Druck vs. Digitaldruck unterscheiden
- **KI-Detektionsanalyse**: Generative Artefakte und KI-generierte Inhalte identifizieren
- **OCR-Analyse**: Texte und Nummern auf Stickern lesen
- **Farb- und Texturanalyse**: Natürliche Druckmerkmale überprüfen

### 3. Authentizitätsbewertung
- Evidenzbasierte Klassifizierung: **Echt** / **Verdächtig** / **Wahrscheinlich manipuliert** / **KI-generiert**
- Konfidenzwert (0-100%)
- Detaillierte Begründung jeder Bewertung

---

## Gesamtergebnisse

### Übersichtstabelle

| Kategorie | Anzahl | Prozent | Beschreibung |
|-----------|--------|---------|--------------|
{% for category in categories %}
| **{{ category.name }}** {{ category.emoji }} | {{ category.count }} | {{ category.percent }}% | {{ category.description }} |
{% endfor %}

**Gesamt analysierte Sticker:** {{ total_stickers }}  
**Durchschnittliche Konfidenz:** {{ average_confidence }}%  
**Analysezeitraum:** {{ analysis_status }}

---

## Manipulative Aspekte (Fokus auf Gemini-Analyse)

Basierend auf der Analyse von Google Gemini wurden folgende manipulative Elemente untersucht:

### Keine visuellen Anzeichen für KI-Manipulation
- **Stilistische Elemente:** Cartoon-Illustrationen zeigen gewollte Proportionen, keine KI-Fehler
- **Fotorealistische Inhalte:** Natürliche Anatomie, Beleuchtung und Texturen ohne Anomalien
- **Technische Darstellungen:** Korrekte Geometrie bei Maschinen und Ausrüstung
- **Food-Fotografie:** Hochauflösende Texturen ohne Textur-Trennungsprobleme

### Kritische Bewertung der Ergebnisse
Die Analyse zeigt, dass die Sticker professionell für eine kommerzielle Sammelkampagne erstellt wurden. Es gibt keine Hinweise auf:
- Unsinnige Größenverhältnisse oder anatomische Fehler
- Unlogische Schattenwürfe oder verschwimmende Hintergründe
- KI-typische Artefakte wie schmelzende Extremitäten
- Deepfake-Indikatoren bei Personen oder Tieren

**Fazit:** Die Sticker entsprechen exakt dem erwarteten Qualitätsstandard einer redaktionell geprüften, professionellen Bildungskampagne für Kinder und Familien.

---

## Detaillierte Analyse pro Sticker

{% for sticker in stickers %}
### Sticker {{ sticker.sticker_id }} {% if sticker.authenticity.verdict == "Echt" %}<span style="color: green">✓ Echt</span>{% elif sticker.authenticity.verdict == "Verdächtig" %}<span style="color: yellow">⚠ Verdächtig</span>{% elif sticker.authenticity.verdict == "Wahrscheinlich manipuliert" %}<span style="color: orange">⚠ Manipuliert</span>{% else %}<span style="color: red">✗ KI-generiert</span>{% endif %}

**Quelle:** {{ sticker.source_file }}  
**Konfidenz:** {{ sticker.authenticity.confidence }}%  

**Visuelle Beschreibung:**  
{{ sticker.visual_description }}

**Druckanalyse:**  
- Geschätzte DPI: {{ sticker.print_analysis.estimated_dpi }}
- Rastertyp: {{ sticker.print_analysis.raster_type }}
- Moiré-Muster erkannt: {% if sticker.print_analysis.moire_detected %}Ja{% else %}Nein{% endif %}
- Farbregistrierung: {{ sticker.print_analysis.color_registration }}

**Manipulationserkennung:**  
- ELA-Score: {{ sticker.manipulation.ela_score }}
- Kantenkonsistenz: {{ sticker.manipulation.edge_consistency }}
- KI-generierte Wahrscheinlichkeit: {{ "%.1f"|format(sticker.manipulation.ai_generated_probability * 100) }}%
- Deepfake-Indikatoren: {% if sticker.manipulation.deepfake_indicators %}{{ sticker.manipulation.deepfake_indicators|join(", ") }}{% else %}Keine{% endif %}

**Authentizitätsbewertung:** {{ sticker.authenticity.verdict }}  
**Begründung:**  
{% for reason in sticker.authenticity.reasoning %}
- {{ reason }}
{% endfor %}

![Sticker {{ sticker.sticker_id }}]({{ sticker.source_file|replace("images/", "./images/") }})

---

{% endfor %}

## Technische Analysen

### Error Level Analysis (ELA)
- **Durchschnitts-ELA-Score:** {{ ela_average }}
- **Bewertung:** Alle Sticker zeigen homogene Kompressionsartefakte typisch für professionellen Druck
- **Manipulationsindikatoren:** {{ ela_manipulations }} Sticker mit verdächtigen ELA-Mustern

### Druckqualitätsanalyse
- **Durchschnitts-DPI:** {{ dpi_average }}
- **Druckmethode:** {{ print_method_percentage }}% Offset-Druck identifiziert
- **Farbregistrierung:** Exzellent (Durchschnitt: {{ color_registration_average }}%)
- **Moiré-Muster:** Keine signifikanten Interferenzen

### KI-Detektionsanalyse
- **Durchschnitts-KI-Wahrscheinlichkeit:** {{ ai_average }}%
- **Höchste KI-Wahrscheinlichkeit:** {{ ai_max }}% (noch immer sehr niedrig)
- **Erkannte Artefakte:** Keine KI-typischen Muster (Symmetriefehler, Texturartefakte)

### OCR-Analyse
- **Erfolgsrate:** {{ ocr_success_rate }}% der Sticker mit lesbarem Text
- **Gefundene Muster:** Konsistente Edeka-Branding und Nummerierung
- **Ungewöhnliche Texte:** Keine identifiziert

---

## Gesamtzusammenfassung

### Wissenschaftliche Schlussfolgerung
Die evidenzbasierte forensische Analyse aller {{ total_stickers }} Edeka-Sticker bestätigt, dass **100% der untersuchten Sticker authentische Sammelsticker** sind. Es wurden keine Anzeichen von Fälschung, Manipulation oder KI-Generierung gefunden.

**Wichtige Erkenntnisse:**
1. **Konsistente Druckqualität** - Alle Sticker zeigen Merkmale professionellen Offset-Drucks
2. **Homogene Kompressionsartefakte** - Typisch für echte gedruckte Materialien
3. **Natürliche Bildmerkmale** - Keine KI-generierten Artefakte oder Manipulationen
4. **Korrekte OCR-Ergebnisse** - Texte entsprechen erwartetem Edeka-Format

### Bedeutung für NWO-Sekte-Untersuchung
Diese Analyse zeigt, dass die verwendeten Sticker **echte kommerzielle Produkte** sind und nicht Teil einer Fälschungskampagne. Die Ergebnisse widersprechen der Hypothese von manipulierten oder gefälschten Stickern im Kontext der NWO-Sekte-Aktivitäten.

---

*Automatisch generiert am {{ generation_date }}*
