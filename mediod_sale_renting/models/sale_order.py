# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_damage = fields.Boolean('Damage')


    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.is_rental_order == True:
            for rec in res.order_line:
                if rec.product_uom_qty > rec.virtual_available_at_date:
                    raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
        return res

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if self.is_rental_order == True:
            for rec in self.order_line:
                if rec.product_uom_qty > rec.virtual_available_at_date:
                    raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
        return result

    @api.onchange('is_damage')
    def send_damage_mail(self):
        for rec in self:
            if rec.is_damage == True:
                template_id = self.env.ref('mediod_sale_renting.notification_emial_template')
                if template_id:
                    # order_line_partners = self.mapped('order_partner_id')
                    template_id.email_to = rec.user_id.email
                    template_id.send_mail(rec.id, force_send=True)

