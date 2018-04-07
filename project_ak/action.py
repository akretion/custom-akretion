# coding: utf-8
# © 2015 Benoît Guillot @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.addons.project_model_to_task.models.action import UNIQUE_ACTION_ID


class IrValues(models.Model):
    _inherit = 'ir.values'

    @api.model
    def get_actions(self, action_slot, model, res_id=False):
        """ Remove if user doesn't have rights """
        res = super(IrValues, self).get_actions(
            action_slot, model, res_id=res_id)
        if (action_slot == 'client_action_multi' and
                not self.env['res.users'].browse(self._uid).has_group(
                    'project_ak.group_customer_user')):
            action = self.set_task_action(model, res_id=res_id)
            if action:
                value = (UNIQUE_ACTION_ID, 'project_model_to_task', action)
                res.remove(value)
        return res
