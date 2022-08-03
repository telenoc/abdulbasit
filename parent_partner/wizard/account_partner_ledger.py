# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo import fields, models
import pdb
from odoo import api, fields, models, _
from datetime import date
import xlsxwriter
import base64
import io

from odoo.exceptions import UserError, ValidationError
import pdb
import time
from datetime import date
import datetime
from datetime import timedelta
from odoo.tools.misc import get_lang
from dateutil import relativedelta
from odoo import tools
from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)

from io import StringIO
import io

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class AccountingReport(models.TransientModel):
    _name = "partner.ledger.wizard"
    _inherit = "account.common.report"

    _description = "Account Partner Ledger"

    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on "
                                          "report if the currency differs from "
                                          "the company currency.")
    reconciled = fields.Boolean('Reconciled Entries', default=True)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search(
                                       [('type', 'in', ['sale', 'purchase'])]))

    partner_ids = fields.Many2one('res.partner', string='Partners',)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    label_filter = fields.Char(string='Column Label', help="This label will be displayed on report to "
                                                           "show the balance computed for the given comparison filter.")
    filter_cmp = fields.Selection([('filter_no', 'No Filters'), ('filter_date', 'Date')],
                                  string='Filter by', required=True, default='filter_no')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='all')
    date_from_cmp = fields.Date(string='Date From')
    display_account = fields.Selection([('all', 'All'),
                                        ('movement', 'With movements'),
                                        ('not_zero', 'With balance is not equal to 0'), ],
                                       string='Display Accounts',
                                       required=True, default='movement')
    enable_filter = fields.Boolean(string='Enable Comparison')
    date_to_cmp = fields.Date(string='Date To')
    debit_credit = fields.Boolean(string='Display Debit/Credit Columns',
                                  help="This option allows you to get more details about "
                                       "the way your balances are computed."
                                       " Because it is space consuming, we do not allow to"
                                       " use it while doing a comparison.")
    analytic_account_ids = fields.Many2many('account.analytic.account',
                                            string='Analytic Accounts')

    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer_supplier')
    date_from = fields.Date(string='Date From', )
    date_to = fields.Date(string='Date To', )
    account_ids = fields.Many2many('account.account', string='Accounts')

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        data['form'].update({'partner_ids': self.partner_ids.ids})
        return data



    def _get_report_data(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled,
                             'amount_currency': self.amount_currency})
        return data

    def _print_report(self, data):
        data = self._get_report_data(data)
        return self.env.ref('parent_partner.action_report_partnerledger').with_context(landscape=True).\
            report_action(self, data=data)



    def _print_reports(self,data):
        data = self._get_report_data(data)
        complete_calculations = self._get_report_valuess(data)
        return self._print_partner_ledger_xlsx_report(complete_calculations)
        # return self.env.ref('parent_partner.ledger_excel_report_id').report_action(self, data=complete_calculations)




    def _liness(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        query = """
               SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
               FROM """ + query_get_data[0] + """
               LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
               LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
               LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
               LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
               WHERE "account_move_line".partner_id = %s
                   AND m.state IN %s
                   AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                   ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def _sum_partners(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        query = """SELECT sum(""" + field + """)
                   FROM """ + query_get_data[0] + """, account_move AS m
                   WHERE "account_move_line".partner_id = %s
                       AND m.id = "account_move_line".move_id
                       AND m.state IN %s
                       AND account_id IN %s
                       AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    def _get_report_valuess(self, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
               SELECT a.id
               FROM account_account a
               WHERE a.internal_type IN %s
               AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
               SELECT DISTINCT "account_move_line".partner_id
               FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
               WHERE "account_move_line".partner_id IS NOT NULL
                   AND "account_move_line".account_id = account.id
                   AND am.id = "account_move_line".move_id
                   AND am.state IN %s
                   AND "account_move_line".account_id IN %s
                   AND NOT account.deprecated
                   AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        if data['form']['partner_ids']:
            partner_ids = data['form']['partner_ids']
        else:
            partner_ids = [res['partner_id'] for res in
                           self.env.cr.dictfetchall()]
        # partners = obj_partner.browse(partner_ids)
        partners = obj_partner.search([('partner_id','in',partner_ids)])
        partners = sorted(partners, key=lambda x: (x.ref or '', x.partner_id.name or ''))
        if not partners:
            raise ValidationError('Please Select The Parent in Parent Field')
        for prt in partners:
            parent_id = self.env['res.partner'].search([('name', '=', prt.partner_id.name)])


        return {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'parent': parent_id,
            'lines': self._liness,
            'sum_partner': self._sum_partners,
        }



    def print_partner_ledger_xlsx_reports(self):

        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return self.with_context(discard_logo_check=True)._print_reports(data)

    def _print_partner_ledger_xlsx_report(self, complete_calculations):
        # ***** Excel Related Statements *****#


        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Partner Ledger", cell_overwrite_ok=True)

        style_table_header = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black;pattern: pattern solid, fore_colour white ;align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, ;")
        style_table_heading = xlwt.easyxf(
            "font:height 250; font: name Liberation Sans, bold on,color black;pattern: pattern solid, fore_colour white ;align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, ;")

        style_date_col = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")

        for aa in range(35):
            col_aa = worksheet.col(aa)
            col_aa.width = 300 * 15

        recs = False
        row = 0
        col = 0

        table_header = ['Date', 'Sub Account (Child)', 'Ref', 'Debit',
                        'Credit', 'Balance']

        x = len(table_header)

        product_image = io.BytesIO(base64.b64decode(self.company_id.logo))
        # worksheet.insert_image(row, col, "image.png", {'image_data': product_image})
        for parent in complete_calculations['parent']:
            parent_name = parent.name
            # worksheet.write_merge(0,1, 0,1, product_image, style=style_table_header)
            # worksheet.insert_image(0,1, 0,1, "image.png", {'image_data': product_image,'x_scale':0.5,'y_scale':0.5})
            worksheet.write_merge(0, 1, 1, 3,  'Account Statement For : '+parent_name, style=style_table_heading)
            # worksheet.write_merge(0, 1, 3,  'hello', style=style_table_header)

            worksheet.write_merge(0,1, 4,4, 'Date From / '+self.date_from.strftime('%d-%b-%y'), style=style_table_header)

            worksheet.write_merge(0,1, 5,5, 'Date To / '+self.date_to.strftime('%d-%b-%y'), style=style_table_header)
            col += 1

        row = 3
        col = 0
        for i in range(x):
            worksheet.write(row, col, table_header[i], style=style_table_header)
            col += 1

        row += 1
        line_row = row
        col = 0
        balance = 0
        total_credit = 0
        total_debit = 0
        start = True

        for doc in complete_calculations['docs']:

            for line in self._liness(complete_calculations['data'], doc):
                col = 0

                prt_name = doc.name
                print(prt_name)
                li_date = line.get("date")
                li_display_name = line.get("name")
                li_credit = line.get("credit")
                li_debit = line.get("debit")
                li_progress = li_debit -li_credit
                li_progress = -(li_progress)
                balance = balance+(li_debit - li_credit)
                total_credit = total_credit+li_credit
                total_debit = total_debit+li_debit


                worksheet.write(line_row, col, li_date.strftime('%d-%b-%y'), style=style_date_col)
                col += 1
                if prt_name != parent_name:
                    worksheet.write(line_row, col, prt_name, style=style_date_col)
                col += 1
                if start != True:
                    worksheet.write(line_row, col, li_display_name, style=style_date_col)
                    col += 1
                else:
                    start = False
                    worksheet.write(line_row, col, 'Starting Balance', style=style_date_col)
                    col += 1
                worksheet.write(line_row, col, li_debit, style=style_date_col)
                col += 1
                worksheet.write(line_row, col, li_credit, style=style_date_col)
                col += 1

                worksheet.write(line_row, col, balance, style=style_date_col)
                col += 1

                line_row += 1
            row+=1
            col = 0

        worksheet.write_merge(line_row,line_row, 0,2, "Total ", style=style_table_header)
        col +=3
        worksheet.write(line_row, col, total_debit, style=style_table_header)
        col +=1
        worksheet.write(line_row, col, total_credit, style=style_table_header)
        col += 1
        worksheet.write(line_row, col, balance, style=style_table_header)

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['partner.report.wizard.report'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Partner Ledger Report.xls'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partner Ledger Report',
            'res_model': 'partner.report.wizard.report',
            'view_mode': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }


class AccountingReport(models.TransientModel):
    _name = "accounting.report"
    _inherit = "account.common.report"
    _description = "Accounting Report"

    def check_report(self):

        res = super(AccountingReport, self).check_report()
        data = {}
        data['form'] = self.read(['account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context
        return res

class PartnerReportWizard(models.TransientModel):
    _name = "partner.report.wizard.report"
    _description = ''

    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)
