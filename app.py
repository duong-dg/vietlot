import streamlit as st
import random
import json
import os

# --- 1. THIẾT LẬP CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Vietlott Smart Picker", 
    page_icon="🎯", 
    layout="centered"
)

st.title("🎯 Vietlott Smart Picker")
st.caption("Công cụ tối ưu bộ số ngẫu nhiên & Phân tích cấu trúc dữ liệu")

# Khởi tạo lịch sử trong session_state
if "history" not in st.session_state:
    st.session_state.history = []

# --- 2. NẠP DỮ LIỆU LỊCH SỬ TỪ FILE JSON (NẾU CÓ) ---
@st.cache_data
def load_vietlott_dataset():
    if os.path.exists("vietlott_history.json"):
        try:
            with open("vietlott_history.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"mega645": [], "power655": []}
    return {"mega645": [], "power655": []}

dataset = load_vietlott_dataset()

# Hiển thị thông tin dữ liệu ở thanh bên (Sidebar)
st.sidebar.title("📊 Dữ liệu Lịch sử")
mega_count = len(dataset.get("mega645", []))
power_count = len(dataset.get("power655", []))

if mega_count > 0 or power_count > 0:
    st.sidebar.success(f"• Mega 6/45: **{mega_count}** kỳ\n• Power 6/55: **{power_count}** kỳ")
else:
    st.sidebar.info("Chưa tìm thấy file `vietlott_history.json`. Ứng dụng vẫn chạy bình thường với chế độ tạo số ngẫu nhiên!")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Dữ liệu lịch sử dùng để kiểm tra rủi ro trùng 100% với giải Jackpot đã nổ trong quá khứ.")

# --- 3. KHU VỰC CẤU HÌNH LOẠI SỐ ---
st.subheader("⚙️ Cấu hình loại số")

game_type = st.selectbox("Chọn loại giải", ["Mega 6/45", "Power 6/55"])
max_num = 45 if game_type == "Mega 6/45" else 55
game_key = "mega645" if game_type == "Mega 6/45" else "power655"

exclude_mode = st.radio(
    "Phương thức loại số:",
    ["🎲 Loại ngẫu nhiên", "✋ Tự chọn số loại thủ công"],
    horizontal=True
)

excluded_numbers = []

if exclude_mode == "🎲 Loại ngẫu nhiên":
    exclude_count = st.number_input("Số lượng số muốn loại", min_value=1, max_value=20, value=6)
else:
    excluded_numbers = st.multiselect(
        f"Chọn các số bạn muốn LOẠI BỎ (trong khoảng 1 - {max_num}):",
        options=list(range(1, max_num + 1)),
        format_func=lambda x: f"{x:02d}",
        default=[1, 2, 3, 4, 5, 6]
    )
    st.caption(f"Đã chọn loại: **{len(excluded_numbers)}** số")

# --- 4. BỘ LỌC CẤU TRÚC TOÁN HỌC ---
st.markdown("---")
st.subheader("🛠️ Bộ lọc cấu trúc dãy số")

col_f1, col_f2 = st.columns(2)
with col_f1:
    enable_parity = st.checkbox("Cân bằng Chẵn / Lẻ", value=True, help="Giữ tỷ lệ Chẵn/Lẻ ở mức 2:4, 3:3 hoặc 4:2")
with col_f2:
    enable_sum = st.checkbox("Cân bằng Tổng dãy số", value=True, help="Giữ tổng dãy số nằm trong khoảng phổ biến thực tế")

sum_min = 90 if game_type == "Mega 6/45" else 120
sum_max = 180 if game_type == "Mega 6/45" else 210

# --- 5. HÀM THUẬT TOÁN BỔ TRỢ ---
def calculate_uniqueness_score(combo):
    """Tính chỉ số độc lạ dựa trên việc né số ngày sinh (1-31) và số đuôi may mắn (6, 8, 9)."""
    over_31_count = sum(1 for x in combo if x > 31)
    lucky_tail_count = sum(1 for x in combo if x % 10 in [6, 8, 9])
    
    score = (over_31_count * 15) + ((6 - lucky_tail_count) * 10) + 10
    return min(max(score, 20), 99)

def is_valid_combination(combo):
    """Kiểm tra xem bộ số có thỏa mãn các bộ lọc cấu trúc hay không."""
    if enable_parity:
        evens = sum(1 for x in combo if x % 2 == 0)
        if evens not in [2, 3, 4]:
            return False
            
    if enable_sum:
        total_sum = sum(combo)
        if not (sum_min <= total_sum <= sum_max):
            return False
            
    return True

def check_historical_jackpot(selected_numbers, g_key):
    """Kiểm tra xem bộ 6 số có trùng 100% với một kết quả Jackpot trong lịch sử hay không."""
    history = dataset.get(g_key, [])
    if not history:
        return False, None, None
        
    selected_set = set(selected_numbers)
    for draw in history:
        if set(draw.get("numbers", [])) == selected_set:
            return True, draw.get("draw_id", "N/A"), draw.get("date", "N/A")
            
    return False, None, None

# --- 6. NÚT XỬ LÝ & BỐC SỐ ---
if st.button("🎲 BỐC SỐ MAY MẮN", use_container_width=True, type="primary"):
    all_numbers = list(range(1, max_num + 1))
    
    # Xác định tập số bị loại
    if exclude_mode == "🎲 Loại ngẫu nhiên":
        if exclude_count >= max_num - 6:
            st.error("Số lượng loại quá nhiều, không đủ 6 số còn lại để chọn!")
            st.stop()
        final_excluded = sorted(random.sample(all_numbers, exclude_count))
    else:
        if len(excluded_numbers) >= max_num - 6:
            st.error(f"Bạn đã chọn loại {len(excluded_numbers)} số, không còn đủ 6 số còn lại để chọn vé!")
            st.stop()
        final_excluded = sorted(excluded_numbers)
        
    # Tập số còn lại sau khi loại
    remaining_numbers = [n for n in all_numbers if n not in final_excluded]
    
    if len(remaining_numbers) < 6:
        st.error("Tập số còn lại nhỏ hơn 6, không thể tạo vé!")
        st.stop()

    # Vòng lặp tìm bộ số thỏa mãn bộ lọc (tối đa 1000 lần)
    selected_numbers = None
    for _ in range(1000):
        candidate = sorted(random.sample(remaining_numbers, 6))
        if is_valid_combination(candidate):
            selected_numbers = candidate
            break
            
    if selected_numbers is None:
        selected_numbers = sorted(random.sample(remaining_numbers, 6))
        st.warning("Không tìm thấy bộ số thỏa mãn 100% bộ lọc khắt khe, hệ thống đã chọn ngẫu nhiên một bộ từ tập còn lại.")

    # Tính toán các chỉ số
    unique_score = calculate_uniqueness_score(selected_numbers)
    is_duplicate, dup_id, dup_date = check_historical_jackpot(selected_numbers, game_key)

    # Lưu kết quả vào phiên làm việc
    res_entry = {
        "game": game_type,
        "mode": "Tự chọn" if exclude_mode != "🎲 Loại ngẫu nhiên" else "Ngẫu nhiên",
        "excluded": final_excluded,
        "selected": selected_numbers,
        "sum": sum(selected_numbers),
        "evens": sum(1 for x in selected_numbers if x % 2 == 0),
        "score": unique_score,
        "is_dup": is_duplicate
    }
    st.session_state.history.insert(0, res_entry)

    # --- 7. HIỂN THỊ KẾT QUẢ KỲ NÀY ---
    st.markdown("---")
    st.subheader("🎯 Kết quả hiện tại")
    
    st.write(f"**Tập số đã LOẠI BỎ ({len(final_excluded)} số):**")
    if final_excluded:
        st.code(", ".join([f"{n:02d}" for n in final_excluded]))
    else:
        st.info("Không loại bỏ số nào.")
    
    st.write("**Bộ 6 số ĐƯỢC CHỌN:**")
    st.success(" - ".join([f"{n:02d}" for n in selected_numbers]))
    
    # Cảnh báo lịch sử (nếu phát hiện trùng 100%)
    if is_duplicate:
        st.error(f"⚠️ **Cảnh báo Lịch sử:** Bộ số này đã từng trúng Jackpot ở kỳ quay #{dup_id} ngày {dup_date}!")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Tổng dãy số", sum(selected_numbers))
    col_m2.metric("Chẵn / Lẻ", f"{res_entry['evens']} / {6 - res_entry['evens']}")
    col_m3.metric("Mức độ Ít Trùng Hàng", f"{unique_score}%")

# --- 8. HIỂN THỊ LỊCH SỬ CÁC BỘ SỐ ĐÃ BỐC ---
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Lịch sử các bộ số đã tạo")
    
    for idx, item in enumerate(st.session_state.history):
        label_dup = " ⚠️ [ĐÃ TỪNG NỔ JACKPOT]" if item.get("is_dup") else ""
        with st.expander(f"Lần {len(st.session_state.history) - idx}: {item['game']} ({item['mode']}) | {', '.join([f'{n:02d}' for n in item['selected']])}{label_dup}"):
            st.write(f"• **Số loại ({len(item['excluded'])} số):** {', '.join([f'{n:02d}' for n in item['excluded']]) if item['excluded'] else 'Không'}")
            st.write(f"• **Tổng dãy:** {item['sum']} | **Chẵn/Lẻ:** {item['evens']}/{6-item['evens']} | **Độ độc lạ:** {item['score']}%")
