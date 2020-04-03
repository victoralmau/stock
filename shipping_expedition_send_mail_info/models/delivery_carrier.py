# -*- coding: utf-8 -*-
from openerp import _, api, exceptions, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    send_mail_info = fields.Boolean(
        string='Send mail info' 
    )    
    mail_info_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Mail Info Plantilla'
    )