from odoo import models

import time
from odoo import api, models, _
from odoo.exceptions import UserError
import base64
import io
from datetime import datetime

from odoo import models
from odoo.tools.misc import get_lang


class PateintCardXls(models.AbstractModel):
    _name = 'report.parent_partner.ledger_excel_report'
    _inherit = 'report.report_xlsx.abstract'
    aa =21

    def generate_xlsx_report(self, workbook, data, complete_calculations,):
        # ***** Excel Related Statements *****#

        # data = self._get_report_data(data)
        # complete_calculations = self._get_report_valuess(data)

        sheet = workbook.add_worksheet("Report")
        worksheet = workbook.add_format(
            {
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'color': 'white',
                'font': 16,
                'fg_color': '#696969',
            }
        )
        cell_border = workbook.add_format({
            'border': 1,
            'valign': 'vcenter', })

        # style_table_header = workbook.add_format(
        #     "font:height 200; font: name Liberation Sans, bold on,color black;pattern: pattern solid, fore_colour white ;align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, ;")
        # style_table_heading = workbook.add_format(
        #     "font:height 250; font: name Liberation Sans, bold on,color black;pattern: pattern solid, fore_colour white ;align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, ;")
        #
        # style_date_col = workbook.add_format(
        #     "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")

        # for aa in range(35):
        #     col_aa = worksheet.col(aa)
        #     col_aa.width = 300 * 15
        #
        # recs = False
        row = 0
        col = 0

        table_header = ['Date', 'Sub Account (Child)', 'Ref', 'Debit','Credit', 'Balance']

        x = len(table_header)

        # product_image = io.BytesIO(base64.b64decode(self.company_id.logo))
        # worksheet.insert_image(row, col, "image.png", {'image_data': product_image})
        for parent in complete_calculations['parent']:
            parent_name = parent.name
            # worksheet.write_merge(0,1, 0,1, product_image, style=style_table_header)
            # worksheet.insert_image(0,1, 0,1, "image.png", {'image_data': product_image,'x_scale':0.5,'y_scale':0.5})
            worksheet.write_merge(0, 1, 2, 3,  parent_name, style=worksheet)
            # worksheet.write_merge(0, 1, 3,  'hello', style=style_table_header)

            worksheet.write_merge(0,1, 4,4, 'Date From / '+self.date_from.strftime('%d-%b-%y'), style=worksheet)

            worksheet.write_merge(0,1, 5,5, 'Date To / '+self.date_to.strftime('%d-%b-%y'), style=worksheet)
            col += 1

        row = 3
        col = 0
        # for i in range(x):
        #     worksheet.write(row, col, table_header[i], style=style_table_header)
        #     col += 1

        row += 1
        line_row = row
        col = 0
        balance = 0
        total_credit = 0
        total_debit = 0
        start = True

        # for doc in complete_calculations['docs']:
        #
        #     for line in self._liness(complete_calculations['data'], doc):
        #         col = 0
        #
        #         prt_name = doc.name
        #         print(prt_name)
        #         li_date = line.get("date")
        #         li_display_name = line.get("name")
        #         li_credit = line.get("credit")
        #         li_debit = line.get("debit")
        #         li_progress = li_debit -li_credit
        #         li_progress = -(li_progress)
        #         balance = balance+(li_debit - li_credit)
        #         total_credit = total_credit+li_credit
        #         total_debit = total_debit+li_debit
        #
        #
        #         worksheet.write(line_row, col, li_date.strftime('%d-%b-%y'), style=style_date_col)
        #         col += 1
        #         worksheet.write(line_row, col, prt_name, style=style_date_col)
        #         col += 1
        #         if start != True:
        #             worksheet.write(line_row, col, li_display_name, style=style_date_col)
        #             col += 1
        #         else:
        #             start = False
        #             worksheet.write(line_row, col, 'Starting Balance', style=style_date_col)
        #             col += 1
        #         worksheet.write(line_row, col, li_debit, style=style_date_col)
        #         col += 1
        #         worksheet.write(line_row, col, li_credit, style=style_date_col)
        #         col += 1
        #
        #         worksheet.write(line_row, col, balance, style=style_date_col)
        #         col += 1
        #
        #         line_row += 1
        #     row+=1
        #     col = 0
        #
        # worksheet.write_merge(line_row,line_row, 0,3, "Total ", style=style_table_header)
        # col +=3
        # worksheet.write(line_row, col, total_debit, style=style_table_header)
        # col +=1
        # worksheet.write(line_row, col, total_credit, style=style_table_header)
        # col += 1
        # worksheet.write(line_row, col, balance, style=style_table_header)

        # file_data = io.BytesIO()
        # workbook.save(file_data)
        # wiz_id = self.env['partner.report.wizard.report'].create({
        #     'data': base64.encodebytes(file_data.getvalue()),
        #     'name': 'Partner Ledger Report.xlsx'
        # })
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Partner Ledger Report',
        #     'res_model': 'partner.report.wizard.report',
        #     'view_mode': 'form',
        #     'res_id': wiz_id.id,
        #     'target': 'new'
        # }

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

    def _get_report_data(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled,
                             'amount_currency': self.amount_currency})
        return data

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        data['form'].update({'partner_ids': self.partner_ids.ids})
        return data