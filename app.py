import streamlit as _st
import google.generativeai as genai
import os

# Configuración de página
_st.set_page_config(
    page_title="CrownTutors AI",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Configurar la API de Gemini de forma segura
api_key_val = ""
try:
    if "GEMINI_API_KEY" in _st.secrets:
        api_key_val = _st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if api_key_val:
    genai.configure(api_key=api_key_val)

# Estilos CSS avanzados
_st.markdown("""
    <style>
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    .fullscreen-video-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        overflow: hidden;
        background: #000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .fullscreen-video-container video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .chat-overlay {
        position: absolute;
        bottom: 80px;
        left: 12px;
        right: 12px;
        background: rgba(0, 0, 0, 0.75);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        padding: 12px 16px;
        max-height: 40vh;
        overflow-y: auto;
        z-index: 10;
    }
    
    .chat-message-user {
        color: #8ab4f8;
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    .chat-message-assistant {
        color: #ffffff;
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    .welcome-screen {
        position: relative;
        z-index: 10;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 90vh;
        text-align: center;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Definición de tutores
TUTORES = {
    "Sofía": {
        "video": "sofia.mp4", 
        "estilo": "Casual y Conversacional", 
        "idioma": "Inglés (British English)",
        "voice_lang": "en-GB",
        "prompt_base": "You are Sofia, an expert and friendly British English tutor with a refined Received Pronunciation (RP) accent. Correct the user constructively and keep the conversation flowing naturally."
    },
    "Sebastián": {
        "video": "sebastian.mp4", 
        "estilo": "Corporativo y Negocios", 
        "idioma": "Inglés (Business)",
        "voice_lang": "en-US",
        "prompt_base": "You are Sebastián, a professional corporate business English coach. Focus on professional vocabulary and business communication."
    }
}

# Inicializar estados de sesión
if "chats_activos" not in _st.session_state:
    _st.session_state.chats_activos = {}

if "chat_actual" not in _st.session_state:
    _st.session_state.chat_actual = None

if "tutor_activo" not in _st.session_state:
    _st.session_state.tutor_activo = None

if "texto_documento" not in _st.session_state:
    _st.session_state.texto_documento = ""

if "ultima_respuesta" not in _st.session_state:
    _st.session_state.ultima_respuesta = ""

# Menú lateral de herramientas
with _st.sidebar:
    _st.title("🛠️ Menú de Herramientas")
    
    api_key_input = _st.text_input("Gemini API Key:", value=api_key_val, type="password")
    if api_key_input:
        genai.configure(api_key=api_key_input)
        api_key_val = api_key_input
        
    _st.markdown("---")
    _st.subheader("💬 Chats Activos")
    
    lista_chats = list(_st.session_state.chats_activos.keys())
    if lista_chats:
        chat_seleccionado = _st.selectbox(
            "Selecciona tu chat:", 
            lista_chats,
            index=lista_chats.index(_st.session_state.chat_actual) if _st.session_state.chat_actual in lista_chats else 0
        )
        if chat_seleccionado != _st.session_state.chat_actual:
            _st.session_state.chat_actual = chat_seleccionado
            if "Sofía" in chat_seleccionado:
                _st.session_state.tutor_activo = "Sofía"
            elif "Sebastián" in chat_seleccionado:
                _st.session_state.tutor_activo = "Sebastián"
            _st.rerun()
    else:
        _st.info("No hay chats iniciados. Crea uno abajo 👇")

    _st.markdown("---")
    _st.subheader("➕ Iniciar Nueva Sesión")
    nuevo_tutor = _st.selectbox("Seleccionar Tutor:", list(TUTORES.keys()))
    
    if _st.button("Crear y Activar Chat"):
        clave_chat = f"{nuevo_tutor} - Sesión Principal"
        saludo_inicial = f"Hello! I'm {nuevo_tutor}. Let's get started with your practice!"
        _st.session_state.chats_activos[clave_chat] = [
            {"role": "assistant", "content": saludo_inicial}
        ]
        _st.session_state.chat_actual = clave_chat
        _st.session_state.tutor_activo = nuevo_tutor
        _st.session_state.ultima_respuesta = saludo_inicial
        _st.rerun()

    _st.markdown("---")
    _st.subheader("📎 Adjuntar Documento")
    archivo_subido = _st.file_uploader("Sube un archivo TXT o PDF", type=["txt", "pdf"])
    if archivo_subido:
        contenido = archivo_subido.read().decode("utf-8", errors="ignore")
        _st.session_state.texto_documento = contenido[:4000]
        _st.success(f"¡'{archivo_subido.name}' integrado al contexto!")

# Pantalla principal condicional
if _st.session_state.chat_actual is None or _st.session_state.tutor_activo is None:
    _st.markdown("""
        <div class="welcome-screen">
            <h2>👋 ¡Bienvenido a CrownTutors AI!</h2>
            <p style="color: #a0a8b4; font-size: 16px; margin-top: 10px;">
                Despliega el menú lateral para configurar tu API Key, seleccionar un tutor e iniciar tu sesión.
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    info_tutor = TUTORES[_st.session_state.tutor_activo]
    historial_actual = _st.session_state.chats_activos[_st.session_state.chat_actual]

    video_file = info_tutor["video"]
    
    if os.path.exists(video_file):
        texto_a_decir = _st.session_state.ultima_respuesta
        lang_voz = info_tutor["voice_lang"]

        video_html = f"""
        <div class="fullscreen-video-container">
            <video id="avatarVideo" src="{video_file}" playsinline muted></video>
        </div>
        <script>
            const video = document.getElementById('avatarVideo');
            const textToSpeak = {repr(texto_a_decir)};
            const voiceLang = "{lang_voz}";

            function playAvatarSpeech() {{
                if (!textToSpeak) return;
                const synth = window.speechSynthesis;
                const utterThis = new SpeechSynthesisUtterance(textToSpeak);
                utterThis.lang = voiceLang;
                
                utterThis.onstart = function() {{
                    video.play();
                }};
                
                utterThis.onend = function() {{
                    video.pause();
                }};
                
                utterThis.onerror = function() {{
                    video.pause();
                }};

                synth.speak(utterThis);
            }}

            window.onload = playAvatarSpeech();
        </script>
        """
        _st.markdown(video_html, unsafe_allow_html=True)
    else:
        _st.error(f"⚠️ No se encontró el archivo de video '{video_file}' en el repositorio de GitHub.")

    # Capa de historial de chat flotante
    _st.markdown('<div class="chat-overlay">', unsafe_allow_html=True)
    for mensaje in historial_actual:
        rol = mensaje["role"]
        texto = mensaje["content"]
        if rol == "user":
            _st.markdown(f'<div class="chat-message-user"><b>Tú:</b> {texto}</div>', unsafe_allow_html=True)
        else:
            _st.markdown(f'<div class="chat-message-assistant"><b>{_st.session_state.tutor_activo}:</b> {texto}</div>', unsafe_allow_html=True)
    _st.markdown('</div>', unsafe_allow_html=True)

    # Barra de mensajes inferior unificada
    with _st.form(key="gemini_input_form", clear_on_submit=True):
        col_plus, col_input, col_send = _st.columns([1, 7, 1])
        
        with col_plus:
            btn_adjuntar = _st.form_submit_button("➕")
        with col_input:
            prompt_usuario = _st.text_input("Mensaje", label_visibility="collapsed", placeholder="Escribe tu mensaje...")
        with col_send:
            btn_enviar = _st.form_submit_button("➤")

    # Lógica de respuesta con Gemini
    if btn_enviar and prompt_usuario:
        historial_actual.append({"role": "user", "content": prompt_usuario})
        
        if not api_key_val:
            respuesta_ia = "⚠️ Error: Por favor ingresa tu API Key de Gemini en el menú de herramientas."
        else:
            with _st.spinner("Pensando respuesta..."):
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    contexto_doc = f"\n\nContext from uploaded document:\n{_st.session_state.texto_documento}" if _st.session_state.texto_documento else ""
                    prompt_completo = f"{info_tutor['prompt_base']}{contexto_doc}\n\nUser message: {prompt_usuario}"
                    
                    response = model.generate_content(prompt_completo)
                    respuesta_ia = response.text
                except Exception as e:
                    respuesta_ia = f"⚠️ Error con Gemini: {str(e)}"
                
        historial_actual.append({"role": "assistant", "content": respuesta_ia})
        _st.session_state.ultima_respuesta = respuesta_ia
        _st.rerun()

    if btn_adjuntar:
        _st.info("💡 Tip: Utiliza la sección 'Adjuntar Documento' en el menú lateral.")
