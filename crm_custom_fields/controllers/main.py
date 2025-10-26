import json
from odoo import http
from odoo.http import request

# --- ¡CONFIGURA ESTO! ---
# IDs de etapas confirmados por ti:
STAGES_TO_EXCLUDE = [5, 6]  # Matriculados y No Interesados
MATRICULADO_STAGE_ID = 5    # ID específico de Matriculados para el desempate

# Ejemplo: SALESPERSON_IDS = [10, 12, 14]
SALESPERSON_IDS = [
    # Reemplaza con tus IDs de vendedores reales
    10, # ID de Vendedor A
    12, # ID de Vendedor B
    14, # ID de Vendedor C
]

# Esto es una clave secreta simple para que solo tu n8n pueda usar esta URL
# ¡Cámbiala por algo seguro y único!
AUTH_TOKEN = "tu-clave-secreta-para-n8n"
# --- FIN DE LA CONFIGURACIÓN ---


class LeadAssignmentController(http.Controller):

    @http.route('/api/v1/get_available_salesperson', type='http', auth='public', methods=['GET'], csrf=False)
    def get_available_salesperson(self, token=None, **kwargs):
        """
        Endpoint HTTP para encontrar el vendedor más disponible.
        
        LÓGICA:
        1. Encuentra el/los vendedores con MENOS clientes activos.
           (Activo = No está en "Matriculado" o "No Interesado").
        2. Si hay un empate, lo rompe asignando al que tenga MÁS clientes "Matriculados".
        
        Llamada de ejemplo desde n8n:
        GET https://tu-odoo.com/api/v1/get_available_salesperson?token=tu-clave-secreta-para-n8n
        """
        
        # 1. Seguridad: Verificar el token
        if not token or token != AUTH_TOKEN:
            return request.make_response(
                json.dumps({"status": 403, "error": "Token de autenticación inválido."}),
                headers=[('Content-Type', 'application/json')],
                status=403
            )

        try:
            # === PASO 1: Encontrar el mínimo de clientes ACTIVOS ===

            # Inicializar contadores para TODOS los vendedores (para incluir a los que tienen 0)
            active_counts = {user_id: 0 for user_id in SALESPERSON_IDS}

            # Definir el dominio de búsqueda para "clientes activos"
            domain_active = [
                ('user_id', 'in', SALESPERSON_IDS),
                ('stage_id', 'not in', STAGES_TO_EXCLUDE)
            ]

            # Ejecutar la consulta de conteo de activos
            active_leads_by_user = request.env['crm.lead'].sudo().read_group(
                domain=domain_active,
                fields=['user_id'],
                groupby=['user_id']
            )

            # Actualizar los contadores con los resultados
            for group in active_leads_by_user:
                user_id = group['user_id'][0]  # El ID del vendedor
                if user_id in active_counts:
                    active_counts[user_id] = group['user_id_count']
            
            # active_counts ahora se ve así: {10: 5, 12: 2, 14: 2}

            # === PASO 2: Identificar a los "Finalistas" (los que empatan con el mínimo) ===

            if not active_counts:
                 # Si no hay vendedores o la lista está vacía, devuelve un error
                 raise Exception("No se encontraron vendedores válidos en la lista SALESPERSON_IDS.")

            # Encontrar cuál es el número mínimo de clientes activos
            min_active_count = min(active_counts.values())

            # Crear una lista de "finalistas" (los que tienen ese número mínimo)
            finalists = [user_id for user_id, count in active_counts.items() if count == min_active_count]

            # === PASO 3: Decidir el ganador ===
            
            best_user_id = None

            if len(finalists) == 1:
                # Caso 1: No hay empate. El ganador es el único finalista.
                best_user_id = finalists[0]
            
            else:
                # Caso 2: ¡Hay un empate! Necesitamos el desempate.
                # (finalists se ve así: [12, 14])

                # Inicializar contadores de matriculados SOLO para los finalistas
                matriculado_counts = {finalist_id: 0 for finalist_id in finalists}
                
                # Dominio para contar matriculados SOLO de los finalistas
                domain_matriculado = [
                    ('user_id', 'in', finalists),
                    ('stage_id', '=', MATRICULADO_STAGE_ID)
                ]

                # Ejecutar la segunda consulta
                matriculado_leads_by_user = request.env['crm.lead'].sudo().read_group(
                    domain=domain_matriculado,
                    fields=['user_id'],
                    groupby=['user_id']
                )

                # Actualizar contadores de matriculados
                for group in matriculado_leads_by_user:
                    user_id = group['user_id'][0]
                    if user_id in matriculado_counts:
                        matriculado_counts[user_id] = group['user_id_count']

                # matriculado_counts se ve así: {12: 10, 14: 15}

                # Encontrar el ganador: el que tenga el MÁXIMO de matriculados
                best_user_id = max(matriculado_counts, key=matriculado_counts.get)
                # Si hay empate aquí también, max() devolverá el primero que encuentre.

            # === PASO 4: Devolver la respuesta ===
            
            response_data = {"status": 200, "user_id": best_user_id}
            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            # Manejar cualquier error inesperado
            response_data = {"status": 500, "error": str(e)}
            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')],
                status=500
            )