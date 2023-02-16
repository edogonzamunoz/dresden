# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    cstm_default_partner_id = fields.Many2one('res.partner', string="Select Customer")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    cstm_default_partner_id = fields.Many2one('res.partner',related='pos_config_id.cstm_default_partner_id',readonly=False)