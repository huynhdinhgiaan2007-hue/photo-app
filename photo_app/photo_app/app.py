import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        user_name = request.form.get('username', '').strip()
        file = request.files.get('file')

        if not user_name:
            message = "Vui lòng nhập tên của bạn!"
        elif not file or file.filename == '':
            message = "Vui lòng chọn một bức ảnh!"
        elif file and allowed_file(file.filename):
            safe_user_folder = secure_filename(user_name) or "anonymous"
            user_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_user_folder)
            os.makedirs(user_path, exist_ok=True)

            filename = secure_filename(file.filename)
            file.save(os.path.join(user_path, filename))
            message = f"Tải ảnh thành công cho tài khoản '{user_name}'!"
        else:
            message = "Định dạng file không hợp lệ!"

    return render_template('index.html', message=message)

@app.route('/admin')
def admin():
    users_data = {}
    if os.path.exists(UPLOAD_FOLDER):
        for user_folder in os.listdir(UPLOAD_FOLDER):
            folder_path = os.path.join(UPLOAD_FOLDER, user_folder)
            if os.path.isdir(folder_path):
                files = os.listdir(folder_path)
                users_data[user_folder] = files
    return render_template('admin.html', users_data=users_data)

@app.route('/uploads/<username>/<filename>')
def send_image(username, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], username), filename)

if __name__ == '__main__':
    import os
from flask import redirect, url_for

@app.route('/delete/<folder_name>/<filename>', methods=['POST'])
def delete_file(folder_name, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('admin'))
    app.run(debug=True, port=5000)
