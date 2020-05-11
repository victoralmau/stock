# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    send_sms_info = fields.Boolean(
        string='Send sms info' 
    )    
    sms_info_sms_template_id = fields.Many2one(
        comodel_name='sms.template',
        string='Sms Info Plantilla'
    )