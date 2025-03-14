# Họ và tên: Nguyễn Tấn Minh
# MSSV: 22643511
# Số thứ tự: 80


# Blog Application

Ứng dụng blog được xây dựng bằng Flask, cho phép người dùng đăng bài, bình luận và quản lý nội dung với hệ thống phân quyền.

## Cài đặt (PowerShell)

1. Clone repository:
```powershell
git clone https://github.com/MinhNguyen1007/ptud-gk-de-1.git
cd ptud-gk-de-1
```

2. Tạo môi trường ảo và kích hoạt:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Nếu gặp lỗi về Execution Policy, chạy lệnh sau với quyền Administrator:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Cài đặt các thư viện cần thiết:
```powershell
pip install -r requirements.txt
```

4. Khởi tạo database:
```powershell
python reset_db.py
```

5. Chạy ứng dụng:
```powershell
python app.py
```

## Cấu trúc thư mục
