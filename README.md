# Blog Application

Ứng dụng blog được xây dựng bằng Flask, cho phép người dùng đăng bài, bình luận và quản lý nội dung với hệ thống phân quyền.

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd blog-app
```

2. Tạo môi trường ảo và kích hoạt:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Khởi tạo database:
```bash
python reset_db.py
```

5. Chạy ứng dụng:
```bash
python app.py
```

## Cấu trúc thư mục
