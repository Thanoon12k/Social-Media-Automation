# Golden Code — إعلان موشن جرافيك

فيديو إعلاني عمودي (1080×1920، 40 ثانية، 30fps) بستايل ذهبي/أسود لصفحة **Golden Code**.

- `golden-code-ad-60s-voice.mp4` — نسخة دقيقة كاملة ويا تعليق صوتي عراقي + ترجمة على الشاشة.
- `golden-code-ad.mp4` — النسخة القصيرة (40 ثانية، موسيقى بس).
- `index.html` — كل المشاهد والحركات (النصوص تتعدل من هنا، واليوزر من `CFG.handle`).
- `music.py` — يولّد الموسيقى والمؤثرات الصوتية متزامنة مع المشاهد (`music.wav`).
- `vo.py` — نص التعليق العراقي (`SCRIPT`)، يولّد الصوت (edge-tts، صوت `ar-IQ-BasselNeural`، وتگدر تبدله بـ `VOICE=ar-IQ-RanaNeural`) ويمط المشاهد حتى تطابق الكلام (`timing.js`).
- `render.mjs` — يصدّر الفيديو فريم-فريم عبر Chromium + ffmpeg.

## إعادة التصدير بعد التعديل
```bash
pip install numpy imageio-ffmpeg
pip install edge-tts
python3 vo.py      # بعد تعديل النص امسح مجلد vo/ حتى ينعاد توليد الصوت
python3 music.py
FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") node render.mjs golden-code-ad-60s-voice.mp4
# معاينة لقطات معينة: node render.mjs --preview 1,10,20,35
```
