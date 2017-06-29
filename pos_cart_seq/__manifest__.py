{
    'name': "POS Cart Sequence",
    'summary': """
        Add sequence number in cart and receipt""",
    'description': """
        Add sequence number in cart and receipt
    """,
    'category': 'Point of Sale',
    'version': '1.0',
    'author': 'Shelton',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_cart_seq_templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'application': True,
}
