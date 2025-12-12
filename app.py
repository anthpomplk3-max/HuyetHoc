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
    .process-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        border-left: 5px solid #4CAF50;
        transition: all 0.3s;
        cursor: pointer;
    }
    .process-card:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .active-process {
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
    .scrollable-list {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        background-color: #f9f9f9;
    }
    .process-list-item {
        padding: 12px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .process-list-item:hover {
        background-color: #e9ecef;
    }
    .process-list-item.active {
        background-color: #2196F3;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Danh sách các Quy Trình
PROCESSES = [
    {"name": "QT 03", "audio": "QT 03.mp3", "text": "QT 03.txt"},
    {"name": "QT 09", "audio": "QT 09.mp3", "text": "QT 09.txt"},
    {"name": "QT 13", "audio": "QT 13.mp3", "text": "QT 13.txt"},
    {"name": "QT 15", "audio": "QT 15.mp3", "text": "QT 15.txt"},
    {"name": "QT 23", "audio": "QT 23.mp3", "text": "QT 23.txt"},
    {"name": "QT 30", "audio": "QT 30.mp3", "text": "QT 30.txt"},
    {"name": "QT 66", "audio": "QT 66.mp3", "text": "QT 66.txt"},
    {"name": "QT 67", "audio": "QT 67.mp3", "text": "QT 67.txt"},
    {"name": "QT 68", "audio": "QT 68.mp3", "text": "QT 68.txt"},
    {"name": "QT 69", "audio": "QT 69.mp3", "text": "QT 69.txt"}
]

# Khởi tạo session state
if 'current_process' not in st.session_state:
    st.session_state.current_process = 0
if 'volume' not in st.session_state:
    st.session_state.volume = 70  # 0-100
if 'playback_speed' not in st.session_state:
    st.session_state.playback_speed = 1.0
if 'player_state' not in st.session_state:
    st.session_state.player_state = "stopped"
if 'audio_data_urls' not in st.session_state:
    st.session_state.audio_data_urls = {}

def load_text_file(filename):
    """Load nội dung file text với nhiều encoding"""
    if not os.path.exists(filename):
        return f"❌ File không tồn tại: {filename}\n\nVui lòng kiểm tra:\n1. File có tồn tại trong thư mục không?\n2. Tên file có đúng không?\n3. File có bị xóa không?"
    
    # Thử nhiều encoding khác nhau
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1258', 'iso-8859-1', 'ascii']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
                if content.strip():  # Nếu có nội dung
                    return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            continue
    
    # Nếu không đọc được, thử đọc binary và decode
    try:
        with open(filename, 'rb') as f:
            raw_data = f.read()
        
        # Thử các encoding phổ biến cho tiếng Việt
        for encoding in ['utf-8', 'utf-16', 'cp1258']:
            try:
                return raw_data.decode(encoding)
            except:
                continue
        
        # Cuối cùng, thử decode với errors='replace'
        return raw_data.decode('utf-8', errors='replace')
    except Exception as e:
        return f"⚠️ Lỗi khi đọc file:\n{str(e)}\n\nThông tin file:\n- Tên: {filename}\n- Kích thước: {os.path.getsize(filename) if os.path.exists(filename) else 0} bytes"

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
    current_process = PROCESSES[st.session_state.current_process]
    audio_file = current_process["audio"]
    audio_url = get_audio_data_url(audio_file)
    
    if not audio_url:
        return f"""
        <div class="audio-controls">
            <div style="color: red; padding: 20px; text-align: center;">
                ⚠️ Không thể tải file audio: {audio_file}
                <br><small>Vui lòng kiểm tra xem file có tồn tại không</small>
            </div>
        </div>
        """
    
    audio_player_html = f"""
    <div class="audio-controls">
        <audio id="audioPlayer" controls style="width: 100%;" autoplay>
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
    
    # Sidebar - Danh sách Quy Trình với thanh cuộn
    with st.sidebar:
        st.markdown("### 📋 Danh sách Quy Trình")
        
        # Tạo container scrollable cho danh sách quy trình
        st.markdown('<div class="scrollable-list">', unsafe_allow_html=True)
        
        for idx, process in enumerate(PROCESSES):
            audio_exists = os.path.exists(process["audio"])
            text_exists = os.path.exists(process["text"])
            
            # Xác định icon trạng thái
            if audio_exists and text_exists:
                status_icon = "✅"
            else:
                status_icon = "❌"
            
            # Xác định class cho item đang active
            is_active = idx == st.session_state.current_process
            item_class = "process-list-item active" if is_active else "process-list-item"
            
            # Tạo HTML cho mỗi item
            item_html = f"""
            <div class="{item_class}" onclick="selectProcess({idx})" style="{'background-color: #2196F3; color: white;' if is_active else ''}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>Quy trình {idx+1}: {process['name']}</strong>
                        <div style="font-size: 0.85em; margin-top: 3px;">
                            <span>🎵 {process['audio']}</span><br>
                            <span>📄 {process['text']}</span>
                        </div>
                    </div>
                    <div>{status_icon}</div>
                </div>
            </div>
            """
            st.markdown(item_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Thêm JavaScript để xử lý click (giả lập)
        st.markdown("""
        <script>
        function selectProcess(index) {
            // Đây là phần giả lập, trong thực tế cần tích hợp với Streamlit
            window.location.href = window.location.pathname + "?process=" + index;
        }
        </script>
        """, unsafe_allow_html=True)
        
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
        
        # Thông tin thống kê
        st.markdown("---")
        st.markdown("### 📊 Thông tin")
        
        current_process = PROCESSES[st.session_state.current_process]
        audio_exists = os.path.exists(current_process["audio"])
        text_exists = os.path.exists(current_process["text"])
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Quy trình", f"{st.session_state.current_process + 1}/{len(PROCESSES)}")
        with col_stat2:
            if audio_exists and text_exists:
                st.success("✅ Đầy đủ")
            else:
                st.error("❌ Thiếu file")
        
        st.info(f"**Đang chọn:** {current_process['name']}")
        st.info(f"**Âm lượng:** {st.session_state.volume}%")
        st.info(f"**Tốc độ:** {st.session_state.playback_speed:.1f}x")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎵 Audio Player")
        
        # Navigation buttons
        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        
        with col_nav1:
            if st.button("⏮️ Trước", key="btn_prev", use_container_width=True, 
                        disabled=st.session_state.current_process == 0):
                st.session_state.current_process = max(0, st.session_state.current_process - 1)
                st.rerun()
        
        with col_nav2:
            current_process = PROCESSES[st.session_state.current_process]
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background-color: #e3f2fd; border-radius: 5px;">
                <strong>Quy trình {st.session_state.current_process + 1}: {current_process['name']}</strong><br>
                <small>🎵 {current_process['audio']} | 📄 {current_process['text']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_nav3:
            if st.button("Tiếp ⏭️", key="btn_next", use_container_width=True,
                        disabled=st.session_state.current_process == len(PROCESSES) - 1):
                st.session_state.current_process = min(len(PROCESSES) - 1, st.session_state.current_process + 1)
                st.rerun()
        
        # Hiển thị audio player
        audio_player_html = create_audio_player()
        st.components.v1.html(audio_player_html, height=200)
        
        # Thông tin chi tiết
        current_process_info = PROCESSES[st.session_state.current_process]
        audio_exists = os.path.exists(current_process_info["audio"])
        text_exists = os.path.exists(current_process_info["text"])
        
        st.markdown(f"""
        <div class="status-bar">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <strong>🎵 Audio:</strong> {current_process_info['audio']} {"✅" if audio_exists else "❌"}<br>
                    <strong>📄 Text:</strong> {current_process_info['text']} {"✅" if text_exists else "❌"}
                </div>
                <div style="text-align: right;">
                    <strong>🔊 Âm lượng:</strong> {st.session_state.volume}%<br>
                    <strong>⚡ Tốc độ:</strong> {st.session_state.playback_speed:.1f}x
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Nút refresh để kiểm tra lại file
        if st.button("🔄 Kiểm tra lại file", key="btn_refresh", use_container_width=True):
            st.rerun()
    
    with col2:
        st.markdown("### 📄 Nội dung Text")
        
        # Load và hiển thị nội dung file text
        current_process = PROCESSES[st.session_state.current_process]
        text_file = current_process["text"]
        
        # Tạo header với thông tin
        audio_file = current_process["audio"]
        text_exists = os.path.exists(text_file)
        audio_exists = os.path.exists(audio_file)
        
        # Header
        st.markdown(f"""
        <div style="background-color: #2196F3; color: white; padding: 15px; border-radius: 10px 10px 0 0; margin-bottom: 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: white;">Quy trình {st.session_state.current_process + 1}: {current_process['name']}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em;">
                        Audio: {audio_file} {"✅" if audio_exists else "❌"} | 
                        Text: {text_file} {"✅" if text_exists else "❌"}
                    </p>
                </div>
                <div style="background-color: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-weight: bold;">
                    QT {current_process['name'].split()[-1]}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if text_exists:
            # Đọc và hiển thị nội dung
            text_content = load_text_file(text_file)
            
            if text_content:
                # Kiểm tra nếu nội dung có vẻ là lỗi
                if "❌ File không tồn tại" in text_content or "⚠️ Lỗi khi đọc file" in text_content:
                    st.markdown(f"""
                    <div class="text-display" style="background-color: #ffebee;">
                        {text_content}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Thêm nút debug
                    with st.expander("🔧 Debug thông tin file"):
                        st.write(f"**Tên file:** {text_file}")
                        st.write(f"**Đường dẫn đầy đủ:** {os.path.abspath(text_file)}")
                        st.write(f"**File tồn tại:** {os.path.exists(text_file)}")
                        if os.path.exists(text_file):
                            st.write(f"**Kích thước:** {os.path.getsize(text_file)} bytes")
                            st.write(f"**Thời gian sửa đổi:** {time.ctime(os.path.getmtime(text_file))}")
                            
                            # Thử đọc raw bytes
                            with open(text_file, 'rb') as f:
                                raw_bytes = f.read(500)  # Đọc 500 byte đầu
                            st.write(f"**500 byte đầu (hex):**")
                            st.code(raw_bytes.hex())
                else:
                    # Hiển thị nội dung bình thường
                    st.markdown(f"""
                    <div class="text-display">
                        {text_content}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Thống kê
                    lines = text_content.split('\n')
                    words = text_content.split()
                    chars = len(text_content)
                    
                    col_info, col_download = st.columns([2, 1])
                    
                    with col_info:
                        st.caption(f"📊 Thống kê: {len(lines)} dòng, {len(words)} từ, {chars:,} ký tự")
                    
                    with col_download:
                        with open(text_file, "rb") as f:
                            st.download_button(
                                label="📥 Tải xuống",
                                data=f,
                                file_name=text_file,
                                mime="text/plain",
                                use_container_width=True
                            )
            else:
                st.warning("File text tồn tại nhưng không có nội dung hoặc không thể đọc.")
        else:
            st.error(f"❌ File text không tồn tại: {text_file}")
            
            # Tạo file text mẫu
            st.info("Tạo file text mẫu để test:")
            
            sample_content = f"""Đây là nội dung mẫu cho file {text_file}

QUY TRÌNH: {current_process['name']}
AUDIO: {audio_file}

Nội dung mẫu:
1. Mục tiêu của quy trình
2. Các bước thực hiện
3. Lưu ý và cảnh báo
4. Tài liệu tham khảo

Thời gian tạo: {time.strftime('%Y-%m-%d %H:%M:%S')}

Bạn có thể chỉnh sửa nội dung này hoặc thay thế bằng nội dung thực tế.
"""
            
            if st.button("📝 Tạo file text mẫu", key="create_sample"):
                try:
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(sample_content)
                    st.success(f"✅ Đã tạo file {text_file}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi tạo file: {str(e)}")
    
    # Hướng dẫn sử dụng
    with st.expander("📖 Hướng dẫn sử dụng"):
        st.markdown("""
        ### 🎯 Cách sử dụng:
        
        1. **Chọn Quy Trình**: 
           - Chọn từ danh sách quy trình trong sidebar bên trái
           - Sử dụng nút ⏮️ và ⏭️ để chuyển quy trình
           - Quy trình đang chọn sẽ được highlight màu xanh
        
        2. **Điều khiển Audio**:
           - Sử dụng audio player để phát/tạm dừng/dừng
           - Điều chỉnh âm lượng bằng thanh trượt
           - Điều chỉnh tốc độ phát (0.5x - 2.0x)
        
        3. **Xem nội dung Text**:
           - Nội dung file text tương ứng sẽ hiển thị bên phải
           - Có thể tải xuống file text bằng nút "Tải xuống"
        
        4. **Kiểm tra file**:
           - ✅: File tồn tại
           - ❌: File không tồn tại
           - Nút "🔄 Kiểm tra lại file" để cập nhật trạng thái
        
        ### 🔧 Xử lý sự cố đọc file text:
        
        - **File không tồn tại**: Tạo file mẫu bằng nút "Tạo file text mẫu"
        - **Lỗi encoding**: Ứng dụng tự động thử nhiều encoding khác nhau
        - **Nội dung không hiển thị**: Mở phần Debug để xem thông tin chi tiết
        
        ### 📋 Danh sách Quy Trình:
        
        1. QT 03
        2. QT 09
        3. QT 13
        4. QT 15
        5. QT 23
        6. QT 30
        7. QT 66
        8. QT 67
        9. QT 68
        10. QT 69
        """)

if __name__ == "__main__":
    main()
