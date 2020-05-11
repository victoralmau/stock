# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)
                    
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Transportista'
    )        