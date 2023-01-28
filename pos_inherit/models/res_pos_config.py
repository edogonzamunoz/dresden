# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class ResPosConfig(models.TransientModel):
    _inherit = "res.config.settings"

    pos_boleta_journal_id = fields.Many2one(related='pos_config_id.pos_boleta_journal_id', readonly=False)


