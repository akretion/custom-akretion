# coding: utf-8
#    Copyright (C) 2015-TODAY Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import UserError


ISSUE_DESCRIPTION = u"""Ce qui ne va pas:
---------------------------


Voilà comment cela devrait fonctionner:
-----------------------------------------------------------
"""


class ProjectProject(models.Model):
    _inherit = 'project.project'

    issue_sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Issue sequence',
        domain=[('code', '=', 'project.task.issue')])


class ProjectTask(models.Model):
    _inherit = 'project.task'

    issue_tracker_url = fields.Char('Bug tracker URL', size=255)
    issue_number = fields.Char('Issue number', size=64)
    display_name = fields.Char(string='Name',
                               compute='_compute_display_name')
    contact_mobile = fields.Char(string='Mobile', related='create_uid.mobile')
    contact_email = fields.Char(string='Email', related='create_uid.email')
    color = fields.Integer(string='Color', compute='_compute_color')

    @api.depends('color')
    def _compute_color(self):
        result = {}
        for task in self:
            if self.env.context.get('color_based_on') == 'milestone':
                result[task.id] = task.milestone_id.color
            elif self.env.context.get('color_based_on') == 'stage':
                result[task.id] = task.stage_id.color
            else:
                result[task.id] = 0
        return result

    @api.multi
    def _read_group_stage_ids(self, domain, read_group_order=None,
                              access_rights_uid=None):
        if self.env.context.get('visible_project_ids'):
            project_ids = self.env.context['visible_project_ids']
        else:
            project_ids = self._resolve_project_id_fromenv.context()
        if not project_ids:
            return super(ProjectTask, self)._read_group_stage_ids(
                domain, read_group_order=read_group_order,
                access_rights_uid=access_rights_uid)
        else:
            # TODO impmement access_right_uid
            stage_obj = self.env['project.task.type']
            order = stage_obj._order
            if read_group_order == 'stage_id desc':
                order = '%s desc' % order
            stages = stage_obj.search([
                ('project_ids', 'in', project_ids),
                ], order=order)
            fold = {}
            result = []
            for stage in stages:
                fold[stage.id] = stage.fold or False
                result.append((stage.id, stage.name))
            return result, fold

    @api.multi
    def _read_group_project_ids(self, domain, read_group_order=None,
                                access_rights_uid=None):
        fold = {}
        result = []
        xml_ids = [
            'project_to_qualify',
            'project_todo_customer',
            'project_erp_provider',
            'project_rejected',
        ]
        for key in xml_ids:
            project = self.env.ref('project_ak.' + key)
            result.append((project.id, project.name))
            fold[project.id] = False
        return result, fold

    @api.multi
    def _read_group_milestone_ids(self, domain, read_group_order=None,
                                  access_rights_uid=None):
        fold = {}
        result = []
        milestones = self.env['project.milestone'].search([])
        for milestone in milestones:
            result.append((milestone.id, milestone.name))
            fold[milestone.id] = False
        return result, fold

    _group_by_full = {
        'stage_id': _read_group_stage_ids,
        'project_id': _read_group_project_ids,
        'milestone_id': _read_group_milestone_ids,
    }

    @api.multi
    def _set_issue_number(self):
        sequence_obj = self.env['ir.sequence']
        for task in self:
            if not task.project_id:
                continue
            sequence = task.project_id.issue_sequence_id
            project_issue = self.env.ref('project_ak.project_to_qualify')
            if task.project_id == project_issue and \
                    not task.issue_number and sequence:
                task.issue_number = sequence_obj.next_by_id(sequence.id)

    @api.model
    def default_get(self, fields):
        vals = super(ProjectTask, self).default_get(fields)
        if 'from_action' in self.env.context:
            project_to_qualify = self.env.ref('project_ak.project_to_qualify')
            vals['project_id'] = project_to_qualify.id
            vals['description'] = ISSUE_DESCRIPTION
            vals['user_id'] = None
            vals['create_uid'] = self._uid
        return vals

    @api.model
    def create(self, vals):
        task = super(ProjectTask, self).create(vals)
        task._set_issue_number()
        return task

    @api.multi
    def write(self, vals):
        if (vals.get('stage_id') and
                not self.env['res.users'].has_group(
                    'project_ak.group_customer_manager')):
            raise UserError(_('You can not change the state of the task'))

        if vals.get('project_id'):
            project_id = vals['project_id']
            for task in self:
                new_vals = vals.copy()
                if project_id != task.project_id.id:
                    project = self.env['project.project'].browse(project_id)
                    new_vals['stage_id'] = project.type_ids[0].id
                super(ProjectTask, self).write(new_vals)
            return True
        else:
            return super(ProjectTask, self).write(vals)

    @api.one
    @api.depends('name', 'issue_number')
    def _compute_display_name(self):
        if self.issue_number:
            names = [self.issue_number, self.name]
            self.display_name = ' '.join(names)
        else:
            self.display_name = self.name


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    color = fields.Integer()


# class ProjectTaskWork(models.Model):
#     _inherit = "project.task.work"

#     date = fields.Date(default=fields.Date.today())
#     invoice_number = fields.Char()
