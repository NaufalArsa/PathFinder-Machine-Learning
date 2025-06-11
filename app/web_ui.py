import streamlit as st
import requests

# Untuk membaca file PDF dan DOCX
from PyPDF2 import PdfReader
import docx

# Konfigurasi halaman
st.set_page_config(page_title="Rekomendasi Pekerjaan dari CV", layout="wide")

st.title("🧠 Rekomendasi Pekerjaan dari CV Otomatis")

uploaded_file = st.file_uploader("Unggah file CV Anda (.pdf, .docx, .txt):", type=["pdf", "docx", "txt"])

if st.button("Dapatkan Rekomendasi Pekerjaan"):
    if uploaded_file:
        file_text = ""

        try:
            # Ekstrak isi berdasarkan format file
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                file_text = "\n".join(
                    page.extract_text() for page in reader.pages if page.extract_text()
                )

            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                file_text = "\n".join([para.text for para in doc.paragraphs])

            elif uploaded_file.type == "text/plain":
                file_text = uploaded_file.read().decode("utf-8")

            # Kirim teks ke endpoint Flask
            if file_text.strip():
                with st.spinner("Memproses CV dan mencari rekomendasi..."):
                    response = requests.post(
                        "http://127.0.0.1:5000/process-resume",
                        json={"resume": file_text}
                    )
                    response.raise_for_status()
                    results = response.json()

                # Tampilkan hasil rekomendasi
                if isinstance(results, list) and results:
                    st.success("Berikut adalah rekomendasi pekerjaan berdasarkan CV Anda:")
                    for idx, rec in enumerate(results, start=1):
                        st.markdown(f"**{idx}. {rec['recommended_job_title']}** — Skor: {rec['similarity_score']}")
                else:
                    st.warning("Tidak ada rekomendasi ditemukan.")

            else:
                st.warning("Isi file CV kosong atau tidak terbaca.")

        except Exception as e:
            st.error(f"Gagal memproses file CV: {e}")
    else:
        st.warning("Silakan unggah file CV terlebih dahulu.")
