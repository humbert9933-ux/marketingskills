import streamlit as st
import os
from groq import Groq
import urllib.parse

# --- CONFIGURACIÓN VISUAL (Estética Premium e Industrial) ---
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

st.title("🚀 CENTRAL MULTIMEDIA (GROQ V3.3)")

# --- CONEXIÓN A GROQ ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- RADAR DE AGENTES ESTRATÉGICOS ---
habilidades_dict = {}
carpetas = ["skills", "habilidades", "."] 
for carpeta in carpetas:
    if os.path.exists(carpeta) and os.path.isdir(carpeta):
        for elemento in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, elemento)
            if os.path.isfile(ruta_completa) and elemento.endswith('.md') and elemento.lower() not in ['readme.md', 'requirements.txt', 'app.py']:
                habilidades_dict[elemento.replace('.md', '')] = ruta_completa
            elif os.path.isdir(ruta_completa):
                sk = os.path.join(ruta_completa, "SKILL.md")
                if os.path.exists(sk): habilidades_dict[elemento] = sk

nombres_habilidades = sorted(list(habilidades_dict.keys()))

# --- INTERFAZ DE USUARIO ---
if not nombres_habilidades:
    st.error("⚠️ No se encontraron agentes (.md) en el repositorio.")
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        seleccion = st.selectbox("Elegir Especialista:", nombres_habilidades)
    with col2:
        generar_img = st.checkbox("¿Imagen?", value=True)

    contexto = st.text_area("Detalles de la campaña o producto:", height=150, 
                            placeholder="Ej: Llantas Atlander para 4x4, enfoque en aventura...")

    if st.button("GENERAR CONTENIDO AHORA"):
        if not GROQ_API_KEY:
            st.error("❌ Falta la variable GROQ_API_KEY en Render.")
        elif contexto and seleccion:
            try:
                # Leer instrucciones del agente seleccionado
                with open(habilidades_dict[seleccion], "r", encoding="utf-8") as f:
                    system_prompt = f.read()

                # Inyectar regla de imagen si está activo
                if generar_img:
                    system_prompt += "\n\nIMPORTANTE: Al final de tu respuesta añade 'PROMPT_IMAGEN:' seguido de una descripción detallada en INGLÉS para una imagen publicitaria profesional, cinematográfica y sin texto."

                with st.spinner(f"Groq procesando con {seleccion}..."):
                    # LLAMADA AL NUEVO MODELO LLAMA 3.3 70B
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": contexto}
                        ],
                        temperature=0.7,
                    )
                    full_text = completion.choices[0].message.content

                # Separación de Texto y Generación de Imagen
                if "PROMPT_IMAGEN:" in full_text:
                    partes = full_text.split("PROMPT_IMAGEN:")
                    st.markdown("---")
                    st.markdown(partes[0])
                    
                    # Generación visual (Modelo Flux vía Pollinations)
                    prompt_encoded = urllib.parse.quote(partes[1].strip())
                    url_imagen = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&model=flux&seed=42"
                    
                    st.subheader("🖼️ Propuesta Visual:")
                    st.image(url_imagen, caption="Imagen generada para tu campaña", use_container_width=True)
                else:
                    st.markdown("---")
                    st.markdown(full_text)
                    
            except Exception as e:
                st.error(f"Hubo un problema con la API: {e}")
        else:
            st.warning("Completa los detalles antes de generar.")
