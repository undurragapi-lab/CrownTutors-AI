import streamlit as _st
import os

# Configuración de página optimizada para vista móvil (Pixel 9)
_st.set_page_config(
    page_title="Polyglot AI Video Tutors",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para el diseño flotante, inmersivo y tipo app móvil
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
    .mobile-screen {
        position: relative;
        width: 100%;
        max-width: 420px;
        height: 680px;
        margin: auto;
        border-radius: 32px;
        overflow: hidden;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
        border: 4px solid #2a2e39;
    }
    
    /* Barra superior flotante (Botón de menú ☰) */
    .top-bar {
        position: absolute;
        top: 15px;
        left: 15px;
        z-index: 10;
    }
    
    /* Capa de chat flotante sobre el video */
    .chat-overlay {
        position: absolute;
        bottom: 80px;
        left: 15px;
        right: 15px;
        background: rgba(10, 14, 23, 0.65);
        backdrop-filter: blur(10px);
        padding: 12px;
        border-radius: 18px;
        max-height: 180px;
        overflow-y: auto;
        border: 1px solid rgba(255,255,255,0.1);
        z-index: 10;
    }
    
    .chat-msg-assistant {
        background: rgba(255, 255, 255, 0.15);
        color: #f0f2f6;
        padding: 8px 12px;
        border-radius: 12px;
        margin-bottom: 8px;
        font-size: 13px;
    }
    
    .chat-msg-user {
        background: rgba(0, 122, 255, 0.4);
        color: #ffffff;
        padding: 8px 12px;
        border-radius: 12px;
        margin-bottom: 8px;
        text-align: right;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# Definición de los 8 tutores base con acento británico RP y perfiles
TUTORES = {
    "Sofía": {"video_path": "ruta_video_sofia.mp4", "estilo": "Casual y Conversacional"},
    "Sebastián": {"video_path": "ruta_video_sebastian.mp4", "estilo": "Corporativo y de Negocios"},
    "Emilia": {"video_path": "ruta_video_emilia.mp4", "estilo": "Literatura y Lectura"},
    "Bruno": {"video_path": "ruta_video_bruno.mp4", "estilo": "Nivel Avanzado y Debate"},
    "Mateo": {"video_path": "ruta_video_mateo.mp4", "estilo": "Dinámico y Juvenil"},
    "Lucas": {"video_path": "ruta_video_lucas.mp4", "estilo": "Marketing y Creatividad"},
    "Martina": {"video_path": "ruta_video_martina.mp4", "estilo": "Rápida y Directa"},
    "Valentina": {"video_path": "ruta_video_valentina.mp4", "estilo": "Gramática y Estructura"}
}

# Inicializar sistema de múltiples chats por idioma en la sesión
if "chats_activos" not in _st.session_state:
    _st.session_state.chats_activos = {
        "Inglés - Sofía": {
            "tutor": "Sofía",
            "idioma": "Inglés",
            "mensajes": [{"role": "assistant", "content": "Hello! I'm Sofia. Let's practice your British English. Feel free to upload a document to discuss!"}]
        }
    }

if "chat_actual" not in _st.session_state:
    _st.session_state.chat_actual = "Inglés - Sofía"

if "mostrar_menu" not in _st.session_state:
    _st.session_state.mostrar_menu = False

if "archivo_cargado_texto" not in _st.session_state:
    _st.session_state.archivo_cargado_texto = None

# Botón de menú flotante superior izquierdo (☰)
_st.markdown('<div class="top-bar">', unsafe_allow_html=True)
if _st.button("☰", help="Abrir menú de herramientas y chats"):
    _st.session_state.mostrar_menu = not _st.session_state.mostrar_menu
_st.markdown('</div>', unsafe_allow_html=True)

# Menú lateral dinámico (Gestión de chats e idiomas)
if _st.session_state.mostrar_menu:
    _st.sidebar.title("🛠️ Menú de Herramientas")
    _st.sidebar.subheader("💬 Chats Multilingües")
    
    lista_nombres_chats = list(_st.session_state.chats_activos.keys())
    chat_seleccionado = _st.sidebar.selectbox("Selecciona un chat activo:", lista_nombres_chats, index=lista_nombres_chats.index(_st.session_state.chat_actual))
    
    if chat_seleccionado != _st.session_state.chat_actual:
        _st.session_state.chat_actual = chat_seleccionado
        _st.rerun()
        
    _st.sidebar.markdown("---")
    _st.sidebar.subheader("➕ Crear Nuevo Chat")
    nuevo_tutor = _st.sidebar.selectbox("Elige Tutor:", list(TUTORES.keys()))
    nuevo_idioma = _st.sidebar.text_input("Idioma a practicar:", "Francés")
    
    if _st.sidebar.button("Iniciar Nuevo Chat"):
        key_chat = f"{nuevo_idioma} - {nuevo_tutor}"
        if key_chat not in _st.session_state.chats_activos:
            _st.session_state.chats_activos[key_chat] = {
                "tutor": nuevo_tutor,
                "idioma": nuevo_idioma,
                "mensajes": [{"role": "assistant", "content": f"Hello! I'm {nuevo_tutor}, ready to practice {nuevo_idioma} with you."}]
            }
        _st.session_state.chat_actual = key_chat
        _st.session_state.mostrar_menu = False
        _st.rerun()

# Obtener datos del chat actual
info_chat_actual = _st.session_state.chats_activos[_st.session_state.chat_actual]
tutor_activo = info_chat_actual["tutor"]
idioma_activo = info_chat_actual["idioma"]
info_tutor = TUTORES[tutor_activo]

# Contenedor visual emulando la pantalla del Pixel 9
_st.markdown('<div class="mobile-screen">', unsafe_allow_html=True)

# 1. Reproductor de video en bucle del tutor activo (Validación optimizada)
if os.path.exists(info_tutor["video_path"]):
    _st.video(info_tutor["video_path"], format="video/mp4", autoplay=True, loop=True, muted=False)
else:
    _st.warning(f"⚠️ Archivo de video para {tutor_activo} no encontrado.")

# 2. Capa de chat flotante transparente con los mensajes del idioma actual
chat_html = f'<div class="chat-overlay"><small style="color:#00d2ff;">Idioma: {idioma_activo} | Tutor: {tutor_activo}</small><hr style="margin:2px 0; border-color:rgba(255,255,255,0.1);">'
for msg in info_chat_actual["mensajes"]:
    if msg["role"] == "assistant":
        chat_html += f'<div class="chat-msg-assistant"><b>{tutor_activo}:</b> {msg["content"]}</div>'
    else:
        chat_html += f'<div class="chat-msg-user"><b>Tú:</b> {msg["content"]}</div>'
chat_html += '</div>'
_st.markdown(chat_html, unsafe_allow_html=True)

_st.markdown('</div>', unsafe_allow_html=True)

# 3. Sección de adjuntar documentos (Panel para contextualizar con archivos)
with _st.expander("📎 Panel de Documentos y Contextualización"):
    archivo_subido = _st.file_uploader("Sube un documento (TXT, PDF) para analizar con el tutor:", type=["txt", "pdf"])
    if archivo_subido is not None:
        texto_archivo = archivo_subido.read().decode("utf-8", errors="ignore")
        _st.session_state.archivo_cargado_texto = texto_archivo[:3000]
        _st.success(f"¡Documento '{archivo_subido.name}' cargado con éxito! Contexto integrado.")

# 4. Barra inferior: Entrada de texto/voz del usuario
_st.write("")
entrada_usuario = _st.text_input("", placeholder=f"Habla o escribe en {idioma_activo}...", label_visibility="collapsed")

if entrada_usuario:
    info_chat_actual["mensajes"].append({"role": "user", "content": entrada_usuario})
    
    contexto_extra = " [Con documento adjunto integrado]" if _st.session_state.archivo_cargado_texto else ""
    respuesta_ia = f"Splendid point!{contexto_extra} [Feedback]: Your {idioma_activo} phrasing is quite good. Let's keep discussing!"
    
    info_chat_actual["mensajes"].append({"role": "assistant", "content": respuesta_ia})
    _st.rerun()
