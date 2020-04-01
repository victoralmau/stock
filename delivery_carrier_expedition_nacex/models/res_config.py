# -*- coding: utf-8 -*-
import logging

from openerp import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)

class NacexConfigSettings(models.TransientModel):
    _name = 'nacex.config.settings'
    _inherit = 'res.config.settings'

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=_default_company
    )
    
    del_cli = fields.Char(related='company_id.nacex_del_cli')
    num_cli = fields.Char(related='company_id.nacex_num_cli')
    dep_cli = fields.Char(related='company_id.nacex_dep_cli')
    tip_ser = fields.Selection(related='company_id.nacex_tip_ser')
    tip_cob = fields.Selection(related='company_id.nacex_tip_cob')
    tip_env = fields.Selection(related='company_id.nacex_tip_env')
    print_model = fields.Char(related='company_id.nacex_print_model')
    print_et = fields.Char(related='company_id.nacex_print_et')    

    @api.onchange('company_id')
    def onchange_company_id(self):
        # update related fields
        if not self.company_id:
            return
        company = self.company_id

        self.del_cli = company.nacex_del_cli
        self.num_cli = company.nacex_num_cli
        self.dep_cli = company.nacex_dep_cli
        self.tip_ser = company.nacex_tip_ser
        self.tip_cob = company.nacex_tip_cob
        self.tip_env = company.nacex_tip_env
        self.print_model = company.nacex_print_model
        self.print_et = company.nacex_print_et        