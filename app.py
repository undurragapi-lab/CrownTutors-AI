import streamlit as _st
import google.generativeai as genai

# Configuración de página optimizada para vista móvil (Pixel 9)
_st.set_page_config(
    page_title="Polyglot AI Video Tutors",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Configurar la API de Gemini (Busca en los secretos de Streamlit Cloud)
try:
    genai.configure(api_key=_st.secrets["GEMINI_API_KEY"])
except Exception:
    # Clave de respaldo o advertencia si no está configurada en secretos
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
    
    /* Contenedor principal estilo tarjeta de app móvil */
    .mobile-container {
        max-width: 420px;
        margin: auto;
        background: #161b22;
        border-radius: 24px;
        border: 2px solid #30363d;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    }
    
    .tutor-header {
        text-align: center;
        margin-bottom: 15px;
    }
    .tutor-avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 3px solid #58a6ff;
        object-fit: cover;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Base de datos de tutores con sus características e instrucciones de sistema
TUTORES = {
    "Sofía": {
        "img": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300", 
        "estilo": "Casual y Conversacional", 
        "idioma": "Inglés (British English)",
        "prompt_base": "You are Sofia, an expert and friendly British English tutor. Respond naturally in British English, correcting the user's phrasing gently if needed."
    },
    "Sebastián": {
        "img": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300", 
        "estilo": "Corporativo y Negocios", 
        "idioma": "Inglés (Business)",
        "prompt_base": "You are Sebastián, a professional business English corporate coach. Focus on professional vocabulary and formal phrasing."
    },
    "Emilia": {
        "img": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300", 
        "estilo": "Literatura y Lectura", 
        "idioma": "Francés",
        "prompt_base": "Vous êtes Emilia, une tutrice de français passionnée de littérature. Répondez en français de manière élégante."
    },
    "Bruno": {
        "img": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300", 
        "estilo": "Nivel Avanzado y Debate", 
        "idioma": "Alemán",
        "prompt_base": "Du bist Bruno, ein deutscher Tutor für fortgeschrittene Konversation und Debatte. Antworte auf Deutsch."
    }
}

# Inicializar estado de la sesión
if "chat_historial" not in _st.session_state:
    _st.session_state.chat_historial = [
        {"role": "assistant", "content": "Hello! I'm Sofia. Let's practice your British English. Feel free to chat or upload a document!"}
    ]

if "tutor_actual" not in _st.session_state:
    _st.session_state.tutor_actual = "Sofía"

if "texto_documento" not in _st.session_state:
    _st.session_state.texto_documento = ""

# Menú lateral para configuración y documentos
with _st.sidebar:
    _st.title("🛠️ Configuración")
    
    # Permitir ingresar la API key si no está en secretos
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
            {"role": "assistant", "content": f"Hello! I'm {tutor_seleccionado}, ready to help you practice {info_nuevo['idioma']}."}
        ]
        _st.rerun()
        
    _st.markdown("---")
    _st.subheader("📎 Contexto por Documento")
    archivo_subido = _st.file_uploader("Sube un archivo TXT o PDF", type=["txt", "pdf"])
    if archivo_subido:
        contenido = archivo_subido.read().decode("utf-8", errors="ignore")
        _st.session_state.texto_documento = contenido[:4000] # Limitar tokens
        _st.success(f"¡'{archivo_subido.name}' cargado con éxito para contextualizar!")

# Obtener información del tutor seleccionado
info_tutor = TUTORES[_st.session_state.tutor_actual]

# Contenedor principal de la interfaz móvil
_st.markdown('<div class="mobile-container">', unsafe_allow_html=True)

# Presentación visual fija del tutor
_st.markdown(f"""
    <div class="tutor-header">
        <img src="{info_tutor['img']}" class="tutor-avatar" />
        <h2 style="margin: 10px 0 2px 0; font-size: 20px;">{_st.session_state.tutor_actual}</h2>
        <p style="margin: 0; color: #58a6ff; font-size: 13px;">{info_tutor['estilo']} ({info_tutor['idioma']})</p>
    </div>
""", unsafe_allow_html=True)

_st.markdown("---")

# Contenedor de chat organizado con scroll interno
contenedor_chat = _st.container(height=320)
with contenedor_chat:
    for mensaje in _st.session_state.chat_historial:
        with _st.chat_message(mensaje["role"]):
            _st.write(mensaje["content"])

_st.markdown('</div>', unsafe_allow_html=True)

# Entrada de texto oficial de Streamlit
prompt_usuario = _st.chat_input("Escribe tu mensaje...")

if prompt_usuario:
    # Registrar mensaje del usuario en el historial
    _st.session_state.chat_historial.append({"role": "user", "content": prompt_usuario})
    
    with _st.spinner("Gemini está pensando..."):
        try:
            # Configurar modelo y contexto
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Construir el prompt completo con la personalidad del tutor y contexto opcional
            contexto_doc = f"\n\nContext from uploaded document:\n{_st.session_state.texto_documento}" if _st.session_state.texto_documento else ""
            prompt_completo = f"{info_tutor['prompt_base']}{contexto_doc}\n\nUser message: {prompt_usuario}"
            
            # Llamada real a Gemini
            response = model.generate_content(prompt_completo)
            respuesta_ia = response.text
        except Exception as e:
            respuesta_ia = f"⚠️ Error al conectar con Gemini. Asegúrate de configurar tu API Key. Detalle: {e}"
            
    # Registrar respuesta de la IA
    _st.session_state.chat_historial.append({"role": "assistant", "content": respuesta_ia})
    _st.rerun()
