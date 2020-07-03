# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
                    
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tsb_sender_center = fields.Char(
        string='TSB Centro'
    )        