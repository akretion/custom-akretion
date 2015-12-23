# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from datetime import datetime, timedelta


class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _description = "Milestone"
    _order = "deadline"

    name = fields.Char()
    deadline = fields.Date()
    active = fields.Boolean(default=True,
        help='If check, this object is always available')
    color = fields.Integer(
        readonly=True,
        help="Color used in task kanban view\n"
             "computed by a planified task (cron)")

    _sql_constraints = [
        ('project_milestone_unique_code', 'UNIQUE (name)',
         _('The milestone name must be unique!')),
    ]

    @api.model
    def _get_milestone_vals(self):
        vals = []
        date = datetime.today()
        for color in [2, 3, 4, 0]:
            date += timedelta(days=7)
            vals.append((date.strftime('%y.%W.1'), date, color))
        return vals

    @api.model
    def _update_milestone(self):
        """
        créer new milestones du trimestre
        désactiver les anciennes milestones
        """
        milestones = self.search([('deadline', '<', fields.Date.today())])
        milestones.write({'active': False, 'color': 0})
        for name, date, color in self._get_milestone_vals():
            milestone = self.search([('name', '=', name)])
            if milestone:
                milestone.write({'color': color})
            else:
                self.create({'name': name, 'deadline': date, 'color': color})
        return True


class ProjectTask(models.Model):
    _inherit = 'project.task'

    milestone_id = fields.Many2one(
        'project.milestone',
        string="Milestone",
        help="Tasks planification with milestones")
