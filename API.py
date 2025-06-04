import requests  # Se importa la librería requests para hacer solicitudes HTTP.

# URL del servidor PHP que maneja la lógica del chatbot.
URL_PHP  = "https://leoviquez.com/IproyectoIntro/"

# Lista que almacena el historial de la conversación.
# Se inicia con un mensaje del sistema que define el comportamiento del asistente.
conversacion = [
    {"role": "system", "content": "Eres un asistente útil y conversacional."}
]

def chat_con_php(mensaje:str)->str:
    """
    Envía el historial de la conversación a un servidor PHP y recibe la respuesta del asistente.
    
    Args:
        mensaje (str): Entrada del usuario que será enviada al servidor.

    Returns:
        str: Respuesta generada por el asistente en el servidor PHP o mensaje de error.
    """
    # Se añade el mensaje del usuario al historial de la conversación.
    conversacion.append({"role": "user", "content": mensaje})

    try:
        # Se envía una solicitud POST al servidor PHP con el historial de conversación en formato JSON.
        respuesta = requests.post(URL_PHP, json={"messages": conversacion})
        
        # Se intenta convertir la respuesta en formato JSON.
        respuesta_json = respuesta.json()
        
        # Extrae el contenido de la respuesta generada por el asistente.
        mensaje_respuesta = respuesta_json["choices"][0]["message"]["content"]
        
        # Se añade la respuesta del asistente al historial de la conversación.
        conversacion.append({"role": "assistant", "content": mensaje_respuesta})
        
        return mensaje_respuesta  # Se retorna el mensaje de respuesta del asistente.
    
    except Exception as e:
        # En caso de error (por ejemplo, problemas de conexión), se devuelve un mensaje de error.
        return f"Error al conectar con el servidor: {e}"

