from flask import Flask, request, jsonify
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = joblib.load('tfidf_vectorizer.joblib')
tfidf_matrix = joblib.load('tfidf_matrix.joblib')
df_ready = pd.read_csv('job_reference_data.csv')

app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    
    abilities = data.get('ability', [])
    skills = data.get('skill', [])
    programs = data.get('program', [])
    
    if not (len(abilities) == len(skills) == len(programs)):
        return jsonify({'error': 'Panjang ability, skill, dan program harus sama'}), 400
        # tujuannya supaya semisal ada banyak CV yang mau di prediksi maka bisa langsung banyak, tapi yaa usahakan semua kolom ada isinya
    
    new_texts = [
        ability + '' + skill + '' + program
        for ability, skill, program in zip(abilities, skills, programs)
    ]
    
    new_tfidf = vectorizer.transform(new_texts)
    similarities = cosine_similarity(new_tfidf, tfidf_matrix)
    
    top_n = 5
    results = []
    
    for i, sims in enumerate(similarities):
        top_indices = sims.argsort()[-top_n:][::-1]
        recommended = [
            {
                'title': df_ready.iloc[idx]['title'],
                'score': round(sims[idx] * 100, 2)
            }
            for idx in top_indices
        ]
        results.append({
            'cv_index': i,
            'recommendation': recommended
        })
        
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
