{
    'name': 'POS Default Customer | POS Set Default Customer ',
    'summary': "Set Default Customer in POS",
    'description': 'Set Default Customer in POS',
    'category': 'Point of Sale',
    'version' : '16.3.2.1',    
    'sequence': 1,
    "author" : "DOTSPRIME",
    "email": 'dotsprime@gmail.com',
    "license": 'OPL-1',
    "price": 5,
    "currency": "USD",    
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'dps_pos_default_customer/static/src/js/get_customer.js',
        ],
    },
    'images': ['static/description/main_screenshot.png'],    
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
