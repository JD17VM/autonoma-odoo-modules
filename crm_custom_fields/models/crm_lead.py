from odoo import models, fields, api
from markupsafe import Markup

from odoo.exceptions import UserError # Es buena práctica mantenerlo por si lo usas en el futuro.

import logging

# --- ESTA ES LA LÍNEA QUE FALTABA ---
# Importamos nuestro nuevo módulo para poder usar sus funciones.
from . import chatwoot_api
from . import chatwoot_sync

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    carrera_postulada = fields.Selection([
        #INGENIERÍAS
        ('ing-ing_quimica', 'Ing. Química'),
        ('ing-ing_ambiental', 'Ing. Ambiental'),
        ('ing-ing_materiales', 'Ing. de Materiales'),
        ('ing-ing_metalurgica', 'Ing. Metalúrgica'),
        ('ing-ing_industrias_alimentarias', 'Ing. de Industrias Alimentarias'),

        ('ing-ing_sistemas', 'Ing. de Sistemas'),
        ('ing-ing_electrica', 'Ing. Eléctrica'),
        ('ing-ing_electronica', 'Ing. Electrónica'),
        ('ing-ing_mecanica', 'Ing. Mecánica'),
        ('ing-ing_industrial', 'Ing. Industrial'),
        ('ing-cs_computacion', 'Ciencia de la Computación'),
        ('ing-ing_telecomunicaciones', 'Ing. de Telecomunicaciones'),

        ('ing-ing_geofisica', 'Ing. Geofísica'),
        ('ing-ing_geologica', 'Ing. Geológica'),
        ('ing-ing__minas', 'Ing. de Minas'),

        ('ing-ing_civil', 'Ing. Civil'),
        ('ing-ing_sanitaria', 'Ing. Sanitaria'),

        ('ing-fisica', 'Física'),
        ('ing-matematicas', 'Matemáticas'),
        ('ing-quimica', 'Química'),

        ('ing-arquitectura', 'Arquitectura'),

        #BIOMÉDICAS
        ('bio-biologia', 'Biología'),
        ('bio-cs_nutricion', 'Cs. de la Nutrición'),
        ('bio-ing_pesquera', 'Ing. Pesquera'),
        ('bio-medicina', 'Medicina'),
        ('bio-enfermeria', 'Enfermería'),
        ('bio-agronomia', 'Agronomía'),

        #SOCIALES
        ('soc-contabilidad', 'Contabilidad'),
        ('soc-finanzas', 'Finanzas'),
        ('soc-economia', 'Economía'),
        ('soc-derecho', 'Derecho'),
        ('soc-trabajo_social', 'Trabajo Social'),
        ('soc-antropologia', 'Antropología'),
        ('soc-turismo_hoteleria', 'Turismo y Hotelería'),
        ('soc-sociologia', 'Sociología'),
        ('soc-historia', 'Historia'),
        ('soc-psicologia', 'Psicología'),
        ('soc-relaciones_industriales', 'Relaciones Industriales'),
        ('soc-ciencias_comunicacion', 'Ciencias de la Comunicación'),
        ('soc-filosofia', 'Filosofía'),
        ('soc-literatura', 'Literatura'),
        ('soc-artes', 'Artes'),
        ('soc-administracion', 'Administración'),
        ('soc-marketing', 'Marketing'),
        ('soc-banca_seguros', 'Banca y Seguros'),
        ('soc-gestion_publica', 'Gestión Pública'),
        ('soc-gestion_empresas', 'Gestión de Empresas'),
        ('soc-educacion', 'Educacion'),
    ], string="Carrera Postulada")

    area = fields.Selection([
        ('ingenierias', 'Ingenierías'),
        ('sociales', 'Sociales'),
        ('biomedicas', 'Biomédicas')
    ], string="Área")

    servicio_educativo = fields.Selection([
        ('ord_2_pre_man', 'Ciclo Ordinario II - Presencial Mañana- 2026'),
        ('ord_2_pre_tar', 'Ciclo Ordinario II - Presencial Tarde - 2026'),
        ('cep_2_pre_man', 'Ciclo CEPRUNSA II - Presencial Mañana - 2026'),
        ('cep_2_pre_tar', 'Ciclo CEPRUNSA II - Presencial Tarde - 2026'),
        ('cep_2_vir_tar', 'Ciclo CEPRUNSA II - Virtual Tarde - 2026'),
        ('quint_pre_tar', 'Ciclo CEPRUNSA Quintos - Presencial Tarde - 2026'),
        ('quint_vir_tar', 'Ciclo CEPRUNSA Quintos - Virtual Tarde - 2026'),
        ('col_sec_esp', 'I.E.P Esparta (secundaria)')
    ], string="Servicio Educativo")

    universidad_postulada = fields.Selection([
        ('unsa', 'Universidad Nacional de San Agustín'),
        ('ucsp', 'Universidad Católica San Pablo'),
        ('ucsm', 'Universidad Católica Santa María'),
        ('otra', 'Otra Universidad'),
    ], string="Universidad Postulada", default='unsa')

    canal = fields.Selection([
        ('whatsapp_1', 'Whastapp 1'),
        ('whatsapp_2', 'Whastapp 2'),
        ('messenger', 'Messenger'),
        ('instagram', 'Instagram'),
        ('manual', 'Manual'),
    ], string="Canal", default='manual')


    canal_icon_html = fields.Html(
        string='Ícono del Canal',
        compute='_compute_canal_icon_html',
        sanitize=False,
        store=False
    )


    @api.depends('canal')
    def _compute_canal_icon_html(self):
        # Diccionario con las rutas de las imágenes por canal
        icon_map = {
            'whatsapp_1': '/crm_custom_fields/static/src/img/whatsapp-logo_num_1.png',
            'whatsapp_2': '/crm_custom_fields/static/src/img/whatsapp-logo_num_2.png',
            #'email': '/crm_custom_fields/static/src/img/email-logo.png',
            #'phone': '/crm_custom_fields/static/src/img/phone-logo.png',
            'messenger': '/crm_custom_fields/static/src/img/facebook-logo.png',
            'instagram': '/crm_custom_fields/static/src/img/instagram-logo.png',
            'manual': '/crm_custom_fields/static/src/img/notas-manuales-logo.png',
            #'web': '/crm_custom_fields/static/src/img/web-logo.png',
        }
        
        for record in self:
            if record.canal and record.canal in icon_map:
                record.canal_icon_html = f'''
                    <img src="{icon_map[record.canal]}" 
                         alt="{record.canal}"/>
                '''
            else:
                record.canal_icon_html = ''

    es_activo_autonoma_bot = fields.Boolean(
        string="Autonoma IA", 
        default=True  # Define el valor inicial por defecto
    )

    can_edit_owner = fields.Boolean(
        string="Puede Editar Vendedor",
        compute='_compute_can_edit_owner',
        store=False  # Debe ser dinámico, no almacenado
    )

    # ... (al final de tu clase, después de test_manual_sync) ...

    def _compute_can_edit_owner(self):
        """
        Comprueba si el usuario actual tiene permiso para editar el campo 'user_id'.
        """
        current_user = self.env.user
        
        # Comprobamos si el usuario es Gerente de Ventas
        is_manager = self.env.user.has_group('sales_team.group_sale_manager')

        for record in self:
            # Permitimos la edición SI:
            # 1. El registro aún no tiene propietario (es nuevo o no asignado)
            # 2. El usuario actual ES el propietario
            # 3. El usuario actual ES un Gerente de Ventas
            
            if (not record.user_id) or (record.user_id == current_user) or (is_manager):
                record.can_edit_owner = True
            else:
                record.can_edit_owner = False

    
    # -------------- HORA FECHA CREACION --------------

    # Campo original
    create_date = fields.Datetime('Fecha de Creación', readonly=True)

    # Campo 1: Solo la Fecha (Día y Mes)
    fecha_display = fields.Char(
        string='Día/Mes',
        compute='_compute_date_time_parts',
        store=False, # No es necesario almacenarlo en la DB
        search=False
    )

    # Campo 2: Solo la Hora
    hora_display = fields.Char(
        string='Hora',
        compute='_compute_date_time_parts',
        store=False,
        search=False
    )

    def _compute_date_time_parts(self):
        # Obtener el locale (idioma) del usuario actual para un formato correcto (ej: oct. vs oct)
        lang_code = self.env.context.get('lang')
        for record in self:
            if record.create_date:
                # 1. Convertir a datetime
                dt_obj = fields.Datetime.context_timestamp(record, record.create_date) # <-- LÍNEA CORREGIDA
                
                # 2. Formatear la fecha: '4 oct.'
                # Formato: Día abreviado del mes (ej. '%d %b.')
                record.fecha_display = dt_obj.strftime("%d %b.").lower()

                # 3. Formatear la hora: '1:04 p. m.'
                # Formato: Hora (12h) con minutos, con indicador AM/PM y minúsculas (ej. '%I:%M %p')
                # Nota: Odoo/Python manejan la conversión horaria del usuario.
                record.hora_display = dt_obj.strftime("%I:%M %p").lower()
            else:
                record.fecha_display = False
                record.hora_display = False



    ultima_hora_respuesta_general = fields.Datetime(
        string="Última Hora de Mensaje",
        store=True,
    )

    # Campo 1: Solo la Fecha (Día y Mes)
    fecha_display_respuesta = fields.Char(
        string='Día/Mes',
        compute='_compute_date_time_parts_respuesta',
        store=False, # No es necesario almacenarlo en la DB
        search=False
    )

    # Campo 2: Solo la Hora
    hora_display_respuesta = fields.Char(
        string='Hora',
        compute='_compute_date_time_parts_respuesta',
        store=False,
        search=False
    )

    def _compute_date_time_parts_respuesta(self):
        # Obtener el locale (idioma) del usuario actual para un formato correcto (ej: oct. vs oct)
        lang_code = self.env.context.get('lang')
        for record in self:
            if record.ultima_hora_respuesta_general:
                # 1. Convertir a datetime
                dt_obj = fields.Datetime.context_timestamp(record, record.ultima_hora_respuesta_general)
                
                # 2. Formatear la fecha: '4 oct.'
                # Formato: Día abreviado del mes (ej. '%d %b.')
                record.fecha_display_respuesta = dt_obj.strftime("%d %b.").lower()

                # 3. Formatear la hora: '1:04 p. m.'
                # Formato: Hora (12h) con minutos, con indicador AM/PM y minúsculas (ej. '%I:%M %p')
                # Nota: Odoo/Python manejan la conversión horaria del usuario.
                record.hora_display_respuesta = dt_obj.strftime("%I:%M %p").lower()
            else:
                record.fecha_display_respuesta = False
                record.hora_display_respuesta = False
    
    id_conversacion = fields.Integer(string="ID Conversación", index=True) # Agregar valor unico

    # ========== SINCRONIZACIÓN CON CHATWOOT ==========

    def write(self, vals):
        """
        SOBREESCRITO:
        1. (NUEVO) Bloquea la reasignación si el usuario actual no es el propietario.
        2. (Original) Detecta cuando cambia el vendedor y sincroniza con Chatwoot.
        """
        
        # --- INICIO DEL NUEVO BLOQUEO DE REASIGNACIÓN ---
        if 'user_id' in vals:
            # Recorremos cada oportunidad que se está intentando modificar
            for record in self:
                current_owner = record.user_id
                current_user = self.env.user
                
                # Verificamos si el usuario actual tiene permisos de Gerente de Ventas
                # 'sales_team.group_sale_manager' es el ID de grupo estándar de Odoo
                is_manager = self.env.user.has_group('sales_team.group_sale_manager')

                # CONDICIÓN DE BLOQUEO:
                # 1. La oportunidad TIENE un propietario (current_owner)
                # 2. El usuario actual NO es ese propietario (current_owner != current_user)
                # 3. El usuario actual TAMPOCO es un Gerente (not is_manager)
                if current_owner and current_owner != current_user and not is_manager:
                    # ¡Lanzamos un error y detenemos la operación!
                    raise UserError(
                        f"¡Reasignación Bloqueada!\n\n"
                        f"Solo {current_owner.name} (el vendedor asignado) o un "
                        f"Gerente de Ventas puede cambiar el propietario de esta oportunidad."
                    )
        # --- FIN DEL NUEVO BLOQUEO ---

        # Si pasa el bloqueo, continuamos con el 'write' original
        result = super(CrmLead, self).write(vals)
        
        # Si cambió el vendedor, sincronizamos
        if 'user_id' in vals:
            for record in self:
                _logger.info(f"Cambio de vendedor detectado en Lead {record.id}")
                
                # Sincronizar con Chatwoot
                sync_result = chatwoot_sync.sync_assignment_to_chatwoot(
                    lead=record,
                    new_user=record.user_id
                )
                
                # Mostrar resultado en el chatter
                record._notify_sync_result(sync_result)
        
        return result

    def _notify_sync_result(self, result):
        """
        Muestra el resultado de la sincronización en el chatter (versión simple).
        """
        if result['success']:
            # Caso Éxito
            body = Markup(
                f"<b>✅ Asignación sincronizada con Chatwoot</b><br/>"
                f"<strong>Vendedor:</strong> {self.user_id.name}<br/>"
                f"<strong>Email:</strong> {self.user_id.email}<br/>"
                f"<strong>ID Conversación:</strong> {self.id_conversacion}<br/>"
                f"<strong>ID Agente Chatwoot:</strong> {result['agent_id']}"
            )
        else:
            # Caso Error
            if result['found_agent']:
                icon = "⚠️"
                title = "Error de asignación en Chatwoot"
            else:
                icon = "❌"
                title = "Error crítico de sincronización"
            
            # Recopilar datos de forma segura
            vendedor = self.user_id.name if self.user_id else 'Sin asignar'
            email = self.user_id.email if self.user_id and self.user_id.email else 'No configurado'
            convo_id = self.id_conversacion if self.id_conversacion else 'No disponible'
            error_msg = result.get('message', 'Error desconocido.')

            body = Markup(
                f"<b>{icon} {title}</b><br/>"
                f"<strong>Error:</strong> {error_msg}<br/><br/>"
                f"<strong>Detalles del intento:</strong><br/>"
                f"<strong>Vendedor:</strong> {vendedor}<br/>"
                f"<strong>Email:</strong> {email}<br/>"
                f"<strong>ID Conversación:</strong> {convo_id}"
            )

        self.message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

    # ========== FUNCIÓN DE PRUEBA ==========

    def test_chatwoot_connection(self):
        """
        Prueba la conexión con Chatwoot.
        """
        chatwoot_api.check_connection()


    def test_manual_sync(self):
        """
        Prueba manual para ver si el código funciona.
        """
        _logger.info("🧪 BOTÓN DE PRUEBA PRESIONADO")
        
        if not self.user_id:
            raise UserError("❌ Este lead no tiene vendedor asignado")
        
        if not self.id_conversacion:
            raise UserError("❌ Este lead no tiene ID de conversación")
        
        _logger.info(f"Lead: {self.id}")
        _logger.info(f"Vendedor: {self.user_id.name}")
        _logger.info(f"Email: {self.user_id.email}")
        _logger.info(f"ID Conversación: {self.id_conversacion}")
        
        # Llamar a la sincronización
        sync_result = chatwoot_sync.sync_assignment_to_chatwoot(
            lead=self,
            new_user=self.user_id
        )
        
        # Mostrar resultado
        self._notify_sync_result(sync_result)
        
        raise UserError(f"✅ Prueba completada. Revisa el chatter para ver el resultado.\n\n{sync_result['message']}")


# Agrega esta función al final de tu clase CrmLead en models.py

def diagnosticar_vendedor_actual(self):
    """
    Botón de diagnóstico para el vendedor C o cualquier otro vendedor.
    Muestra información detallada en el chatter.
    """
    from . import chatwoot_sync
    
    if not self.user_id:
        raise UserError("❌ Este lead no tiene vendedor asignado")
    
    # Ejecutar diagnóstico
    resultado = chatwoot_sync.diagnosticar_vendedor(self.env, self.user_id.name)


def diagnostico_completo_lead(self):
    """
    🔍 DIAGNÓSTICO COMPLETO DE TODO EL PROBLEMA
    Identifica EXACTAMENTE por qué falla la asignación.
    """
    if not self.user_id:
        raise UserError("❌ Este lead no tiene vendedor asignado")
    
    if not self.id_conversacion:
        raise UserError("❌ Este lead no tiene ID de conversación")
    
    # Ejecutar diagnóstico completo
    resultado = chatwoot_api.diagnostico_completo_conversacion(
        conversation_id=self.id_conversacion,
        agent_email=self.user_id.email
    )
    
    # Construir mensaje
    mensaje = "<h3>🔍 DIAGNÓSTICO COMPLETO</h3>"
    mensaje += f"<b>Lead:</b> {self.name} (ID: {self.id})<br/>"
    mensaje += f"<b>Vendedor:</b> {self.user_id.name}<br/>"
    mensaje += f"<b>Email:</b> {self.user_id.email}<br/>"
    mensaje += f"<b>ID Conversación:</b> {self.id_conversacion}<br/><br/>"
    
    # Estado de la conversación
    if resultado['conversacion_existe']:
        conv_info = resultado['conversacion_info']
        mensaje += f"✅ <b>Conversación:</b> EXISTE<br/>"
        mensaje += f"   • Inbox ID: {conv_info['inbox_id']}<br/>"
        mensaje += f"   • Status: {conv_info['status']}<br/>"
        mensaje += f"   • Asignado a: {conv_info['assignee_id'] or 'Sin asignar'}<br/><br/>"
    else:
        mensaje += f"❌ <b>Conversación:</b> NO EXISTE<br/><br/>"
    
    # Estado del agente
    if resultado['agente_existe']:
        mensaje += f"✅ <b>Agente:</b> EXISTE (ID: {resultado['agent_id']})<br/>"
        if resultado['agente_tiene_acceso']:
            mensaje += f"✅ <b>Acceso a Inbox:</b> SÍ<br/><br/>"
        else:
            mensaje += f"❌ <b>Acceso a Inbox:</b> NO<br/><br/>"
    else:
        mensaje += f"❌ <b>Agente:</b> NO EXISTE<br/><br/>"
    
    # Problemas detectados
    if resultado['problemas']:
        mensaje += "<h4>⚠️ PROBLEMAS DETECTADOS:</h4><ul>"
        for problema in resultado['problemas']:
            mensaje += f"<li>{problema}</li>"
        mensaje += "</ul>"
    
    # Soluciones
    if resultado['soluciones']:
        mensaje += "<h4>💡 SOLUCIONES:</h4><ul>"
        for solucion in resultado['soluciones']:
            mensaje += f"<li>{solucion}</li>"
        mensaje += "</ul>"
    
    self.message_post(
        body=Markup(mensaje),
        message_type='comment',
        subtype_xmlid='mail.mt_note'
    )
    
    # Resumen en popup
    resumen = "✅ TODO OK" if not resultado['soluciones'] else "❌ PROBLEMAS ENCONTRADOS"
    raise UserError(f"{resumen}\n\nRevisa el chatter para ver el diagnóstico completo.")
    
    # Construir mensaje para el chatter
    mensaje = f"<h3>🔍 DIAGNÓSTICO DEL VENDEDOR</h3>"
    mensaje += f"<b>Vendedor:</b> {resultado['vendedor_nombre']}<br/>"
    mensaje += f"<b>ID Odoo:</b> {resultado['vendedor_id']}<br/>"
    mensaje += f"<b>Email:</b> {resultado['vendedor_email'] or '❌ SIN EMAIL'}<br/>"
    mensaje += f"<b>Email válido:</b> {'✅ Sí' if resultado['email_valido'] else '❌ No'}<br/>"
    
    if resultado['agente_chatwoot']:
        mensaje += f"<b>Agente Chatwoot:</b> ✅ Encontrado (ID: {resultado['agente_chatwoot']})<br/>"
    else:
        mensaje += f"<b>Agente Chatwoot:</b> ❌ NO encontrado en Chatwoot<br/>"
    
    mensaje += f"<br/><b>Leads asignados:</b> {len(resultado['leads_asignados'])}<br/>"
    
    # Mostrar problemas
    if resultado['problemas']:
        mensaje += "<br/><h4>⚠️ PROBLEMAS DETECTADOS:</h4><ul>"
        for problema in resultado['problemas']:
            mensaje += f"<li>{problema}</li>"
        mensaje += "</ul>"
    else:
        mensaje += "<br/>✅ No se detectaron problemas con este vendedor"
    
    # Mostrar info de leads
    if resultado['leads_asignados']:
        mensaje += "<br/><h4>📋 Detalle de Leads:</h4><ul>"
        for lead_info in resultado['leads_asignados'][:5]:  # Mostrar solo los primeros 5
            mensaje += f"<li>Lead {lead_info['lead_id']}: {lead_info['lead_nombre']} - "
            if lead_info['tiene_conversacion']:
                mensaje += f"✅ Conversación: {lead_info['id_conversacion']}"
            else:
                mensaje += f"❌ {lead_info.get('problema', 'Sin conversación')}"
            mensaje += "</li>"
        if len(resultado['leads_asignados']) > 5:
            mensaje += f"<li>... y {len(resultado['leads_asignados']) - 5} más</li>"
        mensaje += "</ul>"
    
    # Publicar en el chatter
    self.message_post(
        body=Markup(mensaje),
        message_type='comment',
        subtype_xmlid='mail.mt_note'
    )
    
    # También mostrar en popup
    raise UserError(f"✅ Diagnóstico completado. Revisa el chatter para ver los resultados.\n\n"
                   f"Vendedor: {resultado['vendedor_nombre']}\n"
                   f"Email: {resultado['vendedor_email']}\n"
                   f"Agente Chatwoot: {'✅ Encontrado' if resultado['agente_chatwoot'] else '❌ NO encontrado'}")