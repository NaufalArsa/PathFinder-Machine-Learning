import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained TF-IDF vectorizer and matrix
try:
    vectorizer = joblib.load("./models/tfidf_vectorizer.joblib")
    tfidf_matrix = joblib.load("./models/tfidf_matrix.joblib")
    print("✅ Loaded pre-trained TF-IDF vectorizer and matrix.")
except Exception as e:
    print(f"❌ Error loading TF-IDF models: {e}")
    raise

# Load the dataset used to train TF-IDF
df_ready = pd.read_csv("./dataset/job_reference_data.csv")

def preprocess_data(df_clean):
    """Vectorize resume data using the pre-trained TF-IDF model."""
    try:
        df_clean["combined_text"] = df_clean["ability"] + " " + df_clean["skill"] + " " + df_clean["program"]
        return vectorizer.transform(df_clean["combined_text"])
    except Exception as e:
        print(f"❌ Error during vectorization: {e}")
        raise

def predict(df_clean, output_csv="./dataset/resume_output.csv", top_n=3):
    """Find top N job recommendations based on resume similarity."""
    try:
        new_tfidf = preprocess_data(df_clean)
        cosine_similarities = cosine_similarity(new_tfidf, tfidf_matrix)

        results = []

        for i, sims in enumerate(cosine_similarities):
            top_indices = sims.argsort()[-top_n:][::-1]
            for idx in top_indices:
                if idx < len(df_ready):  # Ensure index is valid
                    matched_title = df_ready.iloc[idx]["title"]  # Retrieve job title from original dataset
                else:
                    matched_title = "Unknown"
                
                similarity = sims[idx] * 100
                similarity_score = round(similarity, 2)

                # Ensure minimum score threshold (e.g., avoid showing "0.0%" if near zero)
                if similarity_score < 1:
                    similarity_score = "<1%"  # Handle extremely low scores gracefully

                results.append({
                    "cv_index": i + 1,
                    "recommended_job_title": matched_title,
                    "similarity_score": f"{similarity_score}%"
                })

        df_results = pd.DataFrame(results)
        df_results.to_csv(output_csv, index=False)
        print(f"\n✅ Predictions saved to: {output_csv}")

        return df_results
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        raise
