{
    'name': 'CRM Custom Fields',
    'version': '1.1',
    'summary': 'Añade campos personalizados al formulario de CRM.',
    'author': 'Tu Nombre',
    'depends': ['crm', 'web'],
    'data': [
        'views/nuevo.xml',
        'views/crm_lead_form_view.xml',
        'views/crm_lead_kanban_view.xml',
        'views/favicon_inherit.xml',
        #'views/header_mod.xml',
    ],
    'installable': True,
    'assets': {
        'web.assets_backend': [
            # 'prepend' asegura que tu archivo de variables se cargue PRIMERO.
            ('prepend', 'crm_custom_fields/static/src/scss/primary_variables.scss'),

            'crm_custom_fields/static/src/css/style.css',
            'crm_custom_fields/static/src/scss/kanban_style.scss'
        ],
    },
}