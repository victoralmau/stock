# -*- coding: utf-8 -*-
from openerp import _, api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'        

    cbl_sender_customer = fields.Char(
        string='Cbl sender customer'
    )                                                                                               