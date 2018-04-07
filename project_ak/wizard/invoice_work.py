# coding: utf-8
# © 2015 Benoît Guillot @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, api, models, _
from odoo.exceptions import UserError


class InvoiceWorkLine(models.TransientModel):
    _name = "invoice.work.line"

    invoice_work_id = fields.Many2one(comodel_name="invoice.work")
    user_id = fields.Many2one(comodel_name="res.users", string="Worker")
    work_amount = fields.Float()


class InvoiceWork(models.TransientModel):
    _name = "invoice.work"

    @api.model
    def _get_work_line(self):
        res = []
        line_ids = self.env.context.get('active_ids')
        if line_ids:
            for line in self.env['project.task.work'].read_group(
                    [('id', 'in', line_ids)],
                    ['user_id', 'hours'],
                    ['user_id']):
                res.append((0, 0, {
                    'user_id': line['user_id'][0],
                    'work_amount': line['hours']}))
        return res

    invoice_number = fields.Char()
    work_line_ids = fields.One2many(
        comodel_name="invoice.work.line",
        inverse_name="invoice_work_id",
        default=_get_work_line)

    @api.multi
    def invoice_work(self):
        self.ensure_one()
        line_ids = self.env.context.get('active_ids')
        if line_ids:
            lines = self.env['project.task.work'].browse(line_ids)
            if any([line.invoice_number is not False for line in lines]):
                raise UserError(_("The work as already been invoiced !"))
            lines.write({'invoice_number': self.invoice_number})
