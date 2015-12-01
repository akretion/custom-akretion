# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _description = "Milestone"

    # name = fields.Char(readonly=True)
    name = fields.Char()
    deadline = fields.Date()
    active = fields.Boolean(
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
    def _recompute_milestones(self):
        """
        créer new milestones du trimestre
        désactiver les anciennes milestones
        """
        milestones = self.search([('deadline', '<', fields.Date.today())])
        milestones.write({'active': False, 'color': 0})
        milestones = self.search([('deadline', '>', fields.Date.today())])
        res = self._cr.execute('SELECT max(deadline) from project_milestone')

        res.fetchall()
        return True


class ProjectTask(models.Model):
    _inherit = 'project.task'
    #
    # @api.multi
    # @api.depends('name')
    # def _get_task_color(self):
    #     for rec in self:

    milestone_id = fields.Many2one(
        'project.milestone',
        string="Milestone",
        help="Tasks planification with milestones")
    # color = fields.Integer(_compute='_get_task_color')
