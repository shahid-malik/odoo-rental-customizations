# -*- coding: utf-8 -*-
{
    'name': "Mediod Sale Renting",
    'summary': """
        """,

    'description': """

    """,

    'author': "Mediod Consulting",
    'website': "https://www.mediodconsulting.com",
    'email': '',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    # 'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management','sale','mail','sale_renting'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/sale_order_inherit.xml',
    ],
    'assets': {
        'web.report_assets_common': [
        ],
    },
    # only loaded in demonstration mode
    'demo': [
    ],
}
