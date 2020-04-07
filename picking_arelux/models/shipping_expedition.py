# -*- coding: utf-8 -*-
from openerp import api, models, fields
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'
        
    @api.model
    def create(self, vals):
        record = super(ShippingExpedition, self).create(values)
        #order_id
        if record.picking_id.id>0:
            if record.picking_id.order_id.id>0:
                record.order_id = record.picking_id.order_id.id
                #user_id
                if record.order_id.user_id.id>0:
                    record.user_id = record.order_id.user_id.id
        #return
        return record        