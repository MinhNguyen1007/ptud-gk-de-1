# Họ và tên: Nguyễn Tấn Minh
# MSSV: 22643511
# Số thứ tự: 80


# Blog Application

Ứng dụng blog được xây dựng bằng Flask, cho phép người dùng đăng bài, bình luận và quản lý nội dung với hệ thống phân quyền.

# Ý tưởng:

Tạo trang blog với giao diện chung để xem cái bài viết có thể comment khi có tài khoản

Trang đăng ký sẽ tạo tài khoản cho người dùng

Khi đăng ký xong tài khoản đó mặc định là viewer

Người đăng bài sẽ là author (tức là user bất kì đăng bài thì user đó là author của bài blog đó, vì là tác giả cảu bài đăng nên họ có khả năng xóa hoặc edit bài của họ trong phần read more)

User được quyền đăng bài, comment

Các tài khoản có 3 loại và có vai trò khác nhau: 
    - Viewer: view only 
    - Collaborator: can edit, can’t delelte 
    - Editor: view, edit, delete permission 

Nếu muốn đổi thành các loại user khác buộc phải thông qua ADMIN để có được vai trò đó

Tài khoản ADMIN mặc định:
- Tên tài khoản: admin
- Mật khẩu: admin

ADMIN có chức năng quản lý các user, bài viết, comment, đổi vai trò user thành các loại khác, khóa account, reset mật khẩu, edit hoặc xóa bài viết

Về phần random, do chưa nắm rõ yêu cầu nên ý tưởng ở đây là tải các ảnh đã random về và lưu trong static để lấy các ảnh đó để đăng ảnh chứ không phải mở link ra sẽ hiển thị các ảnh tự random sẵn

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
