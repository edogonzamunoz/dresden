from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_boleta_journal_id = fields.Many2one(
        'account.journal', string='Boleta Journal',
        domain=[('type', '=', 'sale')],
        help="Accounting journal used to create Boleta.")
