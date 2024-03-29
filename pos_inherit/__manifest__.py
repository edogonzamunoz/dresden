# -*- coding: utf-8 -*-
{
    'name': "Pos",

    'summary': """
        Herencia del pos""",

    'description': """
        Herencia del pos
    """,

    'author': "Yeniel Leon Ferre",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'point_of_sale', 'l10n_cl_edi', 'l10n_cl_edi_boletas'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/journal_data.xml',
        'views/account_journal_views.xml',
        'views/pos_config_inherit.xml',
        'views/report_invoice_ticket.xml',
        'views/report_pos_receipt.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_inherit/static/src/js/models.js',
            'pos_inherit/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'pos_inherit/static/src/xml/**/*.xml',
            'pos_inherit/static/src/css/style.css',
        ]
    },
    'license': "AGPL-3",
    'installable': True,
    'application': False,
}
