import streamlit as _st
import google.generativeai as genai
import os

# Configuración de la página
_st.set_page_config(
    page_title="CrownTutors AI",
    layout="centered",
    initial_sidebar_state="auto"
)

# Inicializar la API Key en session_state para que no la pida constantemente
if "api_key" not in _st.session_state:
    _st.session_state.api_key = ""
    try:
        if "GEMINI_API_KEY" in _st.secrets:
            _st.session_state.api_key = _st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if _st.session_state.api_key:
    genai.configure(api_key=_st.session_state.api_key)

# Estilos CSS limpios y modernos
_st.markdown("""
    <style>
    footer {visibility: hidden !important;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 7rem !important;
        max-width: 100% !important;
    }
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Contenedor estético para el avatar */
    .avatar-container {
        width: 100%;
        max-height: 40vh;
        overflow: hidden;
        border-radius: 14px;
        margin-bottom: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #000000;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .avatar-container video {
        width: 100%;
        height: auto;
        object-fit: cover;
    }
    
    /* Caja de historial de chat */
    .chat-history-box {
        background: rgba(20, 20, 20, 0.9);
        border-radius: 12px;
        padding: 12px;
        max-height: 25vh;
        overflow-y: auto;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .chat-message-user {
        color: #8ab4f8;
        margin-bottom: 6px;
        font-size: 14px;
    }
    
    .chat-message-assistant {
        color: #ffffff;
        margin-bottom: 6px;
        font-size: 14px;
    }
    
    .welcome-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 65vh;
        text-align: center;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Definición de tutores (configurados estrictamente en Inglés)
TUTORES = {
    "Sofía": {
        "video": "sofia.mp4", 
        "estilo": "Casual y Conversacional", 
        "idioma": "Inglés (British English)",
        "voice_lang": "en-GB",
        "prompt_base": "You are Sofia, an expert and friendly British English tutor with a refined Received Pronunciation (RP) accent. Always reply in English. Correct the user constructively and keep the conversation flowing naturally."
    },
    "Sebastián": {
        "video": "sebastian.mp4", 
        "estilo": "Corporativo y Negocios", 
        "idioma": "Inglés (Business)",
        "voice_lang": "en-US",
        "prompt_base": "You are Sebastián, a professional corporate business English coach. Always reply in English. Focus on professional vocabulary and business communication."
    }
}

# Inicialización de estados de sesión
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

# Menú lateral de herramientas (☰)
with _st.sidebar:
    _st.title("🛠️ Menú de Herramientas")
    
    api_key_input = _st.text_input("Gemini API Key:", value=_st.session_state.api_key, type="password")
    if api_key_input and api_key_input != _st.session_state.api_key:
        _st.session_state.api_key = api_key_input
        genai.configure(api_key=api_key_input)
        _st.success("¡API Key guardada!")
        
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

# Pantalla de bienvenida o chat activo
if _st.session_state.chat_actual is None or _st.session_state.tutor_activo is None:
    _st.markdown("""
        <div class="welcome-screen">
            <h2>👋 ¡Bienvenido a CrownTutors AI!</h2>
            <p style="color: #a0a8b4; font-size: 16px; margin-top: 10px;">
                Toca el botón de menú <b>(☰)</b> en la esquina superior izquierda 
                para configurar tu API Key, seleccionar un tutor e iniciar tu práctica en inglés.
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    info_tutor = TUTORES[_st.session_state.tutor_activo]
    historial_actual = _st.session_state.chats_activos[_st.session_state.chat_actual]

    video_file = info_tutor["video"]
    texto_a_decir = _st.session_state.ultima_respuesta
    lang_voz = info_tutor["voice_lang"]

    # Reproducción del video sincronizada exactamente con el tiempo de locución del mensaje
    if os.path.exists(video_file):
        video_html = f"""
        <div class="avatar-container">
            <video id="tutorVideo" src="{video_file}" playsinline muted></video>
        </div>
        <script>
            const videoElem = document.getElementById('tutorVideo');
            const messageText = {repr(texto_a_decir)};
            const voiceLanguage = "{lang_voz}";

            function playAvatarSync() {{
                if (!messageText) return;
                
                // Reproducir voz sintética del navegador si está disponible
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(messageText);
                    utterance.lang = voiceLanguage;
                    
                    utterance.onstart = function() {{
                        videoElem.currentTime = 0;
                        videoElem.play();
                    }};
                    
                    utterance.onend = function() {{
                        videoElem.pause();
                        videoElem.currentTime = 0;
                    }};
                    
                    utterance.onerror = function() {{
                        videoElem.pause();
                    }};
                    
                    window.speechSynthesis.speak(utterance);
                }} else {{
                    // Fallback por tiempo estimado basado en la longitud del texto (aprox. 15 caracteres por segundo)
                    const estimatedTimeMs = Math.min(Math.max(messageText.length * 70, 2000), 10000);
                    videoElem.currentTime = 0;
                    videoElem.play();
                    setTimeout(() => {{
                        videoElem.pause();
                        videoElem.currentTime = 0;
                    }}, estimatedTimeMs);
                }}
            }}

            window.addEventListener('load', playAvatarSync);
        </script>
        """
        _st.markdown(video_html, unsafe_allow_html=True)
    else:
        _st.warning(f"⚠️ El archivo de video '{video_file}' no se encuentra en el repositorio de GitHub.")

    # Historial de conversación visible
    _st.markdown('<div class="chat-history-box">', unsafe_allow_html=True)
    for mensaje in historial_actual:
        rol = mensaje["role"]
        texto = mensaje["content"]
        if rol == "user":
            _st.markdown(f'<div class="chat-message-user"><b>Tú:</b> {texto}</div>', unsafe_allow_html=True)
        else:
            _st.markdown(f'<div class="chat-message-assistant"><b>{_st.session_state.tutor_activo}:</b> {texto}</div>', unsafe_allow_html=True)
    _st.markdown('</div>', unsafe_allow_html=True)

    # Formulario unificado de entrada en la parte inferior
    with _st.form(key="gemini_input_form", clear_on_submit=True):
        col_plus, col_input, col_send = _st.columns([1, 7, 1])
        
        with col_plus:
            btn_adjuntar = _st.form_submit_button("➕")
        with col_input:
            prompt_usuario = _st.text_input("Mensaje", label_visibility="collapsed", placeholder="Type your message in English...")
        with col_send:
            btn_enviar = _st.form_submit_button("➤")

    # Lógica con Gemini usando el modelo estable `gemini-1.5-flash`
    if btn_enviar and prompt_usuario:
        historial_actual.append({"role": "user", "content": prompt_usuario})
        
        if not _st.session_state.api_key:
            respuesta_ia = "⚠️ Error: Please enter your Gemini API Key in the sidebar menu (☰)."
        else:
            with _st.spinner("Thinking..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    contexto_doc = f"\n\nContext from uploaded document:\n{_st.session_state.texto_documento}" if _st.session_state.texto_documento else ""
                    prompt_completo = f"{info_tutor['prompt_base']}{contexto_doc}\n\nUser message: {prompt_usuario}"
                    
                    response = model.generate_content(prompt_completo)
                    respuesta_ia = response.text
                except Exception as e:
                    respuesta_ia = f"⚠️ Gemini Error: {str(e)}"
                
        historial_actual.append({"role": "assistant", "content": respuesta_ia})
        _st.session_state.ultima_respuesta = respuesta_ia
        _st.rerun()

    if btn_adjuntar:
        _st.info("💡 Tip: Use the 'Attach Document' section in the sidebar menu (☰).")
