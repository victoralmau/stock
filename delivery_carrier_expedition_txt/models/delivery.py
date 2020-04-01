# -*- coding: utf-8 -*-
from openerp import api, models, fields

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.model
    def _get_carrier_type_selection(self):
        """ Add txt carrier type """
        res = super(DeliveryCarrier, self)._get_carrier_type_selection()
        res.append(('txt', 'TXT'),)
        return res