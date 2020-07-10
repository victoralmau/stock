# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
_logger = logging.getLogger(__name__)

from odoo import fields, models, api

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    link_tracker_id = fields.Many2one(
        comodel_name='link.tracker', 
        string='Link Tracker Id'
    )

    @api.model
    def create(self, values):
        return_object = super(ShippingExpedition, self).create(values)
        # operations
        if return_object.url_info != False:
            return_object.action_generate_shipping_expedition_link_tracker()
        # return
        return return_object

    @api.one
    def action_generate_shipping_expedition_link_tracker(self):
        if self.link_tracker_id.id == 0:
            if self.url_info != False:
                link_tracker_vals = {
                    'title': self.code,
                    'url': self.url_info
                }
                link_tracker_obj = self.env['link.tracker'].sudo().create(link_tracker_vals)
                self.link_tracker_id = link_tracker_obj.id
        # return
        return True