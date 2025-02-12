import streamlit as st
import yt_dlp
from PIL import Image
import requests
from io import BytesIO
import os
import zipfile

# 🔹 إعداد مجلد التنزيلات
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🔹 استخراج بيانات الفيديو من TikTok
def get_tiktok_video_info(video_url):
    options = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',  # جلب أفضل جودة
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            return {
                'title': info.get('title', 'بدون عنوان'),
                'thumbnail': info.get('thumbnail', None),
                'formats': [
                    {
                        'format_id': f['format_id'],
                        'resolution': f.get('resolution', 'غير معروف'),
                        'filesize': f.get('filesize', 0),
                        'ext': f.get('ext', 'mp4')
                    }
                    for f in info.get('formats', []) if f.get('filesize')
                ]
            }
        except Exception as e:
            st.error(f"❌ خطأ أثناء استخراج بيانات الفيديو: {e}")
            return None

# 🔹 تحميل الفيديو باستخدام yt-dlp
def download_video(video_url, format_id):
    options = {
        'format': format_id,
        'outtmpl': f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(video_url, download=True)
        return f"{DOWNLOAD_FOLDER}/{info['title']}.{info['ext']}"

# 🔹 ضغط جميع الفيديوهات في ملف ZIP
def create_zip():
    zip_path = f"{DOWNLOAD_FOLDER}/videos.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, file)
            zipf.write(file_path, arcname=file)
    return zip_path

# 🔹 عرض الصورة المصغرة للفيديو
def show_thumbnail(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    st.image(img, caption="📸 الصورة المصغرة", use_column_width=True)

# 🎨 واجهة Streamlit
st.title("🎥 تحميل فيديوهات TikTok")
st.subheader("📌 أدخل رابط فيديو TikTok:")
video_url = st.text_input("🎬 رابط الفيديو:")

if video_url:
    video_info = get_tiktok_video_info(video_url)
    if video_info:
        st.success(f"✅ تم جلب بيانات الفيديو: {video_info['title']}")
        if video_info['thumbnail']:
            show_thumbnail(video_info['thumbnail'])
        st.subheader("🔽 اختر الجودة للتحميل:")
        format_options = {
            f["format_id"]: f"{f['resolution']} - {round(f['filesize'] / (1024 * 1024), 2)} MB ({f['ext']})"
            for f in video_info['formats']
        }
        format_id = st.selectbox("📌 اختر الجودة:", list(format_options.keys()), format_func=lambda x: format_options[x])
        
        if st.button("📥 تحميل الفيديو"):
            with st.spinner("⏳ جاري التحميل..."):
                file_path = download_video(video_url, format_id)
                if os.path.exists(file_path):
                    st.success("✅ تم تحميل الفيديو!")
                    with open(file_path, "rb") as file:
                        st.download_button("📂 تحميل الفيديو", data=file, file_name=os.path.basename(file_path), mime="video/mp4")
                else:
                    st.error("❌ فشل التحميل!")

        # 🔹 إضافة خيار تحميل كل الفيديوهات كملف ZIP
        if st.button("📥 تحميل جميع الفيديوهات كملف ZIP"):
            with st.spinner("⏳ جاري التحميل..."):
                zip_path = create_zip()
                with open(zip_path, "rb") as zip_file:
                    st.download_button("📂 تحميل جميع الفيديوهات", data=zip_file, file_name="TikTok_Videos.zip", mime="application/zip")
        
        # 🔹 إضافة رابط مباشر لتحميل الفيديو في حال لم يعمل زر التحميل
        st.markdown(f"📎 **رابط تحميل خارجي:** [اضغط هنا لتحميل الفيديو]({video_url})")
