import json
import requests
import sseclient
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd

# Realizamos la configuración de la página de Streamlit

st.set_page_config(
    page_title="Wikipedia Live Stream",
    page_icon="./images/wikilogo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'bot' not in st.session_state:
    st.session_state.bot = 0

if 'user' not in st.session_state:
    st.session_state.user = 0

if 'total' not in st.session_state:
    st.session_state.total = 0

col_titulo, col_bot, col_user, col_total = st.columns([4, 1, 1, 1])

bot_placeholder = col_bot.empty()
user_placeholder = col_user.empty()
total_placeholder = col_total.empty()

with col_titulo:
    st.title("Monitor de Datos en Tiempo Real: Cambios en Wikipedia")
    
with col_bot:
    bot_placeholder.metric(label="🤖 Ediciones Bots", value=st.session_state.bot)
    
with col_user:
    user_placeholder.metric(label="👤 Ediciones Usuarios", value=st.session_state.user)

with col_total:
    total_placeholder.metric(label="📊 Total Ediciones", value=st.session_state.bot + st.session_state.user)

st.divider()

metrica_col, tabla_col = st.columns([1, 3])
count_placeholder = metrica_col.empty()
table_placeholder = st.empty()


# Inicializamos una lista en el estado de la sesión para guardar los cambios
if 'lista_cambios' not in st.session_state:
    st.session_state.lista_cambios = []


def stream_wikipedia():
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    
    # El User-Agent es CLAVE para que no de el error 403
    headers = {
        'User-Agent': 'SBD_Analisis/1.0 (ProyectoEstudiante; contacto: estudiante@ejemplo.com)'
    }
    
    try:
        # stream=True permite leer los datos mientras llegan
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        client = sseclient.SSEClient(response)

        for event in client.events():
            if event.event == 'message':
                try:
                    data = json.loads(event.data)
                    
                    if data.get('server_name') == 'es.wikipedia.org':
                        # Extraemos la info
                        es_bot = data.get('bot')
                        
                        if es_bot:
                            st.session_state.bot += 1
                            bot="Bot"
                        else:
                            st.session_state.user += 1
                            bot="Usuario"
                        
                        nuevo_cambio = {
                            "Hora": datetime.now().strftime("%H:%M:%S"),
                            "Usuario": data.get('user'),
                            "Título": data.get('title'),
                            "Tipo": data.get('type'),
                            "Es": bot
                        }
                        
                        bot_placeholder.metric(label="🤖 Ediciones Bots", value=st.session_state.bot)
                        user_placeholder.metric(label="👤 Ediciones Usuarios", value=st.session_state.user)
                        total_placeholder.metric(label="📊 Total Ediciones", value=st.session_state.bot + st.session_state.user)
                        
                        # Guardamos en el estado de la sesión (limitamos a los últimos 15)
                        st.session_state.lista_cambios.insert(0, nuevo_cambio)
                        st.session_state.lista_cambios = st.session_state.lista_cambios[:15]
                        
                        # Actualizar tabla de forma fluida
                        df = pd.DataFrame(st.session_state.lista_cambios)
                        table_placeholder.table(df) # .table se ve más limpio para logs rápidos

                except json.JSONDecodeError:
                    continue
    except Exception as e:
        st.error(f"Error de conexión: {e}")

st.divider()

boton_div_html = """
<div id="container" style="display: flex; justify-content: center; align-items: center; padding: 20px;">
    <button id="miBoton" style="
        background-color: #262730; 
        color: white; 
        padding: 12px 30px; 
        border-radius: 10px; 
        border: 1px solid #4B4B4B;
        cursor: pointer;
        font-size: 18px;
        font-weight: bold;
        width: 350px;
        transition: 0.3s;
    " onmouseover="this.style.backgroundColor='#3e404a'" onmouseout="this.style.backgroundColor='#262730'">
        Empezar a monitorizar
    </button>
</div>

<script>
    const btn = document.getElementById("miBoton");
    
    btn.onclick = function() {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: Math.random() // Enviamos un valor aleatorio para que Streamlit detecte siempre el cambio
        }, '*');
    };
</script>
"""

evento_click = components.html(boton_div_html, height=150)

if evento_click:
    stream_wikipedia()