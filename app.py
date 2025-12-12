import streamlit as st
import os
import time
import base64

# Thiết lập trang Streamlit
st.set_page_config(
    page_title="Audio Player with Text Sync",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .track-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
        transition: all 0.3s;
        cursor: pointer;
    }
    .track-card:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .active-track {
        border-left: 5px solid #2196F3;
        background-color: #e3f2fd !important;
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
    }
    .audio-controls {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .text-display {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
        font-size: 16px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'Courier New', monospace;
        border: 2px solid #2196F3;
    }
    .control-button {
        margin: 5px;
    }
    .status-bar {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        border-left: 5px solid #4CAF50;
    }
    .slider-container {
        margin: 15px 0;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 8px;
    }
    .slider-value {
        font-weight: bold;
        color: #2196F3;
        font-size: 1.1em;
    }
    .track-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 20px;
    }
    .track-item {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .track-item:hover {
        background-color: #f0f0f0;
        transform: translateY(-2px);
    }
    .track-item.active {
        background-color: #2196F3;
        color: white;
        border-color: #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# Danh sách các file theo thứ tự mới trong hình
TRACKS = [
    {"audio": "QT 03.mp3", "text": "QT 03.txt"},
    {"audio": "QT 09.mp3", "text": "QT 09.txt"},
    {"audio": "QT 13.mp3", "text": "QT 13.txt"},
    {"audio": "QT 15.mp3", "text": "QT 15.txt"},
    {"audio": "QT 23.mp3", "text": "QT 23.txt"},
    {"audio": "QT 30.mp3", "text": "QT 30.txt"},
    {"audio": "QT 66.mp3", "text": "QT 66.txt"},
    {"audio": "QT 67.mp3", "text": "QT 67.txt"},
    {"audio": "QT 68.mp3", "text": "QT 68.txt"},
    {"audio": "QT 69.mp3", "text": "QT 69.txt"}
]

# Khởi tạo session state
if 'current_track' not in st.session_state:
    st.session_state.current_track = 0
if 'volume' not in st.session_state:
    st.session_state.volume = 70  # 0-100
if 'playback_speed' not in st.session_state:
    st.session_state.playback_speed = 1.0
if 'player_state' not in st.session_state:
    st.session_state.player_state = "stopped"
if 'audio_data_urls' not in st.session_state:
    st.session_state.audio_data_urls = {}

def load_text_file(filename):
    """Load nội dung file text"""
    if not os.path.exists(filename):
        return f"File không tồn tại: {filename}"
    
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1258', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                return f.read()
        except:
            continue
    
    try:
        with open(filename, 'rb') as f:
            content = f.read()
        return content.decode('utf-8', errors='replace')
    except Exception as e:
        return f"Lỗi đọc file: {str(e)}"

def get_audio_data_url(audio_file):
    """Chuyển đổi audio file thành data URL để phát"""
    if audio_file in st.session_state.audio_data_urls:
        return st.session_state.audio_data_urls[audio_file]
    
    try:
        if os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                data = f.read()
                base64_encoded = base64.b64encode(data).decode()
                mime_type = "audio/mpeg" if audio_file.endswith('.mp3') else "audio/wav"
                data_url = f"data:{mime_type};base64,{base64_encoded}"
                st.session_state.audio_data_urls[audio_file] = data_url
                return data_url
        return None
    except Exception as e:
        st.error(f"Lỗi khi đọc file audio: {str(e)}")
        return None

def create_audio_player():
    """Tạo HTML audio player với controls"""
    current_audio = TRACKS[st.session_state.current_track]["audio"]
    audio_url = get_audio_data_url(current_audio)
    
    if not audio_url:
        return f"""
        <div class="audio-controls">
            <div style="color: red; padding: 20px; text-align: center;">
                Không thể tải file audio: {current_audio}
            </div>
        </div>
        """
    
    audio_player_html = f"""
    <div class="audio-controls">
        <audio id="audioPlayer" controls style="width: 100%;">
            <source src="{audio_url}" type="audio/mpeg">
            Trình duyệt của bạn không hỗ trợ phát audio.
        </audio>
        
        <div class="slider-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold;">Âm lượng:</span>
                <span id="volumeValue" class="slider-value">{st.session_state.volume}%</span>
            </div>
            <input type="range" id="volumeSlider" min="0" max="100" value="{st.session_state.volume}" 
                   style="width: 100%; height: 10px;" 
                   oninput="document.getElementById('volumeValue').textContent = this.value + '%'; 
                            document.getElementById('audioPlayer').volume = this.value / 100;">
        </div>
        
        <div class="slider-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold;">Tốc độ phát:</span>
                <span id="speedValue" class="slider-value">{st.session_state.playback_speed:.1f}x</span>
            </div>
            <input type="range" id="speedSlider" min="0.5" max="2.0" step="0.1" value="{st.session_state.playback_speed}" 
                   style="width: 100%; height: 10px;" 
                   oninput="document.getElementById('speedValue').textContent = parseFloat(this.value).toFixed(1) + 'x'; 
                            document.getElementById('audioPlayer').playbackRate = parseFloat(this.value);">
        </div>
    </div>
    
    <script>
        // Khởi tạo giá trị khi trang tải xong
        window.addEventListener('DOMContentLoaded', function() {{
            const audio = document.getElementById('audioPlayer');
            if (audio) {{
                // Đặt volume ban đầu
                audio.volume = {st.session_state.volume / 100};
                
                // Đặt tốc độ ban đầu
                audio.playbackRate = {st.session_state.playback_speed};
            }}
        }});
    </script>
    """
    return audio_player_html

def main():
    st.markdown('<h1 class="main-header">🎵 Audio Player with Text Sync</h1>', unsafe_allow_html=True)
    
    # Kiểm tra file tồn tại
    with st.sidebar:
        st.markdown("### 📂 Kiểm tra file")
        
        # Hiển thị dạng bảng 2 cột
        for i in range(0, len(TRACKS), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                track = TRACKS[i]
                audio_exists = os.path.exists(track["audio"])
                text_exists = os.path.exists(track["text"])
                
                st.markdown(f"**Track {i+1}**")
                if audio_exists:
                    st.success(f"🎵 {track['audio']}")
                else:
                    st.error(f"🎵 {track['audio']}")
                
                if text_exists:
                    st.success(f"📄 {track['text']}")
                else:
                    st.error(f"📄 {track['text']}")
                
                # Nút chọn track
                if st.button(f"Chọn {i+1}", key=f"sidebar_select_{i}", use_container_width=True,
                           type="primary" if i == st.session_state.current_track else "secondary"):
                    st.session_state.current_track = i
                    st.rerun()
            
            if i + 1 < len(TRACKS):
                with col2:
                    track = TRACKS[i + 1]
                    audio_exists = os.path.exists(track["audio"])
                    text_exists = os.path.exists(track["text"])
                    
                    st.markdown(f"**Track {i+2}**")
                    if audio_exists:
                        st.success(f"🎵 {track['audio']}")
                    else:
                        st.error(f"🎵 {track['audio']}")
                    
                    if text_exists:
                        st.success(f"📄 {track['text']}")
                    else:
                        st.error(f"📄 {track['text']}")
                    
                    # Nút chọn track
                    if st.button(f"Chọn {i+2}", key=f"sidebar_select_{i+1}", use_container_width=True,
                               type="primary" if (i + 1) == st.session_state.current_track else "secondary"):
                        st.session_state.current_track = i + 1
                        st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎛️ Cài đặt Audio")
        
        # Điều chỉnh volume bằng Streamlit slider
        new_volume = st.slider("Âm lượng", 0, 100, st.session_state.volume, key="volume_slider")
        if new_volume != st.session_state.volume:
            st.session_state.volume = new_volume
            st.rerun()
        
        # Điều chỉnh tốc độ bằng Streamlit slider
        new_speed = st.slider("Tốc độ phát", 0.5, 2.0, float(st.session_state.playback_speed), 0.1, key="speed_slider")
        if new_speed != st.session_state.playback_speed:
            st.session_state.playback_speed = new_speed
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ Thông tin")
        st.info(f"**Track hiện tại:** {st.session_state.current_track + 1}/{len(TRACKS)}")
        st.info(f"**Âm lượng:** {st.session_state.volume}%")
        st.info(f"**Tốc độ:** {st.session_state.playback_speed:.1f}x")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Danh sách Track")
        
        # Tạo grid layout cho danh sách track (2 cột)
        st.markdown('<div class="track-grid">', unsafe_allow_html=True)
        
        # Hiển thị 10 track trong grid 2x5
        for idx in range(len(TRACKS)):
            track = TRACKS[idx]
            audio_exists = os.path.exists(track["audio"])
            text_exists = os.path.exists(track["text"])
            
            # Kiểm tra nếu cả hai file đều tồn tại
            if audio_exists and text_exists:
                status_icon = "✅"
            else:
                status_icon = "❌"
            
            is_active = idx == st.session_state.current_track
            track_class = "track-item active" if is_active else "track-item"
            
            # Tạo HTML cho mỗi track item
            track_html = f"""
            <div class="{track_class}" onclick="selectTrack({idx})">
                <div style="font-weight: bold; font-size: 1.1em;">
                    Track {idx+1} {status_icon}
                </div>
                <div style="font-size: 0.9em; margin-top: 5px;">
                    <div>🎵 {track['audio'].replace('.mp3', '')}</div>
                    <div>📄 {track['text'].replace('.txt', '')}</div>
                </div>
            </div>
            """
            st.markdown(track_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # JavaScript để xử lý click trên track item
        st.markdown(f"""
        <script>
        function selectTrack(index) {{
            // Gửi thông điệp đến Streamlit (giả lập)
            // Trong thực tế, bạn có thể dùng streamlit.components để giao tiếp
            // Tạm thời dùng cách đơn giản là reload với tham số
            window.location.href = window.location.pathname + "?track=" + index;
        }}
        
        // Đọc tham số từ URL
        const urlParams = new URLSearchParams(window.location.search);
        const trackParam = urlParams.get('track');
        if (trackParam !== null) {{
            // Đã chọn track từ URL
        }}
        </script>
        """, unsafe_allow_html=True)
        
        # Navigation buttons
        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        
        with col_nav1:
            if st.button("⏮️ Trước", key="btn_prev", use_container_width=True, 
                        disabled=st.session_state.current_track == 0):
                st.session_state.current_track = max(0, st.session_state.current_track - 1)
                st.rerun()
        
        with col_nav2:
            current_track_display = TRACKS[st.session_state.current_track]
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background-color: #e3f2fd; border-radius: 5px;">
                <strong>Track {st.session_state.current_track + 1}</strong><br>
                <small>{current_track_display['audio'].replace('.mp3', '')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_nav3:
            if st.button("Tiếp ⏭️", key="btn_next", use_container_width=True,
                        disabled=st.session_state.current_track == len(TRACKS) - 1):
                st.session_state.current_track = min(len(TRACKS) - 1, st.session_state.current_track + 1)
                st.rerun()
        
        # Hiển thị audio player
        st.markdown("### 🔊 Audio Player")
        audio_player_html = create_audio_player()
        st.components.v1.html(audio_player_html, height=200)
        
        # Thông tin track hiện tại
        current_track_info = TRACKS[st.session_state.current_track]
        st.markdown(f"""
        <div class="status-bar">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <strong>🎵 Track hiện tại:</strong> {st.session_state.current_track + 1}. {current_track_info['audio']}<br>
                    <strong>📄 File text:</strong> {current_track_info['text']}
                </div>
                <div style="text-align: right;">
                    <strong>🔊 Âm lượng:</strong> {st.session_state.volume}%<br>
                    <strong>⚡ Tốc độ:</strong> {st.session_state.playback_speed:.1f}x
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📄 Nội dung Text")
        
        # Load và hiển thị nội dung file text
        current_text_file = TRACKS[st.session_state.current_track]["text"]
        
        if os.path.exists(current_text_file):
            # Hiển thị thông tin file với highlight
            file_size = os.path.getsize(current_text_file)
            
            # Tạo header với highlight
            current_audio_file = TRACKS[st.session_state.current_track]["audio"]
            st.markdown(f"""
            <div style="background-color: #2196F3; color: white; padding: 15px; border-radius: 10px 10px 0 0; margin-bottom: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: white;">🎵 {current_audio_file.replace('.mp3', '')} | 📁 {current_text_file}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em;">Kích thước: {file_size:,} bytes | Track {st.session_state.current_track + 1}/{len(TRACKS)}</p>
                    </div>
                    <div style="background-color: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-weight: bold;">
                        {current_audio_file.replace('.mp3', '')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Đọc và hiển thị nội dung
            text_content = load_text_file(current_text_file)
            
            if text_content:
                # Tạo text display với scroll và highlight
                st.markdown(f"""
                <div class="text-display">
                    {text_content}
                </div>
                """, unsafe_allow_html=True)
                
                # Thống kê và download button
                col_info, col_download = st.columns([2, 1])
                
                with col_info:
                    lines = text_content.split('\n')
                    words = text_content.split()
                    chars = len(text_content)
                    st.caption(f"📊 Thống kê: {len(lines)} dòng, {len(words)} từ, {chars:,} ký tự")
                
                with col_download:
                    with open(current_text_file, "rb") as f:
                        st.download_button(
                            label="📥 Tải xuống",
                            data=f,
                            file_name=current_text_file,
                            mime="text/plain",
                            use_container_width=True
                        )
            else:
                st.warning("File text tồn tại nhưng không có nội dung hoặc không thể đọc.")
        else:
            st.error(f"❌ File text không tồn tại: {current_text_file}")
            
            # Tạo file text mẫu
            st.info("Tạo file text mẫu để test:")
            
            sample_content = f"""Đây là nội dung mẫu cho file {current_text_file}

Bạn có thể chỉnh sửa nội dung này hoặc thay thế bằng nội dung thực tế.

Các tính năng của ứng dụng:
1. Phát audio file tương ứng: {TRACKS[st.session_state.current_track]['audio']}
2. Hiển thị nội dung text đồng bộ
3. Điều chỉnh âm lượng và tốc độ phát
4. Chuyển đổi giữa các track dễ dàng

Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            if st.button("📝 Tạo file text mẫu", key="create_sample"):
                try:
                    with open(current_text_file, 'w', encoding='utf-8') as f:
                        f.write(sample_content)
                    st.success(f"✅ Đã tạo file {current_text_file}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi tạo file: {str(e)}")
    
    # Hướng dẫn sử dụng
    with st.expander("📖 Hướng dẫn sử dụng"):
        st.markdown("""
        ### 🎯 Cách sử dụng:
        
        1. **Chọn track**: 
           - Nhấp vào track trong danh sách grid (2 cột)
           - Hoặc nhấp nút "Chọn" trong sidebar
           - Track đang chọn sẽ được highlight bằng màu xanh
        
        2. **Điều khiển phát nhạc**:
           - Sử dụng nút play/pause/stop tích hợp trong audio player
           - Sử dụng nút ⏮️ và ⏭️ để chuyển track
        
        3. **Điều chỉnh audio**:
           - Sử dụng thanh trượt "Âm lượng" trong audio player hoặc sidebar
           - Sử dụng thanh trượt "Tốc độ phát" trong audio player hoặc sidebar
           - Giá trị sẽ được cập nhật ngay lập tức
        
        4. **Xem nội dung text**:
           - Nội dung file text tương ứng sẽ hiển thị trong khung màu xanh
           - Có thể tải xuống file text bằng nút "Tải xuống"
        
        ### 📋 Danh sách track mới:
        - QT 03, QT 09, QT 13, QT 15, QT 23
        - QT 30, QT 66, QT 67, QT 68, QT 69
        
        ### 🔧 Xử lý sự cố:
        
        - **Không nghe được âm thanh**: Kiểm tra xem file audio có tồn tại không
        - **Không thấy nội dung text**: Kiểm tra xem file text có tồn tại không
        - **Thanh trượt không hoạt động**: Làm mới trang trình duyệt
        """)

if __name__ == "__main__":
    main()
