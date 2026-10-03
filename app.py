import streamlit as st
import json
import os

@st.cache_data
def load_vietlott_dataset():
    """Nạp dữ liệu lịch sử và lưu vào cache để app chạy siêu nhanh."""
    if os.path.exists("vietlott_history.json"):
        with open("vietlott_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mega645": [], "power655": []}

dataset = load_vietlott_dataset()

# Thống kê nhanh trên giao diện Streamlit
st.sidebar.subheader("📊 Dữ liệu lịch sử")
mega_count = len(dataset.get("mega645", []))
st.sidebar.write(f"• Số kỳ Mega 6/45 đã lưu: **{mega_count}** kỳ")

# Kiểm tra bộ số vừa bốc có trùng 100% với lịch sử Jackpot nào không
def check_historical_jackpot(selected_numbers, game_key="mega645"):
    history = dataset.get(game_key, [])
    selected_set = set(selected_numbers)
    
    for draw in history:
        if set(draw["numbers"]) == selected_set:
            return True, draw["draw_id"], draw["date"]
    return False, None, None
