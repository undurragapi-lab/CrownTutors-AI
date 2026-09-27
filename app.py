import streamlit as _st
import google.generativeai as genai
import os

# Configuración de página optimizada para vista móvil
_st.set_page_config(
    page_title="Polyglot AI Video Tutors",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Configurar la API de Gemini (Busca en los secretos de Streamlit Cloud)
try:
    genai.configure(api_key=_st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

# Estilos CSS limpios y profesionales
_st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #0b0e14;
        color: #ffffff;
    }
    
    .mobile-container {
        max-width: 420px;
        margin: auto;
        background: #161b22;
        border-radius: 24px;
        border: 2px solid #30363d;
        padding: 15px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Diccionario de tutores (Apunta directamente a los archivos en la raíz del repositorio)
TUTORES = {
    "Sofía": {
        "video": "sofia.mp4", 
        "estilo": "Casual y Conversacional", 
        "idioma": "Inglés (British English)",
        "prompt_base": "You are Sofia, an expert and friendly British English tutor. Respond naturally in British English, correcting the user's phrasing gently if needed."
    },
    "Sebastián": {
        "video": "sebastian.mp4", 
        "estilo": "Corporativo y Negocios", 
        "idioma": "Inglés (Business)",
        "prompt_base": "You are Sebastián, a professional business English corporate coach. Focus on professional vocabulary and formal phrasing."
    }
}

# Inicializar estado de la sesión
if "chat_historial" not in _st.session_state:
    _st.session_state.chat_historial = [
        {"role": "assistant", "content": "Hello! I'm Sofia. Let's practice your British English!"}
    ]

if "tutor_actual" not in _st.session_state:
    _st.session_state.tutor_actual = "Sofía"

if "texto_documento" not in _st.session_state:
    _st.session_state.texto_documento = ""

# Menú lateral para configuración
with _st.sidebar:
    _st.title("🛠️ Configuración")
    
    api_key_input = _st.text_input("Gemini API Key (Opcional):", type="password")
    if api_key_input:
        genai.configure(api_key=api_key_input)
        
    _st.subheader("Seleccionar Tutor")
    tutor_seleccionado = _st.selectbox(
        "Tutor activo:", 
        list(TUTORES.keys()), 
        index=list(TUTORES.keys()).index(_st.session_state.tutor_actual)
    )
    
    if tutor_seleccionado != _st.session_state.tutor_actual:
        _st.session_state.tutor_actual = tutor_seleccionado
        info_nuevo = TUTORES[tutor_seleccionado]
        _st.session_state.chat_historial = [
            {"role": "assistant", "content": f"Hello! I'm {tutor_seleccionado}, ready to help you practice."}
        ]
        _st.rerun()
        
    _st.markdown("---")
    _st.subheader("📎 Contexto por Documento")
    archivo_subido = _st.file_uploader("Sube un archivo TXT o PDF", type=["txt", "pdf"])
    if archivo_subido:
        contenido = archivo_subido.read().decode("utf-8", errors="ignore")
        _st.session_state.texto_documento = contenido[:4000]
        _st.success(f"¡'{archivo_subido.name}' cargado con éxito!")

info_tutor = TUTORES[_st.session_state.tutor_actual]

# Contenedor principal
_st.markdown('<div class="mobile-container">', unsafe_allow_html=True)

_st.markdown(f"### 🎙️ Tutor: {_st.session_state.tutor_actual}")

# Reproductor de video robusto (busca el archivo en la raíz)
video_file = info_tutor["video"]
if os.path.exists(video_file):
    _st.video(video_file, format="video/mp4", autoplay=True, loop=True, muted=True)
else:
    _st.warning(f"⚠️ No se encontró el archivo '{video_file}' en el repositorio. Súbelo a la raíz de GitHub.")

_st.markdown("---")

# Historial de chat organizado
contenedor_chat = _st.container(height=280)
with contenedor_chat:
    for mensaje in _st.session_state.chat_historial:
        with _st.chat_message(mensaje["role"]):
            _st.write(mensaje["content"])

_st.markdown('</div>', unsafe_allow_html=True)

# Entrada de chat conectada a Gemini
prompt_usuario = _st.chat_input("Escribe tu mensaje...")

if prompt_usuario:
    _st.session_state.chat_historial.append({"role": "user", "content": prompt_usuario})
    
    with _st.spinner("Gemini está pensando..."):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            contexto_doc = f"\n\nContext from uploaded document:\n{_st.session_state.texto_documento}" if _st.session_state.texto_documento else ""
            prompt_completo = f"{info_tutor['prompt_base']}{contexto_doc}\n\nUser message: {prompt_usuario}"
            
            response = model.generate_content(prompt_completo)
            respuesta_ia = response.text
        except Exception as e:
            respuesta_ia = f"⚠️ Error al conectar con Gemini. Configura tu API Key en los secretos de Streamlit. Detalle: {e}"
            
    _st.session_state.chat_historial.append({"role": "assistant", "content": respuesta_ia})
    _st.rerun()
