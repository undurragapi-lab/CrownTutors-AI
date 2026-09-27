import streamlit as _st

# Configuración de página optimizada para vista móvil (Pixel 9)
_st.set_page_config(
    page_title="Polyglot AI Video Tutors",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS limpios para el contenedor tipo app móvil y modo oscuro
_st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #0b0e14;
        color: #ffffff;
    }
    
    /* Contenedor principal estilo pantalla de celular */
    .mobile-wrapper {
        max-width: 420px;
        margin: auto;
        border-radius: 28px;
        overflow: hidden;
        border: 3px solid #2a2e39;
        background: #121824;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Diccionario de tutores
TUTORES = {
    "Sofía": {"video_path": "sofia.mp4", "estilo": "Casual y Conversacional", "idioma_def": "Inglés (UK)"},
    "Sebastián": {"video_path": "sebastian.mp4", "estilo": "Corporativo", "idioma_def": "Inglés (Business)"},
    "Emilia": {"video_path": "emilia.mp4", "estilo": "Literatura", "idioma_def": "Francés"},
    "Bruno": {"video_path": "bruno.mp4", "estilo": "Debate", "idioma_def": "Alemán"}
}

# Inicializar estado de la sesión
if "chat_historial" not in _st.session_state:
    _st.session_state.chat_historial = [
        {"role": "assistant", "content": "Hello! I'm Sofia. Let's practice your British English. Feel free to upload a document or start chatting!"}
    ]

if "tutor_actual" not in _st.session_state:
    _st.session_state.tutor_actual = "Sofía"

# --- BARRA LATERAL (MENÚ) ---
with _st.sidebar:
    _st.title("🛠️ Menú de Configuración")
    _st.subheader("Selecciona tu Tutor")
    
    tutor_seleccionado = _st.selectbox("Tutor activo:", list(TUTORES.keys()), index=list(TUTORES.keys()).index(_st.session_state.tutor_actual))
    
    if tutor_seleccionado != _st.session_state.tutor_actual:
        _st.session_state.tutor_actual = tutor_seleccionado
        _st.session_state.chat_historial = [
            {"role": "assistant", "content": f"Hello! I'm {tutor_seleccionado}, ready to help you practice."}
        ]
        _st.rerun()
        
    _st.markdown("---")
    _st.subheader("📎 Documento de Contexto")
    archivo_subido = _st.file_uploader("Sube un archivo de texto o PDF", type=["txt", "pdf"])
    if archivo_subido:
        _st.success(f"¡{archivo_subido.name} cargado correctamente!")

# Datos del tutor actual
info_tutor = TUTORES[_st.session_state.tutor_actual]

# --- CONTENEDOR PRINCIPAL TIPO APP MÓVIL ---
_st.markdown('<div class="mobile-wrapper">', unsafe_allow_html=True)

# Encabezado visual de la app móvil
col1, col2 = _st.columns([3, 1])
with col1:
    _st.markdown(f"### 🎙️ {_st.session_state.tutor_actual}")
    _st.caption(f"Estilo: {info_tutor['estilo']}")
with col2:
    if _st.button("⚙️ Menú"):
        _st.toast("Usa el menú lateral de Streamlit para cambiar de tutor.", icon="ℹ️")

# Reproductor de video del tutor (Limpio y centrado)
try:
    _st.video(info_tutor["video_path"], format="video/mp4", autoplay=True, loop=True, muted=True)
except Exception:
    _st.warning("⚠️ Video de tutor no disponible temporalmente.")

_st.markdown("---")

# Contenedor de mensajes de chat nativos (organizados y scrolleables)
chat_container = _st.container(height=300)
with chat_container:
    for mensaje in _st.session_state.chat_historial:
        with _st.chat_message(mensaje["role"]):
            _st.write(mensaje["content"])

_st.markdown('</div>', unsafe_allow_html=True)

# --- ENTRADA DE CHAT NATIVA (Fácil de usar en el Pixel 9) ---
prompt_usuario = _st.chat_input("Escribe tu mensaje aquí...")

if prompt_usuario:
    # Agregar mensaje del usuario
    _st.session_state.chat_historial.append({"role": "user", "content": prompt_usuario})
    
    # Respuesta simulada de la IA (aquí conectaremos la lógica de Gemini más adelante)
    respuesta_ia = f"Splendid! Your phrasing is natural. Let's keep practicing with {_st.session_state.tutor_actual}."
    _st.session_state.chat_historial.append({"role": "assistant", "content": respuesta_ia})
    
    _st.rerun()
