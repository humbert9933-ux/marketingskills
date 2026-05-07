import streamlit as st
import os
from openai import OpenAI

# Configuración Visual (Estética Premium e Industrial)
st.set_page_config(page_title="Marketing Agents Central", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #E0E0E0; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1E1E1E; border-color: #333; }
    .stTextArea textarea { background-color: #1E1E1E; color: #E0E0E0; border: 1px solid #333; }
    .stButton>button { 
        width: 100%; background-color: #2D2D2D; color: white; 
        border: 1px solid #444; border-radius: 5px; height: 3em;
    }
    .stButton>button:hover { border-color: #BB86FC; color: #BB86FC; }
    h1 { font-family: 'Helvetica Neue', sans-serif; font-weight: 700; color: #FFFFFF; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ AGENTES ESTRATÉGICOS")

# Conexión a DeepSeek
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# Localizar habilidades en la estructura del fork
# La carpeta original suele ser 'skills'
base_path = "skills"
if not os.path.exists(base_path):
    base_path = "habilidades" # Por si se renombró al importar

if os.path.exists(base_path):
    habilidades = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    habilidades.sort()
else:
    habilidades = []
    st.error("No se encontró la carpeta de habilidades.")

# Interfaz de Usuario
seleccion = st.selectbox("Elegir Especialista:", habilidades)
contexto = st.text_area("Detalles de la campaña o producto:", height=150, 
                        placeholder="Ej: Llantas Maxell para camiones, enfoque en durabilidad y carga pesada...")

if st.button("GENERAR ESTRATEGIA"):
    if not API_KEY:
        st.error("Falta la API Key de DeepSeek en la configuración.")
    elif contexto and seleccion:
        # Ruta al archivo SKILL.md dentro de la carpeta de la habilidad
        path_prompt = os.path.join(base_path, seleccion, "SKILL.md")
        
        try:
            with open(path_prompt, "r", encoding="utf-8") as f:
                system_prompt = f.read()

            with st.spinner("DeepSeek procesando..."):
                chat_completion = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": contexto}
                    ],
                    temperature=0.7,
                    stream=False
                )
                
                st.markdown("---")
                st.markdown(chat_completion.choices[0].message.content)
                
        except FileNotFoundError:
            st.error(f"No se encontró el archivo SKILL.md en {seleccion}")
    else:
        st.warning("Completa los campos antes de continuar.")
      
