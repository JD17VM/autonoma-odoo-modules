import requests
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# --- Configuración Centralizada de Chatwoot ---
CHATWOOT_URL = "https://app-n8n-chatwoot.essftr.easypanel.host"
CHATWOOT_API_TOKEN = "w7TS8qA8XVLkU3bo8m7E4i8E"
CHATWOOT_ACCOUNT_ID = 2  # Cambiado a 2 basado en tu sugerencia

def _get_headers():
    """Crea los encabezados de autenticación para la API de Chatwoot."""
    return {
        'Content-Type': 'application/json',
        'api_access_token': CHATWOOT_API_TOKEN
    }


def _auto_detect_account_id():
    """
    Intenta detectar automáticamente el Account ID correcto.
    Prueba con IDs del 1 al 10.
    Retorna el primer ID que funcione, o None si ninguno funciona.
    """
    headers = _get_headers()
    
    for account_id in range(1, 11):
        try:
            test_url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/agents"
            response = requests.get(test_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                _logger.info(f"✓ Account ID detectado automáticamente: {account_id}")
                return account_id
        except:
            continue
    
    return None

def check_connection():
    """
    Verifica la conexión con la API de Chatwoot.
    Detecta automáticamente el Account ID correcto si el configurado no funciona.
    Lanza UserError en caso de éxito o fracaso para notificar al usuario.
    """
    _logger.info("Chatwoot API: Verificando conexión...")
    
    # Intentar con el Account ID configurado
    test_url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/agents"
    headers = _get_headers()

    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Chatwoot devuelve directamente la lista de agentes, no en 'payload'
        agents_data = response.json()
        agent_count = len(agents_data) if isinstance(agents_data, list) else 0
        
        # Mostrar información de los agentes encontrados
        agent_info = "\n\n✅ Agentes encontrados:\n"
        if isinstance(agents_data, list):
            for agent in agents_data:
                agent_info += f"  • {agent.get('name', 'Sin nombre')} (Email: {agent.get('email', 'N/A')}, ID: {agent.get('id', 'N/A')})\n"
        
        raise UserError(f"🎉 ¡ÉXITO! Conexión correcta con Chatwoot.\n\n"
                        f"📍 URL: {test_url}\n"
                        f"✓ Código: {response.status_code}\n"
                        f"✓ Account ID: {CHATWOOT_ACCOUNT_ID}\n"
                        f"✓ Total de agentes: {agent_count}{agent_info}")

    except requests.exceptions.HTTPError as e:
        # Si es error 404, intentar detectar el Account ID correcto
        if e.response.status_code == 404:
            _logger.warning(f"Account ID {CHATWOOT_ACCOUNT_ID} no funciona, intentando detectar automáticamente...")
            detected_id = _auto_detect_account_id()
            
            if detected_id:
                error_details = f"❌ El ACCOUNT_ID configurado ({CHATWOOT_ACCOUNT_ID}) no existe.\n\n"
                error_details += f"✅ SOLUCIÓN ENCONTRADA:\n"
                error_details += f"   Tu Account ID correcto es: {detected_id}\n\n"
                error_details += f"Cambia esta línea en chatwoot_api.py:\n"
                error_details += f"   CHATWOOT_ACCOUNT_ID = {detected_id}\n"
            else:
                error_details = f"❌ El ACCOUNT_ID {CHATWOOT_ACCOUNT_ID} no existe.\n\n"
                error_details += f"URL intentada: {test_url}\n\n"
                error_details += f"Posibles soluciones:\n"
                error_details += f"1. Ve a tu Chatwoot → Settings → Account Settings\n"
                error_details += f"2. O mira la URL cuando estés en Chatwoot: .../app/accounts/X/...\n"
                error_details += f"3. Ese número 'X' es tu Account ID correcto\n"
        else:
            error_details = f"URL intentada: {test_url}\n"
            error_details += f"Código: {e.response.status_code}\n"
            
            if e.response.status_code == 401:
                error_details += "\n❌ Error: No autorizado.\n"
                error_details += "Solución: Revisa tu 'CHATWOOT_API_TOKEN' en chatwoot_api.py.\n"
                error_details += "Debes usar un token de API válido (no un token de acceso personal)."
            else:
                try:
                    error_details += f"\nRespuesta del servidor:\n{e.response.json()}"
                except:
                    error_details += f"\nRespuesta del servidor:\n{e.response.text}"
        
        raise UserError(f"¡ERROR DE CONEXIÓN! Chatwoot respondió con un error.\n\n{error_details}")

    except requests.exceptions.RequestException as e:
        _logger.error(f"Error de red al conectar con Chatwoot: {e}")
        raise UserError(f"¡ERROR DE RED! No se pudo conectar a Chatwoot.\n\n"
                        f"URL intentada: {test_url}\n"
                        f"Revisa:\n"
                        f"1. La URL base: {CHATWOOT_URL}\n"
                        f"2. La conexión a internet de tu servidor Odoo\n"
                        f"3. Que no haya firewall bloqueando la conexión\n\n"
                        f"Error técnico: {e}")


def get_agent_by_email(email):
    """
    Busca un agente en Chatwoot por su correo electrónico.
    Retorna el ID del agente si lo encuentra, None si no existe.
    """
    _logger.info(f"Chatwoot API: Buscando agente con email '{email}'...")
    
    url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/agents"
    headers = _get_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        agents = response.json()
        
        if isinstance(agents, list):
            for agent in agents:
                if agent.get('email', '').lower() == email.lower():
                    _logger.info(f"✓ Agente encontrado: {agent.get('name')} (ID: {agent.get('id')})")
                    return agent.get('id')
        
        _logger.warning(f"✗ No se encontró ningún agente con el email '{email}'")
        return None
        
    except Exception as e:
        _logger.error(f"Error al buscar agente en Chatwoot: {e}")
        return None


def assign_conversation_to_agent(conversation_id, agent_id):
    """
    Asigna una conversación de Chatwoot a un agente específico.
    
    Args:
        conversation_id (int): ID de la conversación en Chatwoot
        agent_id (int): ID del agente en Chatwoot
    
    Returns:
        bool: True si la asignación fue exitosa, False en caso contrario
    """
    _logger.info(f"Chatwoot API: Asignando conversación {conversation_id} al agente {agent_id}...")
    
    url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/assignments"
    headers = _get_headers()
    
    payload = {
        "assignee_id": agent_id
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        _logger.info(f"✓ Conversación {conversation_id} asignada exitosamente al agente {agent_id}")
        return True
        
    except requests.exceptions.HTTPError as e:
        _logger.error(f"Error HTTP al asignar conversación: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        _logger.error(f"Error al asignar conversación en Chatwoot: {e}")
        return False