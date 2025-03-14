from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Post, Comment
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime

# Cấu hình upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Tạo thư mục uploads nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Khởi tạo database
db.init_app(app)

# Khởi tạo Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorator để kiểm tra quyền admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Kiểm tra xác nhận mật khẩu
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        # Kiểm tra username đã tồn tại chưa
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))

        # Kiểm tra email đã tồn tại chưa
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('register'))

        # Tạo user mới với role mặc định là viewer
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='viewer',  # Mặc định là viewer
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now login.')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/post/new', methods=['GET', 'POST'])
@login_required  # Chỉ cần đăng nhập là có thể đăng bài
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        # Xử lý file ảnh
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"

        post = Post(
            title=title,
            content=content,
            image_path=image_path,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!')
        return redirect(url_for('home'))
    
    return render_template('create_post.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form['content']
    post = Post.query.get_or_404(post_id)
    comment = Comment(content=content, author=current_user, post=post)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    posts = Post.query.all()
    return render_template('admin/dashboard.html', users=users, posts=posts)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.role == 'admin':
        abort(403)
    users = User.query.filter(User.role != 'admin').all()  # Không hiển thị các admin
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin user')
        return redirect(url_for('admin_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('admin_users'))

@app.route('/admin/posts')
@admin_required
def admin_posts():
    posts = Post.query.all()
    return render_template('admin/posts.html', posts=posts)

@app.route('/admin/post/<int:post_id>/delete')
@login_required
@admin_required
def admin_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully')
    return redirect(url_for('admin_posts'))

@app.route('/admin/comments')
@admin_required
def admin_comments():
    comments = Comment.query.all()
    return render_template('admin/comments.html', comments=comments)

@app.route('/admin/comments/delete/<int:comment_id>')
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully')
    return redirect(url_for('admin_comments'))

# Thêm route để tạo admin (chỉ chạy một lần khi setup)
@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    if User.query.filter_by(role='admin').first():
        flash('Admin already exists')
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        admin = User(username=username, email=email, password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        flash('Admin created successfully')
        return redirect(url_for('login'))
    return render_template('create_admin.html')

@app.route('/reset-db')
def reset_db():
    init_db()
    return 'Database has been reset!'

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Kiểm tra quyền chỉnh sửa: tác giả hoặc người có quyền edit
    if not (current_user == post.author or current_user.role in ['editor', 'collaborator', 'admin']):
        abort(403)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.image_path = f"uploads/{filename}"
        
        db.session.commit()
        flash('Post has been updated!')
        return redirect(url_for('post_detail', post_id=post.id))
    
    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Kiểm tra quyền xóa: tác giả hoặc người có quyền delete
    if not (current_user == post.author or current_user.role in ['editor', 'admin']):
        abort(403)
    
    try:
        db.session.delete(post)  # Sẽ tự động xóa các comment liên quan
        db.session.commit()
        flash('Post has been deleted!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the post.')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('home'))

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # Không cho phép thay đổi role của admin khác
        if user.role == 'admin' and user != current_user:
            flash('Cannot modify other admin accounts')
            return redirect(url_for('admin_users'))
            
        user.role = request.form['role']
        user.is_active = 'is_active' in request.form
        db.session.commit()
        flash(f'User {user.username} has been updated')
        return redirect(url_for('admin_users'))
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/user/<int:user_id>/toggle_status')
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin' and user != current_user:
        flash('Cannot modify other admin accounts')
        return redirect(url_for('admin_users'))
        
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/reset_password')
@login_required
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin' and user != current_user:
        flash('Cannot modify other admin accounts')
        return redirect(url_for('admin_users'))
        
    # Reset password to "password123"
    user.password = generate_password_hash('password123')
    db.session.commit()
    flash(f'Password for {user.username} has been reset to: password123')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
def change_user_role(user_id):
    if not current_user.role == 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Không cho phép thay đổi role của admin
    if user.role == 'admin':
        flash('Cannot modify admin roles', 'error')
        return redirect(url_for('admin_users'))
    
    new_role = request.form.get('role')
    if new_role in ['viewer', 'collaborator', 'editor']:  # Chỉ cho phép đổi thành các role này
        user.role = new_role
        db.session.commit()
        flash(f'Role updated for user {user.username}')
    
    return redirect(url_for('admin_users'))

def init_db():
    with app.app_context():
        # Xóa tất cả bảng cũ
        db.drop_all()
        # Tạo lại tất cả bảng mới
        db.create_all()
        
        # Tạo tài khoản admin
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Database initialized and admin account created!')

if __name__ == '__main__':
    app.run(debug=True) 