import streamlit as st
import random

# Thiết lập cấu hình trang web
st.set_page_config(page_title="Vietlott Smart Picker", page_icon="🎯", layout="centered")

st.title("🎯 Vietlott Smart Picker")
st.caption("Ứng dụng lọc số ngẫu nhiên & phân tích cấu trúc toán học")

# Khởi tạo lịch sử trong session_state
if "history" not in st.session_state:
    st.session_state.history = []

# --- KHU VỰC CẤU HÌNH ---
st.subheader("⚙️ Cấu hình chọn số")

game_type = st.selectbox("Chọn loại giải", ["Mega 6/45", "Power 6/55"])
max_num = 45 if game_type == "Mega 6/45" else 55

# Chọn phương thức loại số
exclude_mode = st.radio(
    "Phương thức loại số:",
    ["🎲 Loại ngẫu nhiên", "✋ Tự chọn số loại thủ công"],
    horizontal=True
)

excluded_numbers = []

if exclude_mode == "🎲 Loại ngẫu nhiên":
    exclude_count = st.number_input("Số lượng số muốn loại", min_value=1, max_value=20, value=6)
else:
    all_numbers_list = list(range(1, max_num + 1))
    # Cho phép chọn tay danh sách số loại
    excluded_numbers = st.multiselect(
        f"Chọn các số bạn muốn LOẠI BỎ (trong khoảng 1 - {max_num}):",
        options=all_numbers_list,
        format_func=lambda x: f"{x:02d}",
        default=[1, 2, 3, 4, 5, 6]  # Giá trị mặc định gợi ý
    )
    st.caption(f"Đã chọn loại: **{len(excluded_numbers)}** số")

# --- BỘ LỌC THÔNG MINH ---
st.markdown("---")
st.subheader("🛠️ Bộ lọc thuật toán")

col_f1, col_f2 = st.columns(2)
with col_f1:
    enable_parity = st.checkbox("Lọc tỷ lệ Chẵn / Lẻ", value=True, help="Chỉ chấp nhận các bộ số có tỷ lệ Chẵn/Lẻ cân bằng (2:4, 3:3, 4:2)")
with col_f2:
    enable_sum = st.checkbox("Lọc tổng dãy số", value=True, help="Chỉ chọn bộ số có tổng nằm trong khoảng phổ biến")

sum_min = 90 if game_type == "Mega 6/45" else 120
sum_max = 180 if game_type == "Mega 6/45" else 210

# --- THUẬT TOÁN XỬ LÝ ---
def is_valid_combination(combo):
    if enable_parity:
        evens = sum(1 for x in combo if x % 2 == 0)
        if evens not in [2, 3, 4]:
            return False
            
    if enable_sum:
        total_sum = sum(combo)
        if not (sum_min <= total_sum <= sum_max):
            return False
            
    return True

# --- NÚT BẤM TẠO SỐ ---
if st.button("🎲 BỐC SỐ MAY MẮN", use_container_width=True, type="primary"):
    all_numbers = list(range(1, max_num + 1))
    
    # Xử lý tập số loại dựa theo chế độ chọn
    if exclude_mode == "🎲 Loại ngẫu nhiên":
        if exclude_count >= max_num - 6:
            st.error("Số lượng loại quá nhiều, không đủ 6 số còn lại để chọn!")
            st.stop()
        final_excluded = sorted(random.sample(all_numbers, exclude_count))
    else:
        if len(excluded_numbers) >= max_num - 6:
            st.error(f"Bạn đã chọn loại {len(excluded_numbers)} số, không còn đủ 6 số còn lại để chọn vé!")
            st.stop()
        if len(excluded_numbers) == 0:
            st.warning("Bạn chưa chọn số nào để loại! Hệ thống sẽ chọn trong toàn bộ số.")
        final_excluded = sorted(excluded_numbers)
        
    # Lọc ra danh sách số còn lại
    remaining_numbers = [n for n in all_numbers if n not in final_excluded]
    
    if len(remaining_numbers) < 6:
        st.error("Tập số còn lại nhỏ hơn 6, không thể tạo vé!")
        st.stop()

    # Tìm bộ số thỏa mãn bộ lọc
    selected_numbers = None
    for _ in range(1000):
        candidate = sorted(random.sample(remaining_numbers, 6))
        if is_valid_combination(candidate):
            selected_numbers = candidate
            break
            
    if selected_numbers is None:
        selected_numbers = sorted(random.sample(remaining_numbers, 6))
        st.warning("Không tìm thấy bộ số thỏa mãn 100% bộ lọc khắt khe, hệ thống đã chọn ngẫu nhiên một bộ từ tập còn lại.")

    # Lưu kết quả
    res_entry = {
        "game": game_type,
        "mode": "Tự chọn" if exclude_mode != "🎲 Loại ngẫu nhiên" else "Ngẫu nhiên",
        "excluded": final_excluded,
        "selected": selected_numbers,
        "sum": sum(selected_numbers),
        "evens": sum(1 for x in selected_numbers if x % 2 == 0)
    }
    st.session_state.history.insert(0, res_entry)

    # Hiển thị kết quả
    st.markdown("---")
    st.subheader("🎯 Kết quả hiện tại")
    
    st.write(f"**Tập số đã LOẠI BỎ ({len(final_excluded)} số):**")
    if final_excluded:
        st.code(", ".join([f"{n:02d}" for n in final_excluded]))
    else:
        st.info("Không loại bỏ số nào.")
    
    st.write("**Bộ 6 số ĐƯỢC CHỌN:**")
    st.success(" - ".join([f"{n:02d}" for n in selected_numbers]))
    
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Tổng dãy số", sum(selected_numbers))
    col_m2.metric("Số Chẵn / Số Lẻ", f"{res_entry['evens']} / {6 - res_entry['evens']}")

# --- HIỂN THỊ LỊCH SỬ ---
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Lịch sử các bộ số đã tạo")
    
    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"Lần {len(st.session_state.history) - idx}: {item['game']} ({item['mode']}) | Bộ số: {', '.join([f'{n:02d}' for n in item['selected']])}"):
            st.write(f"• **Số loại ({len(item['excluded'])} số):** {', '.join([f'{n:02d}' for n in item['excluded']]) if item['excluded'] else 'Không'}")
            st.write(f"• **Tổng dãy số:** {item['sum']}")
            st.write(f"• **Chẵn / Lẻ:** {item['evens']} / {6 - item['evens']}")
