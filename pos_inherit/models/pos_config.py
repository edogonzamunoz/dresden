from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_boleta_journal_id = fields.Many2one(
        'account.journal', string='Boleta Journal',
        domain=[('type', '=', 'sale')],
        help="Accounting journal used to create Boleta.")

    address_change_id = fields.Many2one('res.partner',string='Direccion boleta de POS')
    address_change_street = fields.Char(string='Calle',related='address_change_id.street')
    address_change_street2 = fields.Char(string='Calle 2',related='address_change_id.street2')
    address_change_city = fields.Char(string='Ciudad',related='address_change_id.city')
    address_change_phone = fields.Char(string='Telefono',related='address_change_id.phone')
    address_change_activity_description = fields.Char(string='Telefono',related='address_change_id.l10n_cl_activity_description')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    address_change_id = fields.Many2one('res.partner',related='pos_config_id.address_change_id', readonly=False)
