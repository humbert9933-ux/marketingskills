import streamlit as st
import os
import google.generativeai as genai
import urllib.parse # Para procesar la URL de la imagen

# Configuración Visual
st.set_page_config(page_title="Central Multimedia IA", layout="centered")

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
    .img-container { border: 1px solid #333; border-radius: 10px; padding: 10px; background: #1E1E1E; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ CENTRAL MULTIMEDIA")

# Conexión a Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# --- RADAR DE HABILIDADES ---
habilidades_dict = {}
carpetas = ["skills", "habilidades", "."] 
for c in carpetas:
    if os.path.exists(c) and os.path.isdir(c):
        for e in os.listdir(c):
            ruta = os.path.join(c, e)
            if os.path.isfile(ruta) and e.endswith('.md') and e.lower() not in ['readme.md', 'requirements.txt', 'app.py']:
                habilidades_dict[e.replace('.md', '')] = ruta
            elif os.path.isdir(ruta):
                sk = os.path.join(ruta, "SKILL.md")
                if os.path.exists(sk): habilidades_dict[e] = sk

nombres = sorted(list(habilidades_dict.keys()))

if nombres:
    col1, col2 = st.columns([3, 1])
    with col1:
        seleccion = st.selectbox("Elegir Especialista:", nombres)
    with col2:
        generar_img = st.checkbox("¿Imagen?", value=True)

    contexto = st.text_area("Detalles de la campaña:", height=150, placeholder="Ej: Llantas Maxell para camiones...")

    if st.button("GENERAR CONTENIDO COMPLETO"):
        if not API_KEY:
            st.error("Configura GEMINI_API_KEY en Render.")
        elif contexto and seleccion:
            try:
                with open(habilidades_dict[seleccion], "r", encoding="utf-8") as f:
                    system_prompt = f.read()

                # Si el usuario quiere imagen, le pedimos a Gemini un prompt extra
                if generar_img:
                    system_prompt += "\n\nIMPORTANTE: Al final de tu respuesta, añade una sección llamada 'PROMPT_IMAGEN:' seguida de una descripción detallada en INGLÉS para generar una imagen publicitaria de este producto. La descripción debe ser cinematográfica, estilo profesional y sin texto."

                model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_prompt)
                
                with st.spinner("Procesando texto e idea visual..."):
                    response = model.generate_content(contexto)
                    texto_final = response.text

                # Separar el texto del prompt de imagen si existe
                if "PROMPT_IMAGEN:" in texto_final:
                    partes = texto_final.split("PROMPT_IMAGEN:")
                    resultado_texto = partes[0]
                    imagen_prompt = partes[1].strip()
                    
                    st.markdown("---")
                    st.markdown(resultado_texto)
                    
                    # Generar y mostrar imagen usando Pollinations (Gratis y rápido)
                    prompt_encoded = urllib.parse.quote(imagen_prompt)
                    # Usamos un modelo estilo "Flux" o cinematográfico
                    url_imagen = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux&seed=42"
                    
                    st.subheader("🖼️ Sugerencia Visual para la Campaña:")
                    st.image(url_imagen, caption="Imagen generada por IA para tu anuncio", use_container_width=True)
                    st.info(f"**Prompt usado:** {imagen_prompt}")
                else:
                    st.markdown("---")
                    st.markdown(texto_final)
                    
            except Exception as e:
                st.error(f"Error: {e}")
