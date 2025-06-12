import os
from flask import Flask, request, jsonify
import pandas as pd
import json

from etl_pipeline.extract import extract_resume_features
from etl_pipeline.predict import predict

from etl_pipeline.feedback import feedback

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process-resume', methods=['POST'])
def process_resume():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type. Only .pdf accepted"}), 400

        # Save the uploaded file to ./uploads/
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)

        # Extract and predict
        extracted = extract_resume_features(save_path)
        df_extract = pd.DataFrame([extracted])
        df_result = pd.DataFrame(predict(df_extract))

        # Delete all files in the upload folder
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return jsonify(df_result.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {e}"}), 500
    

@app.route('/review', methods=['POST'])
def review_profile():
    try:
        print("DEBUG: Request received")
        
        if 'file' not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type. Only .pdf accepted"}), 400

        # Save the uploaded file to ./uploads/
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)

        # Extract and predict
        extracted = extract_resume_features(save_path)
        df = pd.DataFrame([extracted])

        print("DEBUG: Extraction result", df.to_dict())

        result = feedback(df.iloc[0])
        print("DEBUG: Type of feedback return", type(result))

        # Delete all files in the upload folder
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return result
        

    except Exception as e:
        return jsonify({"error": f"Review process failed: {e}"}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
