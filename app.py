import streamlit as st
import os
import google.generativeai as genai

# Configuración Visual
st.set_page_config(page_title="Central de Agentes", layout="centered")

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

# Conexión a Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# --- RADAR INTELIGENTE DE HABILIDADES ---
habilidades_dict = {}
carpetas_a_revisar = ["skills", "habilidades", "."] 

for carpeta in carpetas_a_revisar:
    if os.path.exists(carpeta) and os.path.isdir(carpeta):
        for elemento in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, elemento)
            
            # Archivos sueltos .md
            if os.path.isfile(ruta_completa) and elemento.endswith('.md') and elemento.lower() not in ['readme.md', 'requirements.txt', 'app.py']:
                nombre = elemento.replace('.md', '')
                if nombre not in habilidades_dict:
                    habilidades_dict[nombre] = ruta_completa
                    
            # Carpetas del Fork con SKILL.md
            elif os.path.isdir(ruta_completa):
                ruta_skill = os.path.join(ruta_completa, "SKILL.md")
                if os.path.exists(ruta_skill):
                    if elemento not in habilidades_dict:
                        habilidades_dict[elemento] = ruta_skill

nombres_habilidades = list(habilidades_dict.keys())
nombres_habilidades.sort()

# Interfaz de Usuario
if not nombres_habilidades:
    st.error("Buscando agentes... Asegúrate de tener archivos .md en tu repositorio.")
else:
    seleccion = st.selectbox("Elegir Especialista:", nombres_habilidades)
    contexto = st.text_area("Detalles de la campaña o producto:", height=150, 
                            placeholder="Ej: Llantas Maxell para camiones...")

    if st.button("GENERAR ESTRATEGIA"):
        if not API_KEY:
            st.error("Falta la API Key de Gemini en Render (GEMINI_API_KEY).")
        elif contexto and seleccion:
            path_prompt = habilidades_dict[seleccion] 
            
            try:
                with open(path_prompt, "r", encoding="utf-8") as f:
                    system_prompt = f.read()

                with st.spinner(f"Gemini procesando con {seleccion}..."):
                    # Inicializar modelo de Gemini con las instrucciones del agente
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=system_prompt
                    )
                    
                    # Generar respuesta
                    response = model.generate_content(
                        contexto,
                        generation_config=genai.types.GenerationConfig(temperature=0.7)
                    )
                    
                    st.markdown("---")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Error en la generación: {e}")
        else:
            st.warning("Completa los campos antes de continuar.")
