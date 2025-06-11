import streamlit as st
import requests

st.set_page_config(page_title="Job Recommender + CV Feedback", layout="wide")

tab1, tab2 = st.tabs(["📌 Rekomendasi Pekerjaan", "🧠 Feedback CV"])

# ----- Tab 1: Rekomendasi Pekerjaan -----
with tab1:
    st.title("📌 Sistem Rekomendasi Pekerjaan")

    with st.form("job_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            ability = st.text_input("Kemampuan (Ability)")
        with col2:
            skill = st.text_input("Keahlian (Skill)")
        with col3:
            program = st.text_input("Program/Tools")

        submitted = st.form_submit_button("Dapatkan Rekomendasi")

    if submitted:
        payload = {
            "ability": [ability],
            "skill": [skill],
            "program": [program]
        }

        try:
            response = requests.post("http://127.0.0.1:5000/recommend", json=payload)
            response.raise_for_status()
            results = response.json()

            st.success("Top 5 Rekomendasi:")
            for idx, item in enumerate(results[0]["recommendation"], start=1):
                st.markdown(f"**{idx}. {item['title']}** - Skor: {item['score']}%")

        except requests.exceptions.RequestException as e:
            st.error(f"Terjadi kesalahan: {e}")

# ----- Tab 2: Feedback CV Otomatis -----
with tab2:
    st.title("🧠 Evaluasi & Feedback CV Otomatis")

    cv_text = st.text_area("Masukkan isi CV Anda:", height=300)

    if st.button("Dapatkan Feedback CV"):
        if cv_text.strip():
            try:
                response = requests.post("http://127.0.0.1:8000/feedback", json={"cv_text": cv_text})
                response.raise_for_status()
                feedback = response.json().get("feedback", "")
                st.success("Berikut hasil feedback:")
                st.write(feedback)
            except requests.exceptions.RequestException as e:
                st.error(f"Gagal mendapatkan feedback: {e}")
        else:
            st.warning("Mohon isi CV terlebih dahulu.")
