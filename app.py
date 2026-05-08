import streamlit as st
import os
import google.generativeai as genai
import urllib.parse

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Central Multimedia IA", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #E0E0E0; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1E1E1E; border-color: #333; }
    .stTextArea textarea { background-color: #1E1E1E; color: #E0E0E0; border: 1px solid #333; }
    .stButton>button { 
        width: 100%; background-color: #2D2D2D; color: white; 
        border: 1px solid #444; border-radius: 5px; height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover { border-color: #BB86FC; color: #BB86FC; }
    h1 { font-family: 'Helvetica Neue', sans-serif; font-weight: 700; color: #FFFFFF; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ CENTRAL MULTIMEDIA")

# --- CONEXIÓN A GEMINI (FORZANDO V1) ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    # Esta línea es el truco para eliminar el error 404
    os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
    genai.configure(api_key=API_KEY)

# --- RADAR DE AGENTES ---
habilidades_dict = {}
carpetas = ["skills", "habilidades", "."] 

for carpeta in carpetas:
    if os.path.exists(carpeta) and os.path.isdir(carpeta):
        for elemento in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, elemento)
            if os.path.isfile(ruta_completa) and elemento.endswith('.md') and elemento.lower() not in ['readme.md', 'requirements.txt', 'app.py']:
                nombre = elemento.replace('.md', '')
                if nombre not in habilidades_dict:
                    habilidades_dict[nombre] = ruta_completa
            elif os.path.isdir(ruta_completa):
                ruta_skill = os.path.join(ruta_completa, "SKILL.md")
                if os.path.exists(ruta_skill):
                    if elemento not in habilidades_dict:
                        habilidades_dict[elemento] = ruta_skill

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

    if st.button("GENERAR CONTENIDO COMPLETO"):
        if not API_KEY:
            st.error("❌ Configura GEMINI_API_KEY en Render.")
        elif contexto and seleccion:
            try:
                with open(habilidades_dict[seleccion], "r", encoding="utf-8") as f:
                    system_prompt = f.read()

                if generar_img:
                    system_prompt += "\n\nIMPORTANTE: Al final añade 'PROMPT_IMAGEN:' y un prompt en inglés para una imagen publicitaria 4k."

                # Cambiamos a la versión de modelo que Render sí encuentra
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash-latest", # Añadimos '-latest' para forzar búsqueda
                    system_instruction=system_prompt
                )
                
                with st.spinner("Generando contenido..."):
                    response = model.generate_content(contexto)
                    full_text = response.text

                if "PROMPT_IMAGEN:" in full_text:
                    partes = full_text.split("PROMPT_IMAGEN:")
                    st.markdown("---")
                    st.markdown(partes[0])
                    
                    prompt_encoded = urllib.parse.quote(partes[1].strip())
                    url_final = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux"
                    
                    st.subheader("🖼️ Propuesta Visual:")
                    st.image(url_final, use_container_width=True)
                else:
                    st.markdown("---")
                    st.markdown(full_text)
                    
            except Exception as e:
                # Si el error persiste, probamos con el nombre alternativo del modelo
                st.info("Reintentando conexión estable...")
                try:
                    model_alt = genai.GenerativeModel('gemini-1.5-flash')
                    response = model_alt.generate_content(f"Instrucción: {system_prompt}\n\nTarea: {contexto}")
                    st.markdown(response.text)
                except:
                    st.error(f"Error crítico: {e}")
