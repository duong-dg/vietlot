import streamlit as st
import random
import json
import os
import pandas as pd

# --- 1. THIẾT LẬP CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Vietlott Smart Picker", 
    page_icon="🎯", 
    layout="wide"
)

st.title("🎯 Vietlott Smart Picker")
st.caption("Công cụ tối ưu bộ số ngẫu nhiên & Phân tích cấu trúc dữ liệu")

# Khởi tạo lưu trữ lịch sử trong session
if "history" not in st.session_state:
    st.session_state.history = []

# --- 2. NẠP DỮ LIỆU LỊCH SỬ TỪ FILE JSON ---
def load_vietlott_dataset():
    file_path = "vietlott_history.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            st.sidebar.error(f"Lỗi đọc file JSON: {e}")
            return {"mega645": [], "power655": []}
    return {"mega645": [], "power655": []}

dataset = load_vietlott_dataset()

# Hiển thị trạng thái dữ liệu ở Sidebar
st.sidebar.title("📊 Dữ liệu Lịch sử")
mega_count = len(dataset.get("mega645", []))
power_count = len(dataset.get("power655", []))

if mega_count > 0 or power_count > 0:
    st.sidebar.success(f"✅ Đã kết nối dữ liệu:\n• Mega 6/45: **{mega_count}** kỳ\n• Power 6/55: **{power_count}** kỳ")
else:
    st.sidebar.warning("⚠️ Chưa tìm thấy `vietlott_history.json` trên GitHub repo!\n\nHãy đảm bảo bạn đã commit & push file này lên cùng thư mục với `app.py`.")

st.sidebar.markdown("---")

# --- 3. KHU VỰC CẤU HÌNH BỐC SỐ ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("⚙️ Cấu hình bộ số")
    
    game_type = st.selectbox("Chọn loại giải", ["Mega 6/45", "Power 6/55"])
    max_num = 45 if game_type == "Mega 6/45" else 55
    game_key = "mega645" if game_type == "Mega 6/45" else "power655"

    exclude_mode = st.radio(
        "Phương thức loại số:",
        ["🎲 Loại ngẫu nhiên", "✋ Tự chọn thủ công"],
        horizontal=True
    )

    excluded_numbers = []
    if exclude_mode == "🎲 Loại ngẫu nhiên":
        exclude_count = st.number_input("Số lượng số muốn loại", min_value=1, max_value=20, value=6)
    else:
        excluded_numbers = st.multiselect(
            f"Chọn các số bạn muốn LOẠI BỎ (1 - {max_num}):",
            options=list(range(1, max_num + 1)),
            format_func=lambda x: f"{x:02d}",
            default=[1, 2, 3, 4, 5, 6]
        )

    st.markdown("---")
    st.subheader("🛠️ Bộ lọc thuật toán")
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        enable_parity = st.checkbox("Cân bằng Chẵn/Lẻ", value=True)
    with c_f2:
        enable_sum = st.checkbox("Cân bằng Tổng", value=True)

    sum_min = 90 if game_type == "Mega 6/45" else 120
    sum_max = 180 if game_type == "Mega 6/45" else 210

# --- 4. HÀM THUẬT TOÁN BỔ TRỢ ---
def calculate_uniqueness_score(combo):
    over_31_count = sum(1 for x in combo if x > 31)
    lucky_tail_count = sum(1 for x in combo if x % 10 in [6, 8, 9])
    score = (over_31_count * 15) + ((6 - lucky_tail_count) * 10) + 10
    return min(max(score, 20), 99)

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

def check_historical_jackpot(selected_numbers, g_key):
    history = dataset.get(g_key, [])
    if not history:
        return False, None, None
    selected_set = set(selected_numbers)
    for draw in history:
        if set(draw.get("numbers", [])) == selected_set:
            return True, draw.get("draw_id", "N/A"), draw.get("date", "N/A")
    return False, None, None

# --- 5. NÚT BỐC SỐ & HIỂN THỊ KẾT QUẢ ---
with col_right:
    st.subheader("🎯 Kết quả bốc số")
    
    if st.button("🎲 BỐC SỐ MAY MẮN", use_container_width=True, type="primary"):
        all_numbers = list(range(1, max_num + 1))
        
        if exclude_mode == "🎲 Loại ngẫu nhiên":
            if exclude_count >= max_num - 6:
                st.error("Số lượng loại quá nhiều!")
                st.stop()
            final_excluded = sorted(random.sample(all_numbers, exclude_count))
        else:
            if len(excluded_numbers) >= max_num - 6:
                st.error("Số lượng loại thủ công quá nhiều!")
                st.stop()
            final_excluded = sorted(excluded_numbers)
            
        remaining_numbers = [n for n in all_numbers if n not in final_excluded]
        
        selected_numbers = None
        for _ in range(1000):
            candidate = sorted(random.sample(remaining_numbers, 6))
            if is_valid_combination(candidate):
                selected_numbers = candidate
                break
                
        if selected_numbers is None:
            selected_numbers = sorted(random.sample(remaining_numbers, 6))
            st.warning("Đã chọn ngẫu nhiên do bộ lọc quá khắt khe.")

        unique_score = calculate_uniqueness_score(selected_numbers)
        is_duplicate, dup_id, dup_date = check_historical_jackpot(selected_numbers, game_key)

        # Lưu thông tin vào Session State
        res_entry = {
            "Lần bốc": len(st.session_state.history) + 1,
            "Loại giải": game_type,
            "Bộ số chọn": " - ".join([f"{n:02d}" for n in selected_numbers]),
            "Số đã loại": ", ".join([f"{n:02d}" for n in final_excluded]) if final_excluded else "Không",
            "Tổng dãy": sum(selected_numbers),
            "Chẵn/Lẻ": f"{sum(1 for x in selected_numbers if x % 2 == 0)}/{6 - sum(1 for x in selected_numbers if x % 2 == 0)}",
            "Độ độc lạ": f"{unique_score}%",
            "Trùng Lịch sử": f"Cảnh báo kỳ #{dup_id}" if is_duplicate else "Chưa từng nổ"
        }
        st.session_state.history.insert(0, res_entry)

        # Hiển thị trực quan
        st.success(f"**Bộ số được chọn:**  \n### {res_entry['Bộ số chọn']}")
        st.caption(f"**Số đã loại:** {res_entry['Số đã loại']}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng dãy", res_entry["Tổng dãy"])
        m2.metric("Chẵn/Lẻ", res_entry["Chẵn/Lẻ"])
        m3.metric("Độ độc lạ", res_entry["Độ độc lạ"])

        if is_duplicate:
            st.error(f"⚠️️ Bộ số này trùng 100% với Jackpot kỳ #{dup_id} ngày {dup_date}!")

# --- 6. KHU VỰC XEM & LƯU LỊCH SỬ CHỌN SỐ ---
st.markdown("---")
st.subheader("📜 Bảng Lịch sử các bộ số đã bốc")

if st.session_state.history:
    df_history = pd.DataFrame(st.session_state.history)
    
    # Hiển thị bảng tương tác
    st.dataframe(df_history, use_container_width=True)
    
    col_h1, col_h2 = st.columns([1, 4])
    with col_h1:
        # Nút xuất file CSV
        csv_data = df_history.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Tải Lịch sử (.CSV)",
            data=csv_data,
            file_name="lich_su_boc_so_vietlott.csv",
            mime="text/csv"
        )
    with col_h2:
        if st.button("🗑️ Xóa sạch lịch sử"):
            st.session_state.history = []
            st.rerun()
else:
    st.info("Chưa có lượt bốc số nào. Hãy bấm nút **'🎲 BỐC SỐ MAY MẮN'** ở trên để bắt đầu lưu lịch sử!")
