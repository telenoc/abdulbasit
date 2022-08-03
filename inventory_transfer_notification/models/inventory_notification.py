# -*- coding: utf-8 -*-
import pdb

from odoo import models, fields, api,SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError



class InventoryTransferNotification(models.Model):
    _inherit = 'stock.warehouse'
    _description = 'Inventory Transfer Notification'

    user_notification_ids = fields.Many2many('res.users', string="User Notification")
    user_message = fields.Char("Message")


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Inventory Transfer Notification'


    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.env.su:
            self = self.with_user(SUPERUSER_ID)

        for order in self:
            if order.sale_order_template_id and order.sale_order_template_id.mail_template_id:
                order.sale_order_template_id.mail_template_id.send_mail(order.id)
        self.user_notification(self.warehouse_id.user_notification_ids, self.warehouse_id.user_message)
        return res

    def user_notification(self,users,body_text):
        notification_ids =[]
        if users:
            notification_ids = [(0, 0,
                                 {
                                     'res_partner_id': user.partner_id.id,
                                     'notification_type': 'inbox'
                                 }
                                 ) for user in users if users]
        else:
            raise ValidationError('There as No User Please select the Users in User Notification Field')

        if not body_text:
            raise ValidationError('Please Write Message in the Message Field in Warehouse')

        for rec in self.picking_ids:
            self.env['mail.message'].sudo().create({
                'message_type': "notification",
                'body': body_text,
                'subject': "Warehouse Activity",
                'partner_ids': [(4, user.partner_id.id) for user in users if users],
                'model': 'stock.picking',
                'res_id': rec.id,
                'notification_ids': notification_ids,
                'author_id': self.env.user.partner_id and self.env.user.partner_id.id
            })





