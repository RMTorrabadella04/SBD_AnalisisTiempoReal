import json
import requests
import sseclient
import streamlit as st
from datetime import datetime
import pandas as pd

# Realizamos la configuración de la página de Streamlit

st.set_page_config(
    page_title="Wikipedia Live Stream",
    page_icon="./images/wikilogo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Monitor de Datos en Tiempo Real: Cambios en Wikipedia")

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
                        nuevo_cambio = {
                            "Hora": datetime.now().strftime("%H:%M:%S"),
                            "Usuario": data.get('user'),
                            "Título": data.get('title'),
                            "Tipo": data.get('type')
                        }
                        
                        # Guardamos en el estado de la sesión (limitamos a los últimos 15)
                        st.session_state.lista_cambios.insert(0, nuevo_cambio)
                        st.session_state.lista_cambios = st.session_state.lista_cambios[:15]

                        # --- ACTUALIZACIÓN DE UI ---
                        
                        # Actualizar métrica
                        count_placeholder.metric("Ediciones detectadas", len(st.session_state.lista_cambios))
                        
                        # Actualizar tabla de forma fluida
                        df = pd.DataFrame(st.session_state.lista_cambios)
                        table_placeholder.table(df) # .table se ve más limpio para logs rápidos

                except json.JSONDecodeError:
                    continue
    except Exception as e:
        st.error(f"Error de conexión: {e}")


if st.button("Empezar a monitorizar"):
    stream_wikipedia()