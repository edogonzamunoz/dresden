# -*- coding: utf-8 -*-
{
    'name': "Pos Extend",

    'summary': """
        Herencia del l10n_cl_edi para modificar el template del xml de envio al sii""",

    'description': """
        Herencia del l10n_cl_edi para modificar el template del xml de envio al sii
    """,

    'author': "Yeniel Leon Ferre",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'point_of_sale', 'l10n_cl_edi'],

    # always loaded
    'data': [
        'template/dte_template.xml',
        'template/dd_template.xml',
        'template/envio_dte_template.xml',
        'data/action_delete_attachment.xml'
    ],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
