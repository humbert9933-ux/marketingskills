import streamlit as st
import os
import google.generativeai as genai
import urllib.parse

# --- CONFIGURACIÓN VISUAL (Estética Industrial/Premium) ---
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
    .stCheckbox { color: #BB86FC; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ CENTRAL MULTIMEDIA")

# --- CONEXIÓN A GEMINI ---
# Asegúrate de tener la variable GEMINI_API_KEY en Render
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# --- RADAR DE AGENTES (.md) ---
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
    st.error("⚠️ No se encontraron agentes en el repositorio.")
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        seleccion = st.selectbox("Elegir Especialista:", nombres_habilidades)
    with col2:
        generar_img = st.checkbox("¿Imagen?", value=True)

    contexto = st.text_area("Detalles de la campaña:", height=150, 
                            placeholder="Ej: Llantas Maxell para camiones, enfoque en durabilidad...")

    if st.button("GENERAR CONTENIDO COMPLETO"):
        if not API_KEY:
            st.error("❌ Falta GEMINI_API_KEY en Render.")
        elif contexto and seleccion:
            try:
                # Leer el archivo del agente seleccionado
                with open(habilidades_dict[seleccion], "r", encoding="utf-8") as f:
                    system_prompt = f.read()

                # Inyectar instrucción de imagen si aplica
                if generar_img:
                    system_prompt += "\n\nIMPORTANTE: Al final, añade 'PROMPT_IMAGEN:' seguido de una descripción detallada en INGLÉS para una imagen publicitaria profesional (sin texto, 4k, cinematográfica)."

                # LLAMADA CORREGIDA A GEMINI 1.5 FLASH
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_prompt
                )
                
                with st.spinner(f"El {seleccion} está trabajando..."):
                    # Forzamos la generación simple para evitar errores de v1beta
                    response = model.generate_content(contexto)
                    full_text = response.text

                # Procesar Texto e Imagen
                if "PROMPT_IMAGEN:" in full_text:
                    partes = full_text.split("PROMPT_IMAGEN:")
                    st.markdown("---")
                    st.markdown(partes[0])
                    
                    # Generar visualización
                    prompt_img = partes[1].strip()
                    prompt_encoded = urllib.parse.quote(prompt_img)
                    url_final = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux&seed=42"
                    
                    st.subheader("🖼️ Propuesta Visual:")
                    st.image(url_final, caption="Sugerencia de la IA para tu anuncio", use_container_width=True)
                else:
                    st.markdown("---")
                    st.markdown(full_text)
                    
            except Exception as e:
                st.error(f"Hubo un problema: {e}")
