import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained TF-IDF vectorizer and matrix
try:
    vectorizer = joblib.load("Model/tfidf_vectorizer.joblib")
    tfidf_matrix = joblib.load("Model/tfidf_matrix.joblib")
    print("✅ Loaded pre-trained TF-IDF vectorizer and matrix.")
except Exception as e:
    print(f"❌ Error loading TF-IDF models: {e}")
    raise

# Load the dataset used to train TF-IDF
df_ready = pd.read_csv("job_reference_data.csv")

def preprocess_data(df_clean):
    """Vectorize resume data using the pre-trained TF-IDF model."""
    try:
        df_clean["combined_text"] = df_clean["ability"] + " " + df_clean["skill"] + " " + df_clean["program"]
        return vectorizer.transform(df_clean["combined_text"])
    except Exception as e:
        print(f"❌ Error during vectorization: {e}")
        raise

def predict(df_clean, output_csv="predictions.csv", top_n=5):
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

                results.append({
                    "cv_index": i + 1,
                    "recommended_job_title": matched_title,
                    "similarity_score": round(sims[idx] * 100, 2)  # Convert to percentage
                })

        df_results = pd.DataFrame(results)
        df_results.to_csv(output_csv, index=False)
        print(f"\n✅ Predictions saved to: {output_csv}")

        return df_results
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        raise
