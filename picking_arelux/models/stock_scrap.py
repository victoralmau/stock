# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)

class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    cost = fields.Float(
        compute='_cost',
        string='Coste',
        store=False
    )
    
    @api.one        
    def _cost(self):
        self.cost = 0
        if self.move_id.id>0:
            for quant_id in self.move_id.quant_ids:
                if quant_id.cost>0:
                    self.cost += (quant_id.cost*self.scrap_qty)
                else:
                    self.cost += (quant_id.inventory_value/self.scrap_qty)