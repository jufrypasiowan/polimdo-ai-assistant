import os
import streamlit as st
from google import genai
from google.genai import types
from polimdo_scraper import search_polimdo_data

st.set_page_config(page_title="Polimdo AI: Smart Campus Assistant", page_icon="🏫", layout="wide")

st.title("🏫 Polimdo AI: Smart Campus Assistant")
st.caption("Asisten Informasi Akademik & Layanan Mahasiswa Politeknik Negeri Manado")

with st.sidebar:
    st.header("⚙️ Parameter Informasi")
    api_key = st.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    gaya_bahasa = st.selectbox(
        "Gaya Bahasa (Persona)",
        ["Formal & Resmi (Layanan Akademik)", "Santai & Ramah (Kakak Tingkat/Peer)"]
    )
    
    jurusan = st.selectbox(
        "Fokus Jurusan / Domain",
        ["Umum / Informasi Kampus", "Teknik Elektro", "Teknik Sipil", "Teknik Mesin", "Akuntansi", "Administrasi Bisnis", "Pariwisata"]
    )
    
    temperature = st.slider("Tingkat Respon (Temperature)", 0.0, 1.0, 0.3, 0.1)
    use_live_data = st.checkbox("Gunakan Live Search polimdo.ac.id", value=True)
    
    st.divider()
    if st.button("🗑️ Hapus Memori Percakapan"):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.info("🔑 Masukkan Gemini API Key Anda pada sidebar untuk mengaktifkan bot.", icon="🔑")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanyakan info pendaftaran, jadwal kuliah, pengumuman, atau info jurusan Polimdo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    polimdo_context = ""
    retrieved_sources = []
    
    if use_live_data:
        with st.status("🔍 Mencari data terbaru dari polimdo.ac.id...", expanded=False) as status:
            search_results = search_polimdo_data(f"{jurusan} {prompt}")
            if search_results:
                polimdo_context = "\n".join([f"- Judul: {r['title']}\n  Ringkasan: {r['snippet']}\n  Link: {r['link']}" for r in search_results])
                retrieved_sources = search_results
                status.update(label="✅ Data dari polimdo.ac.id berhasil ditemukan!", state="complete")
            else:
                status.update(label="⚠️ Tidak menemukan data spesifik, menggunakan basis pengetahuan umum.", state="complete")

    system_instruction = f"""
    Anda adalah Polimdo AI, asisten cerdas resmi Politeknik Negeri Manado (Polimdo).
    
    Konfigurasi Operasional:
    - Gaya Bahasa: {gaya_bahasa}
    - Fokus Jurusan: {jurusan}
    
    Data Hasil Pencarian dari Website Resmi (polimdo.ac.id):
    ---
    {polimdo_context if polimdo_context else 'Tidak ada data pencarian web langsung.'}
    ---
    
    Aturan Jawaban:
    1. Utamakan penggunaan informasi dari Data Hasil Pencarian jika relevan.
    2. Berikan jawaban yang tepat, informatif, dan membantu.
    3. Jika terdapat link referensi dari data pencarian, cantumkan tautannya.
    """

    contents = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

    with st.chat_message("assistant"):
        with st.spinner("Polimdo AI sedang menyusun jawaban..."):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                )
                
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=contents,
                    config=config
                )
                
                bot_reply = response.text
                st.markdown(bot_reply)
                
                if retrieved_sources:
                    st.divider()
                    st.markdown("**🌐 Sumber Referensi (polimdo.ac.id):**")
                    for src in retrieved_sources:
                        st.markdown(f"- [{src['title']}]({src['link']})")
                
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except Exception as e:
                st.error(f"Gagal memproses respons: {e}")
