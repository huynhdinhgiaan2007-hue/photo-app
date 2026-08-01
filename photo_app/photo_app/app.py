import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Cấu hình dung lượng tối đa cho 1 lần tải lên: 1 GB (1024 MB)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return process_upload()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    return process_upload()

def process_upload():
    username = request.form.get('username', '').strip()
    if not username:
        username = 'Anonymous'
    
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        
    # Nhận toàn bộ danh sách file được tải lên
    files = request.files.getlist('files') or request.files.getlist('file')
    for file in files:
        if file and file.filename != '':
            file.save(os.path.join(user_folder, file.filename))
            
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    users_data = {}
    try:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for username in os.listdir(app.config['UPLOAD_FOLDER']):
                user_path = os.path.join(app.config['UPLOAD_FOLDER'], username)
                if os.path.isdir(user_path):
                    files = [f for f in os.listdir(user_path) if os.path.isfile(os.path.join(user_path, f))]
                    if files:
                        users_data[username] = files
    except Exception as e:
        print(f"Lỗi trong admin: {e}")
        
    return render_template('admin.html', users_data=users_data)

@app.route('/war.jpg')
def serve_logo():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'war.jpg')

@app.route('/uploads/<username>/<filename>')
def send_image(username, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], username), filename)

@app.route('/delete/<username>/<filename>', methods=['POST'])
def delete_file(username, filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], username, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Lỗi xóa file: {e}")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
