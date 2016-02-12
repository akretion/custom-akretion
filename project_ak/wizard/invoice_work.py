# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015-TODAY Akretion (http://www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, api, models, _
from openerp.exceptions import Warning as UserError


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
        line_ids = self._context.get('active_ids')
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
        line_ids = self._context.get('active_ids')
        if line_ids:
            lines = self.env['project.task.work'].browse(line_ids)
            if any([line.invoice_number != False for line in lines]):
                raise UserError(_("The work as already been invoiced !"))
            lines.write({'invoice_number': self.invoice_number})
