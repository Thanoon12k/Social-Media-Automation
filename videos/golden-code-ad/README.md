# Golden Code — إعلان موشن جرافيك

فيديو إعلاني عمودي (1080×1920، 40 ثانية، 30fps) بستايل ذهبي/أسود لصفحة **Golden Code**.

- `golden-code-ad.mp4` — الفيديو النهائي الجاهز للنشر (ريلز / تيك توك / ستوري / إعلان).
- `index.html` — كل المشاهد والحركات (النصوص تتعدل من هنا، واليوزر من `CFG.handle`).
- `music.py` — يولّد الموسيقى والمؤثرات الصوتية متزامنة مع المشاهد (`music.wav`).
- `render.mjs` — يصدّر الفيديو فريم-فريم عبر Chromium + ffmpeg.

## إعادة التصدير بعد التعديل
```bash
pip install numpy imageio-ffmpeg
python3 music.py
FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") node render.mjs golden-code-ad.mp4
# معاينة لقطات معينة: node render.mjs --preview 1,10,20,35
```
