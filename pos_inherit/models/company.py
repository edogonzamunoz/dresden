from odoo import fields, models, api

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_company(self):
        """
        
        """
        res = super(PosSession, self)._loader_params_res_company()
        fields_to_add = ['primary_color', 'partner_id', 'l10n_cl_sii_regional_office', 'l10n_cl_dte_resolution_number', 'l10n_cl_dte_resolution_date', 'l10n_cl_activity_description', 'street', 'street2',
        'city', 'state_id', 'country_id']
        
        for field in fields_to_add:
            res.get('search_params').get('fields').append(field)
        
        return res

    def _loader_params_pos_order(self):
        return {
            'search_params': {
                'fields': ['l10n_cl_sii_barcode'],
            },
        }

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('pos.order')
        return result

    def _get_pos_ui_pos_order(self, params):
        return self.env['pos.order'].search_read(**params['search_params'])
