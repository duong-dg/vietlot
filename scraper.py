import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# URL nguồn dữ liệu kết quả Vietlott (Mega 6/45 & Power 6/55)
# Bạn có thể dùng API công khai hoặc cào từ các trang cập nhật kết quả uy tín
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

FILE_PATH = "vietlott_history.json"

def load_local_data():
    """Đọc dữ liệu lịch sử hiện có từ file JSON."""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"mega645": [], "power655": []}
    return {"mega645": [], "power655": []}

def save_local_data(data):
    """Lưu dữ liệu mới vào file JSON."""
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("✅ Đã cập nhật và lưu dữ liệu thành công vào vietlott_history.json!")

def fetch_latest_mega645():
    """
    Hàm mô phỏng/cào dữ liệu kết quả Mega 6/45 gần nhất.
    Trong thực tế, bạn gửi request đến URL chứa bảng kết quả.
    """
    url = "https://xoso.com.vn/vietlott/mega-6-45.html" # Ví dụ trang nguồn
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # --- Đoạn logic bóc tách HTML (Tùy thuộc vào cấu trúc DOM của trang web nguồn) ---
            # Ví dụ giả định bóc tách danh sách bóng:
            # numbers = [int(ball.text) for ball in soup.find_all("span", class_="ball")[:6]]
            
            # Giả lập kết quả thu thập được từ Web Scraping chuẩn xác:
            latest_draw = {
                "draw_id": "01250",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "numbers": [5, 12, 23, 31, 38, 42]
            }
            return latest_draw
    except Exception as e:
        print(f"⚠️ Lỗi khi cào dữ liệu Mega 6/45: {e}")
    return None

def update_database():
    """Hàm điều phối kiểm tra và cập nhật dữ liệu mới nếu chưa có."""
    data = load_local_data()
    latest_mega = fetch_latest_mega645()
    
    if latest_mega:
        # Kiểm tra xem kỳ quay này đã tồn tại trong lịch sử chưa
        existing_ids = [item["draw_id"] for item in data.get("mega645", [])]
        if latest_mega["draw_id"] not in existing_ids:
            data["mega645"].insert(0, latest_mega)  # Thêm vào đầu danh sách
            save_local_data(data)
        else:
            print("ℹ️ Dữ liệu kỳ quay mới nhất đã tồn tại, không cần thêm.")

if __name__ == "__main__":
    print("🔄 Đang tiến hành cào dữ liệu Vietlott mới nhất...")
    update_database()
