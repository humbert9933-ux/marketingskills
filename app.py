import streamlit as st
import os
import google.generativeai as genai
import urllib.parse

# 1. CONFIGURACIÓN VISUAL (Estética Premium e Industrial)
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

# 2. CONEXIÓN A GEMINI
# Asegúrate de que en Render la variable se llame GEMINI_API_KEY
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# 3. RADAR INTELIGENTE DE HABILIDADES
# Escanea carpetas y archivos .md para listar tus agentes
habilidades_dict = {}
carpetas_a_revisar = ["skills", "habilidades", "."] 

for carpeta in carpetas_a_revisar:
    if os.path.exists(carpeta) and os.path.isdir(carpeta):
        for elemento in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, elemento)
            
            # Detecta archivos .md sueltos (como experto-ruby.md)
            if os.path.isfile(ruta_completa) and elemento.endswith('.md') and elemento.lower() not in ['readme.md', 'requirements.txt', 'app.py']:
                nombre = elemento.replace('.md', '')
                if nombre not in habilidades_dict:
                    habilidades_dict[nombre] = ruta_completa
                    
            # Detecta carpetas con archivos SKILL.md (estructura original del fork)
            elif os.path.isdir(ruta_completa):
                ruta_skill = os.path.join(ruta_completa, "SKILL.md")
                if os.path.exists(ruta_skill):
                    if elemento not in habilidades_dict:
                        habilidades_dict[elemento] = ruta_skill

nombres_habilidades = sorted(list(habilidades_dict.keys()))

# 4. INTERFAZ DE USUARIO
if not nombres_habilidades:
    st.error("No se encontraron agentes. Verifica tus archivos .md en GitHub.")
else:
    # Selector de agente y opción de imagen
    col1, col2 = st.columns([3, 1])
    with col1:
        seleccion = st.selectbox("Elegir Especialista:", nombres_habilidades)
    with col2:
        generar_img = st.checkbox("¿Imagen?", value=True)

    contexto = st.text_area("Detalles de la campaña o producto:", height=150, 
                            placeholder="Ej: Llantas Maxell para camiones, enfoque en durabilidad...")

    # 5. LÓGICA DE GENERACIÓN
    if st.button("GENERAR CONTENIDO COMPLETO"):
        if not API_KEY:
            st.error("Falta la API Key de Gemini en la configuración de Render.")
        elif contexto and seleccion:
            path_prompt = habilidades_dict[seleccion] 
            
            try:
                with open(path_prompt, "r", encoding="utf-8") as f:
                    system_prompt = f.read()

                # Instrucción extra para la imagen si el checkbox está activo
                if generar_img:
                    system_prompt += "\n\nIMPORTANTE: Al final de tu respuesta, añade SIEMPRE una sección llamada 'PROMPT_IMAGEN:' seguida de una descripción detallada en INGLÉS para generar una imagen publicitaria profesional de este producto. La descripción debe ser cinematográfica, de alta resolución y sin texto."

                with st.spinner(f"Optimizando con {seleccion}..."):
                    # Uso de gemini-1.5-flash para estabilidad y velocidad
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=system_prompt
                    )
                    
                    response = model.generate_content(
                        contexto,
                        generation_config=genai.types.GenerationConfig(temperature=0.7)
                    )
                    
                    full_response = response.text

                # Separación de Texto e Imagen
                if "PROMPT_IMAGEN:" in full_response:
                    partes = full_response.split("PROMPT_IMAGEN:")
                    texto_marketing = partes[0]
                    prompt_para_imagen = partes[1].strip()
                    
                    st.markdown("---")
                    st.markdown(texto_marketing)
                    
                    # Generación visual vía Pollinations (Modelo Flux)
                    prompt_encoded = urllib.parse.quote(prompt_para_imagen)
                    url_imagen = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux&seed=42"
