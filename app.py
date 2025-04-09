import io
import os
import traceback
from flask import Flask, request, send_file, jsonify

# Không cần import 'remove' ở đây nếu bạn muốn lazy load model
# Hoặc import bình thường nếu muốn load ngay khi app khởi động
from rembg import remove

app = Flask(__name__)

# Nên chọn model nhẹ để tiết kiệm tài nguyên trên Railway
REM BG_MODEL = os.environ.get("REMBG_MODEL", "u2netp")

# Route kiểm tra sức khỏe (health check) mà Railway có thể dùng
@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Rembg API is running!", "model_used": REMBG_MODEL})

@app.route('/remove', methods=['POST'])
def remove_bg_api():
    if 'file' not in request.files:
        return jsonify({"error": "Missing 'file' part in form-data"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            input_data = file.read()
            print(f"Processing file: {file.filename}, size: {len(input_data)} bytes, using model: {REM BG_MODEL}")

            # --- Xử lý xóa nền ---
            output_data = remove(input_data, model_name=REM BG_MODEL)
            # --------------------

            print(f"Successfully removed background for: {file.filename}")

            return send_file(
                io.BytesIO(output_data),
                mimetype='image/png'
            )

        except Exception as e:
            error_message = f"Error processing image: {str(e)}"
            print(error_message)
            traceback.print_exc() # In đầy đủ lỗi ra log của Railway để debug
            return jsonify({"error": error_message}), 500
    else:
        # Trường hợp này ít khi xảy ra
        return jsonify({"error": "Invalid file object"}), 400

# Block này chỉ chạy khi bạn chạy file trực tiếp (python app.py)
# Khi deploy trên Railway bằng Gunicorn, nó sẽ không chạy
if __name__ == '__main__':
    # Railway sẽ cung cấp PORT qua biến môi trường
    port = int(os.environ.get("PORT", 8080))
    # Chạy debug nội bộ
    app.run(debug=True, host='0.0.0.0', port=port)