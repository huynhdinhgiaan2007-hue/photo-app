import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

# === ĐIỀN THÔNG TIN CLOUDINARY CỦA BẠN VÀO ĐÂY ==
cloudinary.config( 
  cloud_name = "xz9idpxr", 
  api_key = "488942164463563", 
  api_secret = "s43bwIwBiEvq1X9tsLecHl4VsRc",
  secure = True
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # Cho phép gửi file cực lớn (1GB)

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
        
    files = request.files.getlist('files') or request.files.getlist('file')
    for file in files:
        if file and file.filename != '':
            # Đẩy ảnh thẳng lên Cloudinary vào thư mục của username
            cloudinary.uploader.upload(
                file, 
                folder=f"war_app/{username}",
                public_id=os.path.splitext(file.filename)[0]
            )
            
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    users_data = {}
    try:
        # Quét toàn bộ ảnh đã lưu trên Cloudinary
        result = cloudinary.api.resources(
            type="upload",
            prefix="war_app/",
            max_results=500
        )
        
        for resource in result.get('resources', []):
            folder_parts = resource['public_id'].split('/')
            if len(folder_parts) >= 3:
                username = folder_parts[1]
                image_url = resource['secure_url']
                public_id = resource['public_id']
                
                if username not in users_data:
                    users_data[username] = []
                users_data[username].append({
                    'url': image_url,
                    'public_id': public_id
                })
    except Exception as e:
        print(f"Lỗi Cloudinary Admin: {e}")
        
    return render_template('admin.html', users_data=users_data)

@app.route('/delete', methods=['POST'])
def delete_file():
    public_id = request.form.get('public_id')
    if public_id:
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"Lỗi xóa ảnh: {e}")
    return redirect(url_for('admin'))

@app.route('/war.jpg')
def serve_logo():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'war.jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
