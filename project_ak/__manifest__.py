# coding: utf-8
# © 2018 @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Project Akretion',
    'summary': 'Custom for Akretion',
    'version': '10.0.0.0.1',
    "category": "Project Management",
    'description': """\
This module extends the ``Project`` module to allow manage issues with tasks.
Please refer to that module's description.
""",
    'author': "Akretion",
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'project_milestone',
        'project_model_to_task',
    ],
    'data': [
        'project_data.xml',
        'security/group.xml',
        'project_view.xml',
        # 'wizard/invoice_work_view.xml',
    ],
    'installable': True,
}
