# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
                    
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tsb_sender_center = fields.Char(
        string='TSB Centro'
    )        