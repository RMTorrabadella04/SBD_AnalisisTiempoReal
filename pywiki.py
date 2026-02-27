import json
import requests
import sseclient

def stream_wikipedia():
    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    
    # El User-Agent es CLAVE para que no de el error 403
    headers = {
        'User-Agent': 'SBD_Analisis_Raul/1.0 (ProyectoEstudiante; contacto: raul@ejemplo.com)'
    }

    print("--- Intentando conectar con el servidor de Wikimedia ---")
    
    try:
        # stream=True permite leer los datos mientras llegan
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        client = sseclient.SSEClient(response)

        print("--- ¡CONECTADO! Escuchando cambios en la Wikipedia en español... ---\n")

        for event in client.events():
            if event.event == 'message':
                try:
                    data = json.loads(event.data)
                    
                    # Filtramos por la Wikipedia en español
                    if data.get('server_name') == 'es.wikipedia.org':
                        user = data.get('user')
                        title = data.get('title')
                        print(f"-> [EDIT] {user} ha editado: {title}")
                
                except json.JSONDecodeError:
                    continue

    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar. Revisa tu internet.")
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")

if __name__ == "__main__":
    stream_wikipedia()
