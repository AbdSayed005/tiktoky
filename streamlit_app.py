import streamlit as st
import yt_dlp
from PIL import Image
import requests
from io import BytesIO
import os

# 🔹 مجلد التنزيلات
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🔹 استخراج بيانات الفيديوهات من TikTok عبر رابط حساب أو فيديو فردي
def get_tiktok_videos(url):
    options = {
        'quiet': True,
        'extract_flat': True if "tiktok.com/@" in url else False,  # استخراج كل فيديوهات الحساب
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                videos = [
                    {
                        'title': entry['title'],
                        'url': entry['url'],
                        'thumbnail': entry.get('thumbnail', None),
                        'filesize': entry.get('filesize', 0)
                    }
                    for entry in info['entries'] if 'url' in entry
                ]
                return videos
            else:
                return [{
                    'title': info.get('title', 'بدون عنوان'),
                    'url': url,
                    'thumbnail': info.get('thumbnail', None),
                    'filesize': info.get('filesize', 0)
                }]
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
        file_path = f"{DOWNLOAD_FOLDER}/{info['title']}.{info['ext']}"
        return file_path

# 🔹 عرض الصورة المصغرة
def show_thumbnail(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    st.image(img, caption="📸 الصورة المصغرة", use_container_width=True)

# 🎨 تحسين واجهة Streamlit
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
            font-family: 'Arial', sans-serif;
        }
        .stButton>button {
            width: 100%;
            height: 50px;
            font-size: 18px;
            border-radius: 10px;
            background-color: #FF4500;
            color: white;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #FF6347;
        }
        .footer {
            position: fixed;
            bottom: 10px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: gray;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #FF4500;'>🎥 تحميل فيديوهات TikTok</h1>
    <p style='text-align: center; color: gray;'>قم بتحميل فيديوهات TikTok بجودة عالية بسهولة</p>
""", unsafe_allow_html=True)

st.subheader("📌 أدخل رابط حساب TikTok أو فيديو فردي:")

url = st.text_input("🎬 رابط الحساب / الفيديو:")

if url:
    video_list = get_tiktok_videos(url)

    if video_list:
        st.success(f"✅ تم العثور على {len(video_list)} فيديو(هات)")

        total_size = sum(v['filesize'] for v in video_list if v['filesize'])
        st.info(f"📦 **إجمالي حجم الفيديوهات:** {round(total_size / (1024 * 1024), 2) if total_size else 'غير معروف'} MB")

        selected_videos = []
        for i, video in enumerate(video_list):
            with st.expander(f"📌 {video['title']}"):
                col1, col2 = st.columns([1, 3])
                with col1:
                    if video['thumbnail']:
                        show_thumbnail(video['thumbnail'])
                with col2:
                    size_mb = round(video['filesize'] / (1024 * 1024), 2) if video['filesize'] else "غير معروف"
                    st.write(f"📏 **حجم الفيديو:** {size_mb} MB")
                    if st.checkbox(f"🔽 تحميل هذا الفيديو", key=f"vid_{i}"):
                        selected_videos.append(video['url'])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 تحميل الفيديوهات المحددة") and selected_videos:
                with st.spinner("⏳ جاري التحميل..."):
                    for video_url in selected_videos:
                        file_path = download_video(video_url, 'best')
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as file:
                                st.download_button(label=f"📂 تحميل {os.path.basename(file_path)}", data=file, file_name=os.path.basename(file_path), mime="video/mp4")
                    st.success("✅ تم تحميل الفيديوهات بنجاح!")

        with col2:
            if st.button("📥 تحميل كل الفيديوهات دفعة واحدة"):
                with st.spinner("⏳ جاري التحميل..."):
                    for video in video_list:
                        file_path = download_video(video['url'], 'best')
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as file:
                                st.download_button(label=f"📂 تحميل {os.path.basename(file_path)}", data=file, file_name=os.path.basename(file_path), mime="video/mp4")
                    st.success("✅ تم تحميل جميع الفيديوهات بنجاح!")

# 🔹 إضافة توقيع المطور
st.markdown("""
    <div class='footer'>
        🚀 تم التطوير بواسطة <b>خباب</b> ❤️
    </div>
""", unsafe_allow_html=True)
