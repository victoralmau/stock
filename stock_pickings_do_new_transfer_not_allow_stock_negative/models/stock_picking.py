# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, models, _
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'                    
    
    @api.multi
    def do_transfer(self):
        allow_do_transfer = True
        # operations
        for obj in self:
            if obj.picking_type_id.code == 'outgoing':
                for pack_operation_product_id in obj.pack_operation_product_ids:
                    if pack_operation_product_id.product_id.product_tmpl_id.allow_negative_stock == False:
                        # pack_lot_ids
                        if pack_operation_product_id.pack_lot_ids:
                            for pack_lot_id in pack_operation_product_id.pack_lot_ids:
                                if pack_lot_id.qty > 0:
                                    qty_item = pack_operation_product_id.product_id.product_tmpl_id.get_quantity_by_lot_id(pack_lot_id.lot_id.id)[0]
                                    qty_item_final = qty_item-pack_lot_id.qty
                                    if qty_item_final < 0:
                                        raise exceptions.Warning(_('Product  %s - %s would keep stock %s') % (
                                            pack_operation_product_id.product_id.name,
                                            pack_lot_id.lot_id.name,
                                            qty_item_final
                                        ))
                        else:
                            if pack_operation_product_id.qty_done > 0:
                                qty_item = pack_operation_product_id.product_id.product_tmpl_id.get_quantity_by_lot_id(0)[0]
                                qty_item_final = qty_item-pack_operation_product_id.qty_done
                                if qty_item_final < 0:
                                    raise exceptions.Warning(_('Product  %s would keep stock %s') % (
                                        pack_operation_product_id.product_id.name,
                                        qty_item_final
                                    ))
        # allow_do_transfer
        if allow_do_transfer:
            return super(StockPicking, self).do_transfer()