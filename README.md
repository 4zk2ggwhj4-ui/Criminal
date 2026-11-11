# Kriminalfall Ravensbruck – interaktive Cartoon-Krimi-Serie

| Datei | Inhalt |
|---|---|
| `Kriminalfall_Folge_01.mp4` | Folge 1, 1080×1920, 30 FPS |
| `Kriminalfall_Folge_01_Cover.png` | TikTok-Cover «Der Mann, der zweimal existierte» |
| `folge_01_elevenlabs.txt` | Sprechertext Folge 1 |
| `serien_bibel.json` | Kontinuität: Charaktere, Ereignisse, Hinweise, Rätsel, Abstimmungen |
| `audio/` | Sprecher-Audio (ElevenLabs) |
| `produktion/` | Renderer (Python + Pillow + FFmpeg) |

## Neu rendern

```bash
pip install pillow numpy
cd produktion
python3 audio.py ../audio/folge_01_sprecher.mp3 /tmp/mix.wav   # Musik + SFX (synthetisch) + Stimme
python3 render.py /tmp/mix.wav ../Kriminalfall_Folge_01.mp4    # Video, Länge = Audiolänge
python3 cover.py ../Kriminalfall_Folge_01_Cover.png
```

Alle Bilder, Musik und Soundeffekte werden prozedural im Code erzeugt (keine Fremdmedien).
Schriften: Anton, Montserrat, Share Tech Mono – jeweils SIL Open Font License 1.1 (`produktion/fonts/`).
