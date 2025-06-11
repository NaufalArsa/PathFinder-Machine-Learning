from flask import Flask, request, jsonify
import pandas as pd

from extract import extract_resume_features
from predict import predict

app = Flask(__name__)

@app.route('/process-resume', methods=['POST'])
def process_resume():
    try:
        extracted_data = []
        df_result = pd.DataFrame()

        # Retrieve resume string from JSON
        data = request.get_json()
        if not data or "resume" not in data:
            return jsonify({"error": "No resume text provided"}), 400

        resume_text = data.get("resume")
        if not isinstance(resume_text, str) or not resume_text.strip():
            return jsonify({"error": "Invalid resume format"}), 400

        # Extract resume features
        try:
            extracted = extract_resume_features(resume_text)
            if not extracted:
                return jsonify({"error": "Failed to extract resume features"}), 500
        except Exception as e:
            return jsonify({"error": f"Resume extraction error: {e}"}), 500

        extracted_data.append(extracted)

        # Convert extracted data to DataFrame
        try:
            df_extract = pd.DataFrame(extracted_data)
            print(df_extract.head())
        except Exception as e:
            return jsonify({"error": f"Error converting extracted data to DataFrame: {e}"}), 500

        # Predict job recommendations
        try:
            df_result = pd.DataFrame(predict(df_extract))
        except Exception as e:
            return jsonify({"error": f"Prediction process failed: {e}"}), 500

        # Return JSON results
        return jsonify(df_result.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
