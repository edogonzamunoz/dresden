# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.float_utils import float_repr
import base64
from markupsafe import Markup
import re
from lxml import etree

class AccountMove(models.Model):
    _inherit = 'account.move'

    def existe_proprina(self):
        for inv in self.line_ids:
            if inv.product_id.name == 'PROPINA SUGERIDA':
                return True
        return False

    def _l10n_cl_create_dte_envelope(self, receiver_rut='60803000-K'):
        file_name = 'F{}T{}.xml'.format(self.l10n_latam_document_number, self.l10n_latam_document_type_id.code)
        digital_signature = self.company_id._get_digital_signature(user_id=self.env.user.id)
        template = self.l10n_latam_document_type_id._is_doc_type_voucher() and self.env.ref(
            'l10n_cl_edi_extend.envio_boleta') or self.env.ref('l10n_cl_edi_extend.envio_dte')
        dte = self.l10n_cl_dte_file.raw.decode('ISO-8859-1')
        dte = Markup(dte.replace('<?xml version="1.0" encoding="ISO-8859-1" ?>', ''))
        dte_rendered = self.env['ir.qweb']._render(template.id, {
            'move': self,
            'RutEmisor': self._l10n_cl_format_vat(self.company_id.vat),
            'RutEnvia': digital_signature.subject_serial_number,
            'RutReceptor': receiver_rut,
            'FchResol': self.company_id.l10n_cl_dte_resolution_date,
            'NroResol': self.company_id.l10n_cl_dte_resolution_number,
            'TmstFirmaEnv': self._get_cl_current_strftime(),
            'dte': dte,
            '__keep_empty_lines': True,
        })
        dte_rendered = dte_rendered.replace('<?xml version="1.0" encoding="ISO-8859-1" ?>', '')
        dte_signed = self._sign_full_xml(
            dte_rendered, digital_signature, 'SetDoc',
            self.l10n_latam_document_type_id._is_doc_type_voucher() and 'bol' or 'env',
            self.l10n_latam_document_type_id._is_doc_type_voucher()
        )
        return dte_signed, file_name

    def _l10n_cl_get_dte_barcode_xml(self):
        """
        This method create the "stamp" (timbre). Is the auto-contained information inside the pdf417 barcode, which
        consists of a reduced xml version of the invoice, containing: issuer, recipient, folio and the first line
        of the invoice, etc.
        :return: xml that goes embedded inside the pdf417 code
        """
        dd = self.env['ir.qweb']._render('l10n_cl_edi_extend.dd_template', {
            'move': self,
            'format_vat': self._l10n_cl_format_vat,
            'float_repr': float_repr,
            'format_length': self._format_length,
            'format_uom': self._format_uom,
            'time_stamp': self._get_cl_current_strftime(),
            'caf': self.l10n_latam_document_type_id._get_caf_file(self.company_id.id, int(self.l10n_latam_document_number)),
            '__keep_empty_lines': True,
        })
        caf_file = self.l10n_latam_document_type_id._get_caf_file(self.company_id.id, int(self.l10n_latam_document_number))
        ted = self.env['ir.qweb']._render('l10n_cl_edi.ted_template', {
            'dd': dd,
            'frmt': self._sign_message(dd.encode('ISO-8859-1', 'replace'), caf_file.findtext('RSASK')),
            'stamp': self._get_cl_current_strftime(),
            '__keep_empty_lines': True,
        })
        return {
            'ted': Markup(re.sub(r'\n\s*$', '', ted, flags=re.MULTILINE)),
            'barcode': etree.tostring(etree.fromstring(re.sub(
                r'<TmstFirma>.*</TmstFirma>', '', ted), parser=etree.XMLParser(remove_blank_text=True)))
        }

    def _l10n_cl_create_dte(self):
        if self.l10n_latam_document_type_id.code == '39' or self.l10n_latam_document_type_id.code == '33':
            folio = int(self.l10n_latam_document_number)
            doc_id_number = 'F{}T{}'.format(folio, self.l10n_latam_document_type_id.code)
            dte_barcode_xml = self._l10n_cl_get_dte_barcode_xml()
            self.l10n_cl_sii_barcode = dte_barcode_xml['barcode']
            dte = self.env['ir.qweb']._render('l10n_cl_edi_extend.dte_template', {
                'move': self,
                'format_vat': self._l10n_cl_format_vat,
                'get_cl_current_strftime': self._get_cl_current_strftime,
                'format_length': self._format_length,
                'format_uom': self._format_uom,
                'float_repr': float_repr,
                'doc_id': doc_id_number,
                'caf': self.l10n_latam_document_type_id._get_caf_file(self.company_id.id,
                                                                      int(self.l10n_latam_document_number)),
                'amounts': self._l10n_cl_get_amounts(),
                'withholdings': self._l10n_cl_get_withholdings(),
                'dte': dte_barcode_xml['ted'],
                '__keep_empty_lines': True,
            })
            digital_signature = self.company_id._get_digital_signature(user_id=self.env.user.id)
            signed_dte = self._sign_full_xml(
                dte, digital_signature, doc_id_number, 'doc', self.l10n_latam_document_type_id._is_doc_type_voucher())
            dte_attachment = self.env['ir.attachment'].create({
                'name': 'DTE_{}.xml'.format(self.name),
                'res_model': self._name,
                'res_id': self.id,
                'type': 'binary',
                'datas': base64.b64encode(signed_dte.encode('ISO-8859-1', 'replace'))
            })
            self.l10n_cl_dte_file = dte_attachment.id
        else:
            super(AccountMove, self)._l10n_cl_create_dte()

    def action_delete_attachment_pdf(self):
        invoices = self.env['account.move'].search([])
        for attac in invoices.attachment_ids:
            if attac.name.split('.')[1] == 'pdf':
                attac._file_delete(attac.store_fname)