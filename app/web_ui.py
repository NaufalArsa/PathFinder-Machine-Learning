# streamlit_ui.py
import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("Rekomendasi Pekerjaan berdasarkan CV")

st.markdown("## Masukkan Data CV dan Lihat Rekomendasi")

# Layout: dua kolom, kiri untuk input, kanan untuk hasil
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Form Input CV")
    num_cv = st.number_input("Jumlah CV yang ingin dicek:", min_value=1, max_value=10, value=1, step=1)

    abilities = []
    skills = []
    programs = []

    for i in range(num_cv):
        st.markdown(f"#### CV #{i+1}")
        ability = st.text_input(f"Kemampuan (Ability) CV #{i+1}", key=f"ability_{i}")
        skill = st.text_input(f"Skill CV #{i+1}", key=f"skill_{i}")
        program = st.text_input(f"Program/Tools CV #{i+1}", key=f"program_{i}")
        
        abilities.append(ability)
        skills.append(skill)
        programs.append(program)

    if st.button("Dapatkan Rekomendasi"):
        payload = {
            "ability": abilities,
            "skill": skills,
            "program": programs
        }

        try:
            response = requests.post("http://127.0.0.1:5000/recommend", json=payload)
            if response.status_code == 200:
                results = response.json()

                with col2:
                    st.markdown("## Hasil Rekomendasi")
                    for result in results:
                        st.markdown(f"### CV #{result['cv_index'] + 1}")
                        for rec in result['recommendation']:
                            st.markdown(f"- **{rec['title']}** (Skor: {rec['score']}%)")
            else:
                st.error(f"Gagal: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Gagal terhubung ke server Flask. Pastikan Flask berjalan di http://127.0.0.1:5000")
