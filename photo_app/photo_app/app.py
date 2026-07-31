import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Cấu hình thư mục lưu ảnh
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    username = request.form.get('username', '').strip()
    if not username:
        username = 'Anonymous'
    
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        
    files = request.files.getlist('files')
    for file in files:
        if file and file.filename != '':
            file.save(os.path.join(user_folder, file.filename))
            
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    users_data = {}
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for username in os.listdir(app.config['UPLOAD_FOLDER']):
            user_path = os.path.join(app.config['UPLOAD_FOLDER'], username)
            if os.path.isdir(user_path):
                files = [f for f in os.listdir(user_path) if os.path.isfile(os.path.join(user_path, f))]
                if files:  # Chỉ hiển thị người đăng nếu có ít nhất 1 ảnh
                    users_data[username] = files
    return render_template('admin.html', users_data=users_data)

@app.route('/uploads/<username>/<filename>')
def send_image(username, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], username), filename)

@app.route('/delete/<username>/<filename>', methods=['POST'])
def delete_file(username, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], username, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
