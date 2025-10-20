# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

# --- Configuración de Chatwoot ---
# MEJORA: Mueve esto a los Parámetros del Sistema (ir.config_parameter)
# para no tenerlos "hardcodeados" en el código.
CHATWOOT_URL = "https://chatwoot.tudominio.com"  # Reemplaza con tu URL
CHATWOOT_API_TOKEN = "TU_API_TOKEN_DE_ADMINISTRADOR" # Reemplaza con tu Token

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        """
        Hereda el método write. Se dispara cada vez que se edita un contacto.
        """
        # 1. Obtenemos el vendedor *antes* del cambio (si existe)
        salesperson_before = self.user_id if self.ensure_one() else False

        # 2. Ejecuta la escritura normal de Odoo.
        res = super(ResPartner, self).write(vals)

        # 3. Comprueba si el 'user_id' (Vendedor) estaba en los valores a cambiar.
        if 'user_id' in vals:
            # Nos aseguramos de que estamos trabajando con un solo registro
            if self.ensure_one():
                salesperson_after = self.user_id
                
                # ¡Se asignó o cambió un vendedor!
                if salesperson_after:
                    _logger.info(f"Chatwoot: Vendedor cambiado para {self.name}. Invocando asignación.")
                    try:
                        self._assign_chatwoot_conversation(salesperson_after)
                    except Exception as e:
                        _logger.error(f"Chatwoot: Error al asignar: {e}")
                
                # Se quitó el vendedor, desasignamos en Chatwoot
                elif salesperson_before:
                     _logger.info(f"Chatwoot: Vendedor quitado para {self.name}. Invocando desasignación.")
                     try:
                        self._unassign_chatwoot_conversation()
                     except Exception as e:
                        _logger.error(f"Chatwoot: Error al desasignar: {e}")

        return res

    def _get_chatwoot_headers(self):
        """Helper para los headers de la API"""
        return {
            'Content-Type': 'application/json',
            'api_access_token': CHATWOOT_API_TOKEN
        }

    def _find_chatwoot_agent_id(self, agent_email):
        """
        Busca el ID de un Agente en Chatwoot usando su email.
        """
        if not agent_email:
            return None
        
        url = f"{CHATWOOT_URL}/api/v1/agents/search?q={agent_email}"
        response = requests.get(url, headers=self._get_chatwoot_headers())
        response.raise_for_status() # Lanza error si la API falla
        
        agents = response.json()
        if agents:
            # Asume que el primer resultado es el correcto
            return agents[0].get('id')
        return None

    def _find_chatwoot_contact_id(self, contact_email):
        """
        Busca el ID de un Contacto en Chatwoot usando su email.
        """
        if not contact_email:
            return None
            
        url = f"{CHATWOOT_URL}/api/v1/contacts/search?q={contact_email}"
        response = requests.get(url, headers=self._get_chatwoot_headers())
        response.raise_for_status()
        
        # El search de contactos devuelve un payload diferente
        contacts = response.json().get('payload', [])
        if contacts:
            return contacts[0].get('id')
        return None

    def _assign_chatwoot_conversation(self, salesperson):
        """
        Lógica principal: Busca y asigna las conversaciones.
        """
        self.ensure_one() # Asegura que solo procesamos un partner

        agent_email = salesperson.login
        contact_email = self.email

        if not agent_email or not contact_email:
            _logger.warning("Chatwoot: Falta email de agente o contacto.")
            return

        # 1. Identificador del Vendedor (Agente)
        agent_id = self._find_chatwoot_agent_id(agent_email)
        if not agent_id:
            _logger.error(f"Chatwoot: Agente con email {agent_email} NO encontrado.")
            return

        # 2. Identificador del Cliente (Contacto)
        contact_id = self._find_chatwoot_contact_id(contact_email)
        if not contact_id:
            _logger.info(f"Chatwoot: Contacto {contact_email} no tiene chat. No se asigna nada.")
            return

        # 3. Listar todas las conversaciones "abiertas" de ese contacto
        conv_url = f"{CHATWOOT_URL}/api/v1/contacts/{contact_id}/conversations"
        conv_response = requests.get(conv_url, headers=self._get_chatwoot_headers())
        conv_response.raise_for_status()
        
        conversations = conv_response.json().get('payload', [])
        open_conversations = [c for c in conversations if c.get('status') == 'open']

        if not open_conversations:
            _logger.info(f"Chatwoot: Contacto {contact_email} no tiene chats abiertos.")
            return

        # 4. Asignar cada conversación abierta
        for conversation in open_conversations:
            # 5. Identificador del Chat (Conversación)
            conversation_id = conversation.get('id')
            
            assign_url = f"{CHATWOOT_URL}/api/v1/conversations/{conversation_id}/assignments"
            payload = {
                "assignee_id": agent_id
            }
            assign_response = requests.post(assign_url, json=payload, headers=self._get_chatwoot_headers())
            
            if assign_response.status_code == 200:
                _logger.info(f"Chatwoot: ÉXITO. Chat {conversation_id} asignado a Agente {agent_id}.")
            else:
                _logger.error(f"Chatwoot: FALLO al asignar chat {conversation_id}: {assign_response.text}")

    def _unassign_chatwoot_conversation(self):
        """
        Quita la asignación de las conversaciones abiertas.
        """
        # Esta lógica es casi idéntica, pero el payload es diferente
        contact_id = self._find_chatwoot_contact_id(self.email)
        if not contact_id:
            return # No hay contacto, no hay nada que desasignar

        conv_url = f"{CHATWOOT_URL}/api/v1/contacts/{contact_id}/conversations"
        conv_response = requests.get(conv_url, headers=self._get_chatwoot_headers())
        if not conv_response.ok: return

        conversations = conv_response.json().get('payload', [])
        open_conversations = [c for c in conversations if c.get('status') == 'open']

        for conversation in open_conversations:
            conversation_id = conversation.get('id')
            assign_url = f"{CHATWOOT_URL}/api/v1/conversations/{conversation_id}/assignments"
            payload = {
                "assignee_id": 0  # 0 significa "desasignar" o "enviar a la cola"
            }
            requests.post(assign_url, json=payload, headers=self._get_chatwoot_headers())
            _logger.info(f"Chatwoot: Chat {conversation_id} desasignado.")