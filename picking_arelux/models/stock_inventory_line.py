# -*- coding: utf-8 -*-
from odoo import api, models, fields

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'
    
    prod_lot_id_ref = fields.Char( 
        string='Referencia interna',
        compute='_get_prod_lot_id_ref',
        store=False
    )
    
    @api.one        
    def _get_prod_lot_id_ref(self):
        for line in self:                              
            line.prod_lot_id_ref = line.prod_lot_id.ref                                                                                                                   