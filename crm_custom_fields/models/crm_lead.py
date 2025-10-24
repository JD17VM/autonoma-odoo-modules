from odoo import models, fields, api

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

    canal = fields.Selection([
        ('whatsapp_1', 'Whastapp 1'),
        ('whatsapp_2', 'Whastapp 2'),
        ('messenger', 'Messenger'),
        ('instagram', 'Instagram'),
        ('manual', 'Manual'),
    ], string="Canal")


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
                dt_obj = record.ultima_hora_respuesta_general
                
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
        Detecta cuando cambia el vendedor y sincroniza con Chatwoot.
        """
        # Ejecutamos el write original primero
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
        Muestra el resultado de la sincronización en el chatter.
        """
        if result['success']:
            # ✅ ÉXITO
            self.message_post(
                body=f"<div style='padding: 10px; background-color: #d4edda; border-left: 4px solid #28a745;'>"
                    f"<h4 style='margin: 0 0 10px 0; color: #155724;'>✅ Asignación sincronizada con Chatwoot</h4>"
                    f"<p style='margin: 5px 0;'><strong>Vendedor:</strong> {self.user_id.name}</p>"
                    f"<p style='margin: 5px 0;'><strong>Email:</strong> {self.user_id.email}</p>"
                    f"<p style='margin: 5px 0;'><strong>ID Conversación:</strong> {self.id_conversacion}</p>"
                    f"<p style='margin: 5px 0;'><strong>ID Agente Chatwoot:</strong> {result['agent_id']}</p>"
                    f"</div>",
                subject="Sincronización exitosa",
                message_type='notification'
            )
        else:
            # ❌ ERROR
            if result['found_agent']:
                icon = "⚠️"
                color = "#fff3cd"
                border_color = "#ffc107"
                text_color = "#856404"
            else:
                icon = "❌"
                color = "#f8d7da"
                border_color = "#dc3545"
                text_color = "#721c24"
            
            self.message_post(
                body=f"<div style='padding: 10px; background-color: {color}; border-left: 4px solid {border_color};'>"
                    f"<h4 style='margin: 0 0 10px 0; color: {text_color};'>{icon} Error en sincronización con Chatwoot</h4>"
                    f"<p style='margin: 5px 0;'><strong>Vendedor:</strong> {self.user_id.name if self.user_id else 'Sin asignar'}</p>"
                    f"<p style='margin: 5px 0;'><strong>Email:</strong> {self.user_id.email if self.user_id and self.user_id.email else 'No configurado'}</p>"
                    f"<p style='margin: 5px 0;'><strong>ID Conversación:</strong> {self.id_conversacion if self.id_conversacion else 'No disponible'}</p>"
                    f"<p style='margin: 10px 0 5px 0; color: {text_color};'><strong>Error:</strong> {result['message']}</p>"
                    f"</div>",
                subject="Error de sincronización",
                message_type='notification'
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