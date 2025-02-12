import streamlit as st

# إعداد الصفحة
st.set_page_config(page_title="منصة الأدوات", page_icon="🚀", layout="wide")

# تنسيق CSS لتصميم أجمل
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 36px;
            color: #FF4500;
        }
        .sub-title {
            text-align: center;
            font-size: 20px;
            color: gray;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }
        .stButton>button {
            width: 250px;
            height: 60px;
            font-size: 18px;
            border-radius: 12px;
            background-color: #FF4500;
            color: white;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover {
            background-color: #FF6347;
        }
    </style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown("<h1 class='main-title'>🎯 منصة الأدوات المتعددة</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>🚀 اختر أداة للبدء</p>", unsafe_allow_html=True)

# زر الانتقال إلى بوت TikTok
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 تحميل فيديوهات TikTok"):
        st.switch_page("pages/tiktok_downloader.py")  # الانتقال لصفحة البوت
with col2:
    if st.button("📊 أداة أخرى قيد التطوير"):
        st.switch_page("pages/another_tool.py")  # الانتقال لأداة أخرى

# إضافة توقيع
st.markdown("<p style='text-align: center; color: gray;'>🛠 تم التطوير بواسطة خباب</p>", unsafe_allow_html=True)
