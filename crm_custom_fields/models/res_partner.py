# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

# --- Configuración de Chatwoot ---
# RECUERDA CAMBIAR ESTOS VALORES
CHATWOOT_URL = "https://app-n8n-chatwoot.essftr.easypanel.host"
CHATWOOT_API_TOKEN = "w7TS8qA8XVLkU3bo8m7E4i8E"

class CrmLead(models.Model):
    # Heredamos de Oportunidades/Prospectos
    _inherit = 'crm.lead' 

    def _get_chatwoot_headers(self):
        """
        Helper para crear los encabezados de autenticación.
        """
        return {
            'Content-Type': 'application/json',
            'api_access_token': CHATWOOT_API_TOKEN
        }

    def test_chatwoot_connection(self):
        """
        Esta es nuestra primera función de prueba.
        La llamará el botón "Probar Conexión Chatwoot (Test)"
        """
        _logger.info("Chatwoot: Iniciando prueba de conexión...")
        
        # Usamos la API de 'agentes' (vendedores) para ver si responde
        test_url = f"{CHATWOOT_URL}/api/v1/agents"
        headers = self._get_chatwoot_headers()

        try:
            # Intentamos conectarnos
            response = requests.get(test_url, headers=headers, timeout=10)
            
            # Comprobación básica de éxito
            if response.ok:
                agents_data = response.json()
                agent_count = len(agents_data)
                # Si todo sale bien, muestra un pop-up de éxito
                raise UserError(f"¡ÉXITO! Conexión correcta con Chatwoot.\n\n"
                                f"Código: {response.status_code}\n"
                                f"Se encontraron {agent_count} agentes.")
            else:
                # Si Chatwoot devuelve un error (ej. 401 Token Inválido)
                raise UserError(f"¡ERROR DE CONEXIÓN! Chatwoot respondió.\n\n"
                                f"Código: {response.status_code}\n"
                                f"Error: {response.text}")

        except Exception as e:
            # Error de red, URL incorrecta, timeout, etc.
            raise UserError(f"¡ERROR! No se pudo conectar.\n\n"
                            f"Revisa tu URL y que Odoo pueda acceder a ella.\n"
                            f"Error: {e}")