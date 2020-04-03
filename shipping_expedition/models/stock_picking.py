# -*- coding: utf-8 -*-
# Copyright 2012-2015 Akretion <http://www.akretion.com>.
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
                    
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_carrier_type_selection(self):
        carrier_obj = self.env['delivery.carrier']
        return carrier_obj._get_carrier_type_selection()

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Transportista',
        states={'done': [('readonly', True)]},
    )
    carrier_type = fields.Selection(
        related='carrier_id.carrier_type',
        string='Tipo de transportista',
        readonly=True,
    )
    shipping_expedition_id = fields.Many2one(
        comodel_name='shipping.expedition',
        inverse_name='picking_id',
        string='Expedicion',
        readonly=True,
        copy=False
    )                    

    @api.multi
    def generate_default_shipping_expedition(self, package_ids=None):
        """ Abstract method

        :param package_ids: optional list of ``stock.quant.package`` ids
                            only packs in this list will have their label
                            printed (all are generated when None)

        :return: (file_binary, file_type)

        """
        raise UserError(_('No label is configured for the ' 'selected delivery method.'))

    @api.multi
    def generate_shipping_expedition(self, package_ids=None):
        """Generate a shipping label by default

        This method can be inherited to create specific shipping labels
        a list of label must be return as we can have multiple
        stock.quant.package for a single picking representing packs

        :param package_ids: optional list of ``stock.quant.package`` ids
                             only packs in this list will have their label
                             printed (all are generated when None)

        :return: list of dict containing
           name: name to give to the attachement
           file: file as string
           file_type: string of file type like 'PDF'
           (optional)
           tracking_id: tracking_id if picking lines have tracking_id and
                        if label generator creates shipping label per
                        pack

        """
        default_shipping_expedition = self.generate_default_shipping_expedition(package_ids=package_ids)
        if not package_ids:
            return [default_shipping_expedition]
        labels = []
        for package_id in package_ids:
            shipping_expedition = default_shipping_expedition.copy()
            shipping_expedition['tracking_id'] = package_id
            labels.append(shipping_expedition)
        return labels

    @api.multi
    def get_shipping_expedition_values(self, expedition):
        self.ensure_one()
        
        return {
            'code': None,
            'delivery_code': None,
            'date': None,
            'hour': None,
            'observations': None,
            'state': None,
            'state_code': None,
            'exps_rels': None,
        }

    @api.multi
    def generate_shipping_expedition(self, package_ids=None):
        return True                

    @api.multi
    def action_generate_shipping_expedition(self, package_ids=None):
        """ Method for the 'Generate Label' button.

        It will generate the labels for all the packages of the picking.

        """
        if self.shipping_expedition_id.id==0:
            shipping_expedition_obj = self.env['shipping.expedition']
                                
            for pick in self:            
                if self.carrier_id.id>0:
                    if package_ids:
                        shipping_expedition = pick.generate_shipping_expedition(
                            package_ids=package_ids
                        )
                    else:
                        shipping_expedition = pick.generate_shipping_expedition()                                
                    
                    data = pick.get_shipping_expedition_values(shipping_expedition)
                    
                    if data==None and shipping_expedition!=None:
                        data = shipping_expedition                                        
                    
                    if data!=None:                                                                                                                                                         
                        data['partner_id'] = self.partner_id.id
                        data['picking_id'] = self.id
                        data['carrier_id'] = self.carrier_id.id                    
                        data['origin'] = self.name
                        data['observations'] = pick.shipping_expedition_note
                        
                        sale_order_ids = self.env['sale.order'].search(
                            [
                                ('name', '=', self.origin)
                            ]
                        )
                        for sale_order_id in sale_order_ids:
                            data['order_id'] = sale_order_id.id
                            
                            if sale_order_id.user_id:
                                data['user_id'] = sale_order_id.user_id.id                                                                           
                        
                        shipping_expedition_obj = shipping_expedition_obj.create(data)
                        
                        self.shipping_expedition_id = shipping_expedition_obj                                                 
        return True;
                
    @api.one    
    def action_error_create_shipping_expedition_message_slack(self, res):
        return
        
    @api.one    
    def action_error_edit_shipping_expedition_message_slack(self, res):
        return                        