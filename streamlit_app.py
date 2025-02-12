import streamlit as st
import yt_dlp
import os
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# تكوين الصفحة
st.set_page_config(
    page_title="TikTok Downloader",
    page_icon="🎵",
    layout="wide"
)

# تخصيص CSS
st.markdown("""
<style>
    .video-container {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s;
        border: 1px solid #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
    }
    
    .video-container:hover {
        transform: scale(1.01);
        border-color: #fe2c55;
        box-shadow: 0 4px 12px rgba(254, 44, 85, 0.2);
    }
    
    .video-info {
        flex-grow: 1;
    }
    
    .video-title {
        color: white;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .video-stats {
        color: #a7a7a7;
        font-size: 14px;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #fe2c55;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ff405c;
        transform: translateY(-2px);
    }

    .floating-menu {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
    }

    .floating-menu-content {
        display: none;
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }

    .floating-menu:hover .floating-menu-content {
        display: block;
    }

    .floating-stat {
        color: white;
        padding: 5px 10px;
        margin: 5px 0;
        border-bottom: 1px solid #333;
        font-size: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .download-button {
        background-color: #fe2c55;
        color: white;
        padding: 15px 30px;
        border-radius: 30px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
        text-align: center;
        justify-content: center;
    }

    .download-button:hover {
        transform: translateY(-2px);
        background-color: #ff405c;
    }

    .hidden-button {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

def format_duration(seconds):
    if not seconds:
        return "غير معروف"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"

def format_timestamp(timestamp):
    if not timestamp:
        return "غير معروف"
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except:
        return "غير معروف"

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def get_videos_size(videos, selected_indices):
    total_size = 0
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        for idx in selected_indices:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_info = ydl.extract_info(videos[idx]['url'], download=False)
                if 'filesize' in video_info:
                    total_size += video_info['filesize']
                elif 'filesize_approx' in video_info:
                    total_size += video_info['filesize_approx']
                
        return total_size
    except Exception as e:
        return 0

def get_videos_list(profile_url):
    try:
        profile_url = profile_url.strip()
        profile_url = profile_url.replace('vm.tiktok.com', 'www.tiktok.com')
        profile_url = profile_url.replace('vt.tiktok.com', 'www.tiktok.com')

        if 'tiktok.com' not in profile_url:
            st.error("⚠️ الرجاء إدخال رابط TikTok صحيح")
            return None, None

        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                profile_info = ydl.extract_info(profile_url, download=False)
            except Exception as e:
                st.error(f"⚠️ خطأ في جلب البيانات: {str(e)}")
                return None, None
            
            if 'entries' in profile_info:
                videos = []
                username = profile_url.split('@')[1].split('?')[0].split('/')[0]
                for video in profile_info['entries']:
                    video_info = {
                        'id': video.get('id', ''),
                        'title': video.get('title', 'بدون عنوان'),
                        'duration': video.get('duration', 0),
                        'view_count': video.get('view_count', 0),
                        'timestamp': video.get('timestamp', 0),
                        'url': f"https://www.tiktok.com/@{username}/video/{video['id']}"
                    }
                    videos.append(video_info)
                return videos, username
            else:
                st.error("⚠️ لم يتم العثور على فيديوهات في هذا الحساب")
                return None, None
    except Exception as e:
        st.error(f"⚠️ خطأ غير متوقع: {str(e)}")
        return None, None
def display_video_card(video, index, filtered_videos):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"""
        <div class="video-container" onclick="document.getElementById('checkbox_{index}').click()">
            <div class="video-info">
                <div class="video-title">{video['title']}</div>
                <div class="video-stats">
                    👁️ {video['view_count']:,} مشاهدة • 
                    ⏱️ {format_duration(video['duration'])} • 
                    📅 {format_timestamp(video['timestamp'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        is_selected = st.checkbox("تحديد", key=f"video_{index}")
        if is_selected and index not in st.session_state.selected_videos:
            st.session_state.selected_videos.append(index)
        elif not is_selected and index in st.session_state.selected_videos:
            st.session_state.selected_videos.remove(index)

def download_videos(videos, selected_indices):
    try:
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", "TikTok_Videos")
        os.makedirs(download_path, exist_ok=True)

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'ignoreerrors': True,
        }
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def download_video(idx):
            video = videos[idx]
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video['url']])
                return True, video['title']
            except Exception as e:
                return False, str(e)
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(download_video, idx) for idx in selected_indices]
            for i, future in enumerate(futures):
                success, result = future.result()
                progress = (i + 1) / len(selected_indices)
                progress_bar.progress(progress)
                if success:
                    status_text.success(f"تم تحميل: {result}")
                else:
                    status_text.error(f"فشل التحميل: {result}")
        
        progress_bar.progress(1.0)
        status_text.success('✅ اكتمل التحميل!')
        return True, download_path
    except Exception as e:
        st.error(f"⚠️ حدث خطأ: {str(e)}")
        return False, None

def main():
    if 'selected_videos' not in st.session_state:
        st.session_state.selected_videos = []
    if 'videos_loaded' not in st.session_state:
        st.session_state.videos_loaded = False
    if 'download_clicked' not in st.session_state:
        st.session_state.download_clicked = False
    
    st.title("🎵 TikTok Downloader")
    st.write("أدخل رابط حساب TikTok لتحميل الفيديوهات")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        profile_url = st.text_input(
            "رابط حساب TikTok",
            placeholder="مثال: https://www.tiktok.com/@username"
        )
    with col2:
        fetch_button = st.button("جلب الفيديوهات 📥", use_container_width=True)
    
    if fetch_button and profile_url:
        with st.spinner("جاري جلب الفيديوهات..."):
            videos, username = get_videos_list(profile_url)
            if videos:
                st.session_state.videos = videos
                st.session_state.username = username
                st.session_state.videos_loaded = True
                st.rerun()
    
    if st.session_state.get('videos_loaded', False):
        videos = st.session_state.videos
        username = st.session_state.username
        
        st.subheader(f"📱 حساب: @{username}")
        st.write(f"عدد الفيديوهات: {len(videos)}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input("🔍 بحث في الفيديوهات", key="search")
        with col2:
            sort_by = st.selectbox(
                "ترتيب حسب",
                ['التاريخ (الأحدث)', 'التاريخ (الأقدم)', 'المشاهدات (الأعلى)', 'المدة (الأطول)']
            )
        
        filtered_videos = videos.copy()
        if search_query:
            filtered_videos = [v for v in filtered_videos if search_query.lower() in v['title'].lower()]
        
        if sort_by == 'التاريخ (الأحدث)':
            filtered_videos.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == 'التاريخ (الأقدم)':
            filtered_videos.sort(key=lambda x: x['timestamp'])
        elif sort_by == 'المشاهدات (الأعلى)':
            filtered_videos.sort(key=lambda x: x['view_count'], reverse=True)
        elif sort_by == 'المدة (الأطول)':
            filtered_videos.sort(key=lambda x: x['duration'], reverse=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ اختيار الكل", use_container_width=True):
                st.session_state.selected_videos = list(range(len(filtered_videos)))
                st.rerun()
        with col2:
            if st.button("❌ إلغاء اختيار الكل", use_container_width=True):
                st.session_state.selected_videos = []
                st.rerun()

        # عرض الزر العائم في الأعلى
        if len(st.session_state.selected_videos) > 0:
            selected_count = len(st.session_state.selected_videos)
            total_duration = sum(filtered_videos[i]['duration'] for i in st.session_state.selected_videos)
            total_views = sum(filtered_videos[i]['view_count'] for i in st.session_state.selected_videos)
            total_size = get_videos_size(filtered_videos, st.session_state.selected_videos)

            download_placeholder = st.empty()
            with download_placeholder:
                st.markdown(
                    f"""
                    <div class="floating-menu">
                        <div class="floating-menu-content">
                            <div class="floating-stat">
                                📊 عدد الفيديوهات: {selected_count}
                            </div>
                            <div class="floating-stat">
                                ⏱️ المدة الإجمالية: {format_duration(total_duration)}
                            </div>
                            <div class="floating-stat">
                                👁️ إجمالي المشاهدات: {total_views:,}
                            </div>
                            <div class="floating-stat">
                                💾 الحجم التقريبي: {format_size(total_size)}
                            </div>
                        </div>
                        <div class="download-button" onclick="document.getElementById('start_download').click()">
                            📥 تحميل {selected_count} فيديو
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # زر مخفي لبدء التحميل
            if st.button("تحميل", key="start_download"):
                with st.spinner("جاري التحميل..."):
                    success, download_path = download_videos(
                        filtered_videos,
                        st.session_state.selected_videos
                    )
                    if success:
                        st.balloons()
                        st.success("✅ تم تحميل الفيديوهات بنجاح!")
                        st.info(f"📂 مسار التحميل: {download_path}")
                        if st.button("📂 فتح مجلد التحميل"):
                            if os.name == 'nt':  # Windows
                                os.startfile(download_path)
                            else:  # macOS/Linux
                                os.system(f'xdg-open "{download_path}"')

        # عرض الفيديوهات
        for i, video in enumerate(filtered_videos):
            display_video_card(video, i, filtered_videos)

if __name__ == "__main__":
    main()        
