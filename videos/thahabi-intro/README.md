# ذهبي 🤖 — فيديو تعريف الوكيل الذكي

فيديو عمودي (1080×1920، ~40 ثانية) يعرّف بشخصية **ذهبي**، الوكيل الذكي اللي يدير صفحة الكود الذهبي، ويعلن تحدي الـ 1000 متابع.

- `thahabi-intro.mp4` — الفيديو النهائي (صوت عراقي + حركة فم متزامنة + ترجمة + موسيقى).
- `design.html` / `design-A.png` / `design-B.png` — ورقة تصميم الشخصية بالستايلين (المعتمد: A).
- `robot.js` — رسم الشخصية (التعابير: normal / talk / happy / cool / sad، وحركة الإيد والرمش والفم).
- `vo.py` — نص التعليق (`BEATS`) وتوليد الصوت وتوقيت كل كلمة وبيانات حركة الفم → `timing.js`.
- `music.py` — موسيقى ومؤثرات متزامنة ويا الكلمات، ويدمج الصوت فوقها.
- `index.html` — المشاهد والحركة. `render.mjs` — التصدير.

## إعادة التصدير
```bash
pip install numpy imageio-ffmpeg edge-tts
python3 vo.py        # بعد تعديل النص امسح مجلد vo/
python3 music.py
FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") node render.mjs thahabi-intro.mp4
```
