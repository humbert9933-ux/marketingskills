import streamlit as st
import os
from groq import Groq
import urllib.parse
import re

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Central Multimedia IA", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #E0E0E0; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1E1E1E; border-color: #333; }
    .stTextArea textarea { background-color: #1E1E1E; color: #E0E0E0; border: 1px solid #333; }
    .stButton>button { 
        width: 100%; background-color: #2D2D2D; color: white; 
        border: 1px solid #444; border-radius: 5px; height: 3em; font-weight: bold;
    }
    .stButton>button:hover { border-color: #BB86FC; color: #BB86FC; }
    h1 { font-family: 'Helvetica Neue', sans-serif; font-weight: 700; color: #FFFFFF; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 CENTRAL MULTIMEDIA (NANO-OPTIMIZED)")

# --- CONEXIÓN A GROQ ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- RADAR DE AGENTES ---
habilidades_dict = {}
carpetas = ["skills", "habilidades", "."] 
for carpeta in carpetas:
    if os.path.exists(carpeta) and os.path.isdir(carpeta):
        for elemento in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, elemento)
            if os.path.isfile(ruta_completa) and elemento.endswith('.md') and elemento.lower() not in ['readme.md', 'requirements.txt', 'app.py']:
                habilidades_dict[elemento.replace('.md', '')] = ruta_completa
            elif os.path.isdir(ruta_completa):
                ruta_skill = os.path.join(ruta_completa, "SKILL.md")
                if os.path.exists(ruta_skill): habilidades_dict[elemento] = ruta_skill

nombres_habilidades = sorted(list(habilidades_dict.keys()))

# --- INTERFAZ ---
if not nombres_habilidades:
    st.error("⚠️ No se encontraron agentes.")
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        seleccion = st.selectbox("Elegir Especialista:", nombres_habilidades)
    with col2:
        generar_img = st.checkbox("¿Imagen?", value=True)

    contexto = st.text_area("Detalles de la campaña:", height=150)

    if st.button("GENERAR CONTENIDO"):
        if contexto and seleccion:
            try:
                with open(habilidades_dict[seleccion], "r", encoding="utf-8") as f:
                    agent_instructions = f.read()

                # Aquí es donde Gemini actúa como Director de Arte
                if generar_img:
                    agent_instructions += """
                    \n\nAL FINAL, genera un IMAGE_PROMPT_START: seguido de una descripción cinematográfica en inglés. 
                    Usa este estilo: 'High-end commercial photography, studio lighting, 8k, hyper-realistic, photorealistic'.
                    """

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": agent_instructions}, {"role": "user", "content": contexto}]
                )
                
                full_text = completion.choices[0].message.content
                
                if "IMAGE_PROMPT_START:" in full_text:
                    partes = full_text.split("IMAGE_PROMPT_START:")
                    st.markdown("---")
                    st.markdown(partes[0])
                    
                    # Usamos Pollinations con el modelo FLUX (que es el más parecido al mío)
                    prompt_encoded = urllib.parse.quote(partes[1].strip())
                    url_img = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true"
                    
                    st.image(url_img, caption="Propuesta Visual Generada", use_container_width=True)
                else:
                    st.markdown(full_text)
                    
            except Exception as e:
                st.error(f"Error: {e}")
