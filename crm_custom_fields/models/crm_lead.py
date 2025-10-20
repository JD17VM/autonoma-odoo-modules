from odoo import models, fields, api
from odoo.exceptions import UserError  # <--- Importado para los pop-ups
import requests                      # <--- Importado para la API
import logging                       # <--- Importado para logs

_logger = logging.getLogger(__name__)

# --- Configuración de Chatwoot ---
# RECUERDA CAMBIAR ESTOS VALORES
CHATWOOT_URL = "https://app-n8n-chatwoot.essftr.easypanel.host"
CHATWOOT_API_TOKEN = "w7TS8qA8XVLkU3bo8m7E4i8E"

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


    # --- FUNCIONES DE PRUEBA DE CHATWOOT ---
    # (Las pegamos aquí, dentro de la misma clase)

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