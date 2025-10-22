import requests
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# --- Configuración Centralizada de Chatwoot ---
# AHORA, TODOS LOS CAMBIOS DE CONFIGURACIÓN LOS HARÁS AQUÍ
CHATWOOT_URL = "https://app-n8n-chatwoot.essftr.easypanel.host"
CHATWOOT_API_TOKEN = "w7TS8qA8XVLkU3bo8m7E4i8E"
CHATWOOT_ACCOUNT_ID = 1 # Generalmente es 1 si solo tienes una instalación

def _get_headers():
    """Crea los encabezados de autenticación para la API de Chatwoot."""
    return {
        'Content-Type': 'application/json',
        'api_access_token': CHATWOOT_API_TOKEN
    }

def check_connection():
    """
    Verifica la conexión con la API de Chatwoot.
    Lanza UserError en caso de éxito o fracaso para notificar al usuario.
    """
    _logger.info("Chatwoot API: Verificando conexión...")
    # Usamos la API de 'agentes' (vendedores) para ver si responde
    test_url = f"{CHATWOOT_URL}/api/v1/agents"
    headers = _get_headers()

    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        agents_data = response.json().get('payload', [])
        agent_count = len(agents_data)
        
        raise UserError(f"¡ÉXITO! Conexión correcta con Chatwoot.\n\n"
                        f"Código: {response.status_code}\n"
                        f"Se encontraron {agent_count} agentes.")

    except requests.exceptions.HTTPError as e:
        error_details = f"Código: {e.response.status_code}\n"
        if e.response.status_code == 401:
            error_details += "Error: No autorizado. Revisa tu 'api_access_token' en el archivo chatwoot_api.py."
        elif e.response.status_code == 404:
            error_details += "Error: No encontrado. Revisa tu 'CHATWOOT_URL' en chatwoot_api.py. Asegúrate de que NO termine con '/api/v1'."
        else:
            error_details += f"Respuesta: {e.response.text}"
        raise UserError(f"¡ERROR DE CONEXIÓN! Chatwoot respondió con un error.\n\n{error_details}")

    except requests.exceptions.RequestException as e:
        _logger.error(f"Error de red al conectar con Chatwoot: {e}")
        raise UserError(f"¡ERROR DE RED! No se pudo conectar a Chatwoot.\n\n"
                        f"Revisa tu URL ({CHATWOOT_URL}) y la conexión a internet de tu servidor Odoo.\n"
                        f"Error técnico: {e}")