"""
Módulo de sincronización entre Odoo CRM y Chatwoot.
Versión simple: Solo asigna vendedor cuando cambia.
"""

import logging
from . import chatwoot_api

_logger = logging.getLogger(__name__)


def sync_assignment_to_chatwoot(lead, new_user):
    """
    Sincroniza la asignación de un vendedor de Odoo a Chatwoot.
    Versión simple y directa.
    
    Args:
        lead: Objeto crm.lead de Odoo
        new_user: Usuario (vendedor) recién asignado
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'found_agent': bool,
            'agent_id': int or None
        }
    """
    _logger.info(f"🔄 Iniciando sincronización para Lead {lead.id}")
    
    # Validación 1: ¿Tiene ID de conversación?
    if not lead.id_conversacion:
        _logger.warning(f"Lead {lead.id} no tiene ID de conversación")
        return {
            'success': False,
            'message': 'Este lead no tiene ID de conversación de Chatwoot',
            'found_agent': False,
            'agent_id': None
        }
    
    # Validación 2: ¿Tiene vendedor asignado?
    if not new_user:
        _logger.info(f"Lead {lead.id} fue desasignado (sin vendedor)")
        return {
            'success': False,
            'message': 'No hay vendedor asignado',
            'found_agent': False,
            'agent_id': None
        }
    
    # Validación 3: ¿El vendedor tiene email?
    if not new_user.email:
        _logger.error(f"Vendedor {new_user.name} no tiene email configurado")
        return {
            'success': False,
            'message': f"El vendedor '{new_user.name}' no tiene email configurado en Odoo",
            'found_agent': False,
            'agent_id': None
        }
    
    # Paso 1: Buscar agente en Chatwoot
    _logger.info(f"🔍 Buscando agente con email: {new_user.email}")
    agent_id = chatwoot_api.get_agent_by_email(new_user.email)
    
    if not agent_id:
        _logger.error(f"❌ No se encontró agente con email: {new_user.email}")
        return {
            'success': False,
            'message': f"No se encontró un agente en Chatwoot con el email '{new_user.email}'",
            'found_agent': False,
            'agent_id': None
        }
    
    _logger.info(f"✓ Agente encontrado - ID: {agent_id}")
    
    # Paso 2: Asignar conversación
    _logger.info(f"📞 Asignando conversación {lead.id_conversacion} al agente {agent_id}")
    success = chatwoot_api.assign_conversation_to_agent(lead.id_conversacion, agent_id)
    
    if success:
        _logger.info(f"✅ Asignación exitosa")
        return {
            'success': True,
            'message': f"Conversación asignada exitosamente a '{new_user.name}'",
            'found_agent': True,
            'agent_id': agent_id
        }
    else:
        _logger.error(f"❌ Error al asignar conversación")
        return {
            'success': False,
            'message': 'Error al asignar la conversación en Chatwoot',
            'found_agent': True,
            'agent_id': agent_id
        }

def diagnosticar_vendedor(odoo_env, vendedor_name):
    """
    Función de diagnóstico para identificar problemas con un vendedor específico.
    """
    _logger.info(f"🔍 Diagnosticando vendedor: {vendedor_name}")
    
    vendedor = odoo_env['res.users'].search([('name', '=', vendedor_name)], limit=1)
    
    if not vendedor:
        return {'error': f"Vendedor '{vendedor_name}' no encontrado"}
    
    resultado = {
        'vendedor_id': vendedor.id,
        'vendedor_nombre': vendedor.name,
        'vendedor_email': vendedor.email,
        'email_valido': bool(vendedor.email),
        'leads_asignados': [],
        'agente_chatwoot': None,
        'problemas': []
    }
    
    if not vendedor.email:
        resultado['problemas'].append("❌ Sin email configurado")
    else:
        agent_id = chatwoot_api.get_agent_by_email(vendedor.email)
        resultado['agente_chatwoot'] = agent_id
        if not agent_id:
            resultado['problemas'].append(f"❌ Email '{vendedor.email}' no existe en Chatwoot")
    
    # Buscar leads
    leads = odoo_env['crm.lead'].search([('user_id', '=', vendedor.id)])
    for lead in leads:
        lead_info = {
            'lead_id': lead.id,
            'lead_nombre': lead.name,
            'id_conversacion': lead.id_conversacion,
            'tiene_conversacion': bool(lead.id_conversacion and lead.id_conversacion > 0)
        }
        if not lead_info['tiene_conversacion']:
            lead_info['problema'] = "Sin ID de conversación válido"
        resultado['leads_asignados'].append(lead_info)
    
    return resultado