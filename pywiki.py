import json
import requests
import sseclient
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Wikipedia Live Stream",
    page_icon="./images/wikilogo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialización de estados
if 'bot' not in st.session_state: st.session_state.bot = 0
if 'user' not in st.session_state: st.session_state.user = 0
if 'server_objetivo' not in st.session_state: st.session_state.server_objetivo = "es.wikipedia.org"
if 'lista_cambios' not in st.session_state: st.session_state.lista_cambios = []
if 'monitoreando' not in st.session_state: st.session_state.monitoreando = False

mapa_a_servidores = {
    # --- EUROPA ---
    "Spain": "es.wikipedia.org",
    "France": "fr.wikipedia.org",
    "Germany": "de.wikipedia.org",
    "Italy": "it.wikipedia.org",
    "Portugal": "pt.wikipedia.org",
    "Russia": "ru.wikipedia.org",
    "United Kingdom": "en.wikipedia.org",
    
    # --- LATINOAMÉRICA (es.wikipedia.org) ---
    "Mexico": "es.wikipedia.org",
    "Argentina": "es.wikipedia.org",
    "Colombia": "es.wikipedia.org",
    "Chile": "es.wikipedia.org",
    "Peru": "es.wikipedia.org",
    "Venezuela": "es.wikipedia.org",
    "Ecuador": "es.wikipedia.org",
    "Guatemala": "es.wikipedia.org",
    "Cuba": "es.wikipedia.org",
    "Bolivia": "es.wikipedia.org",
    "Dominican Republic": "es.wikipedia.org",
    "Honduras": "es.wikipedia.org",
    "Paraguay": "es.wikipedia.org",
    "El Salvador": "es.wikipedia.org",
    "Nicaragua": "es.wikipedia.org",
    "Costa Rica": "es.wikipedia.org",
    "Panama": "es.wikipedia.org",
    "Uruguay": "es.wikipedia.org",
    "Puerto Rico": "es.wikipedia.org",
    "Brazil": "pt.wikipedia.org", # Brasil en portugués
    
    # --- ÁFRICA (Español) ---
    "Equatorial Guinea": "es.wikipedia.org",
    
    # --- OCEANÍA ---
    "Australia": "en.wikipedia.org",
    "New Zealand": "en.wikipedia.org",
    
    # --- NORTEAMÉRICA Y ASIA ---
    "United States of America": "en.wikipedia.org",
    "Canada": "en.wikipedia.org",
    "Japan": "ja.wikipedia.org",
    "China": "zh.wikipedia.org"
}
SERVIDOR_GLOBAL = "commons.wikimedia.org"

# --- CABECERA ---
col_titulo, col_bot, col_user, col_total = st.columns([4, 1, 1, 1])
with col_titulo:
    st.title("Monitor de Datos en Tiempo Real: Wikipedia")

bot_placeholder = col_bot.empty()
user_placeholder = col_user.empty()
total_placeholder = col_total.empty()

bot_placeholder.metric(label="🤖 Bots", value=st.session_state.bot)
user_placeholder.metric(label="👤 Usuarios", value=st.session_state.user)
total_placeholder.metric(label="📊 Total", value=st.session_state.bot + st.session_state.user)

st.divider()

# --- CUERPO: TABLA Y MAPA ---
tabla_col, mapa_col = st.columns([1.8, 1.2])

with tabla_col:
    st.subheader(f"🌐 Servidor: {st.session_state.server_objetivo}")
    table_placeholder = st.empty()
    table_placeholder.dataframe(pd.DataFrame(st.session_state.lista_cambios), use_container_width=True, hide_index=True)

with mapa_col:
    st.subheader("Selección de Servidor (Pincha el mar para Global)")
    m = folium.Map(location=[25, 0], zoom_start=1, tiles="CartoDB dark_matter")
    geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"

    # Iluminación de países
    def style_fn(feature):
        name = feature['properties']['name']
        srv = mapa_a_servidores.get(name)
        if srv == st.session_state.server_objetivo:
            return {'fillColor': '#f1c40f', 'color': 'white', 'weight': 3, 'fillOpacity': 0.9} # Activo
        elif name in mapa_a_servidores:
            return {'fillColor': '#3498db', 'color': '#3498db', 'weight': 1, 'fillOpacity': 0.4} # Disponible
        return {'fillColor': '#2c3e50', 'color': '#4B4B4B', 'weight': 0.5, 'fillOpacity': 0.7} # Resto

    folium.GeoJson(
        geojson_url,
        style_function=style_fn,
        highlight_function=lambda x: {'fillColor': 'white', 'fillOpacity': 0.8},
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['País:'])
    ).add_to(m)

    mapa_data = st_folium(m, width="100%", height=380, key="mapa_final_v10")

    # Lógica de detección (País o Commons)
    if mapa_data:
        target = None
        if mapa_data.get("last_active_drawing"):
            pais_click = mapa_data["last_active_drawing"]["properties"]["name"]
            target = mapa_a_servidores.get(pais_click)
        
        # Si no has pinchado un país pero has pinchado el mapa -> Commons
        if target is None and mapa_data.get("last_clicked"):
            target = SERVIDOR_GLOBAL
            
        if target and target != st.session_state.server_objetivo:
            st.session_state.server_objetivo = target
            st.session_state.bot, st.session_state.user = 0, 0
            st.session_state.lista_cambios = []
            st.session_state.monitoreando = False # Se para al cambiar
            st.rerun()

# --- ESTILO DEL BOTÓN (TU CÓDIGO) ---
st.markdown("""
<style>
    .stButton {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
    }
    .stButton > button {
        background-color: #262730 !important;
        color: white !important;
        padding: 12px 30px !important;
        border-radius: 10px !important;
        border: 1px solid #4B4B4B !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 350px !important;
        height: auto !important;
        transition: 0.3s !important;
    }
    .stButton > button:hover {
        background-color: #3e404a !important;
        border-color: #ffffff !important;
    }
    .element-container { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# Lógica del botón
texto = "Dejar de monitorear" if st.session_state.monitoreando else "Empezar a monitorizar"

st.divider()

if st.button(texto):
    st.session_state.monitoreando = not st.session_state.monitoreando
    st.rerun()

# --- FUNCIÓN DE STREAM ---
def stream_wikipedia():
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    headers = {'User-Agent': 'SBD_Monitor/1.0'}
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        client = sseclient.SSEClient(response)
        for event in client.events():
            if not st.session_state.monitoreando: break
            if event.event == 'message':
                try:
                    data = json.loads(event.data)
                    if data.get('server_name') == st.session_state.server_objetivo:
                        es_bot = data.get('bot')
                        if es_bot: st.session_state.bot += 1
                        else: st.session_state.user += 1
                        
                        nuevo = {
                            "Hora": datetime.now().strftime("%H:%M:%S"),
                            "Usuario": data.get('user'),
                            "Título": data.get('title'),
                            "Es": "Bot" if es_bot else "Usuario"
                        }
                        st.session_state.lista_cambios.insert(0, nuevo)
                        st.session_state.lista_cambios = st.session_state.lista_cambios[:15]
                        
                        bot_placeholder.metric("🤖 Bots", st.session_state.bot)
                        user_placeholder.metric("👤 Usuarios", st.session_state.user)
                        total_placeholder.metric("📊 Total", st.session_state.bot + st.session_state.user)
                        table_placeholder.dataframe(pd.DataFrame(st.session_state.lista_cambios), use_container_width=True, hide_index=True)
                except: continue
    except: st.error("Conexión perdida")


if st.session_state.monitoreando:
    stream_wikipedia()