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
    carrier_code = fields.Char(
        related='carrier_id.code',
        readonly=True,
    )
    shipping_expedition_id = fields.Many2one(
        comodel_name='shipping.expedition',
        inverse_name='picking_id',
        string='Expedicion',
        readonly=True,
        copy=False
    )
    option_ids = fields.Many2many(
        comodel_name='delivery.carrier.option',
        string='Options'
    )
    
    expedition_image = fields.Char(
        compute='_get_expedition_image',
        store=False,
    )    
    
    @api.multi
    def _get_expedition_image(self):
        return False                    

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

    @api.onchange('carrier_id')
    def carrier_id_change(self):
        """ Inherit this method in your module """
        if not self.carrier_id:
            return
        # This can look useless as the field carrier_code and
        # carrier_type are related field. But it's needed to fill
        # this field for using this fields in the view. Indeed the
        # module that depend of delivery base can hide some field
        # depending of the type or the code
        carrier = self.carrier_id
        self.carrier_type = carrier.carrier_type
        self.carrier_code = carrier.code
        default_options = carrier.default_options()
        self.option_ids = [(6, 0, default_options.ids)]
        result = {
            'domain': {
                'option_ids': [('id', 'in', carrier.available_option_ids.ids)],
            }
        }
        return result

    @api.onchange('option_ids')
    def option_ids_change(self):
        if not self.carrier_id:
            return
        carrier = self.carrier_id
        for available_option in carrier.available_option_ids:
            if (available_option.mandatory and
                    available_option not in self.option_ids):
                # XXX the client does not allow to modify the field that
                # triggered the onchange:
                # https://github.com/odoo/odoo/issues/2693#issuecomment-56825399
                # Ideally we should add the missing option
                raise UserError(
                    _("You should not remove a mandatory option."
                      "Please cancel the edit or "
                      "add back the option: %s.") % available_option.name
                )

    @api.model
    def _values_with_carrier_options(self, values):
        values = values.copy()
        carrier_id = values.get('carrier_id')
        option_ids = values.get('option_ids')
        if carrier_id and not option_ids:
            carrier_obj = self.env['delivery.carrier']
            carrier = carrier_obj.browse(carrier_id)
            default_options = carrier.default_options()
            if default_options:
                values.update(option_ids=[(6, 0, default_options.ids)])
        return values

    @api.multi
    @api.returns('stock.quant.package')
    def _get_packages_from_picking(self):
        """ Get all the packages from the picking """
        self.ensure_one()
        operation_obj = self.env['stock.pack.operation']
        packages = self.env['stock.quant.package'].browse()
        operations = operation_obj.search(
            ['|',
             ('package_id', '!=', False),
             ('result_package_id', '!=', False),
             ('picking_id', '=', self.id)]
        )
        for operation in operations:
            # Take the destination package. If empty, the package is
            # moved so take the source one.
            packages |= operation.result_package_id or operation.package_id
        return packages

    @api.multi
    def write(self, vals):
        """ Set the default options when the delivery method is changed.

        So we are sure that the options are always in line with the
        current delivery method.

        """
        vals = self._values_with_carrier_options(vals)
        return super(StockPicking, self).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """ Trigger carrier_id_change on create

        To ensure options are setted on the basis of carrier_id copied from
        Sale order or defined by default.

        """
        vals = self._values_with_carrier_options(vals)
        return super(StockPicking, self).create(vals)

    @api.multi
    def _get_label_sender_address(self):
        """ On each carrier label module you need to define
            which is the sender of the parcel.
            The most common case is 'picking.company_id.partner_id'
            and then choose the contact which has the type 'delivery'
            which is suitable for each delivery carrier label module.
            But your client might want to customize sender address
            if he has several brands and/or shops in his company.
            In this case he doesn't want his customer to see
            the address of his company in his transport label
            but instead, the address of the partner linked to his shop/brand

            To reach this modularity, call this method to get sender address
            in your delivery_carrier_label_yourcarrier module, then every
            developer can manage specific needs by inherit this method in
            module like :
            delivery_carrier_label_yourcarrier_yourproject.
        """
        self.ensure_one()
        partner = self.company_id.partner_id
        address_id = partner.address_get(adr_pref=['delivery'])['delivery']
        return self.env['res.partner'].browse(address_id)

    @api.multi
    def _check_existing_shipping_expedition(self):
        """ Check that expedition don't already exist for this picking """
        self.ensure_one()
        expeditions = self.env['shipping.expedition'].search([
            ('picking_id', '=', self.id)
        ])
        if _check_existing_shipping_label:
            raise UserError(
                _('Some expeditions already exist for the picking %s.\n'
                  'Please delete the existing expeditions')
                % self.name)
                
    @api.one    
    def action_error_create_shipping_expedition_message_slack(self, res):
        return
        
    @api.one    
    def action_error_edit_shipping_expedition_message_slack(self, res):
        return                        