# TestY TMS - Test Management System
# Copyright (C) 2025 KNS Group LLC (YADRO)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Also add information on how to contact you by electronic and paper mail.
#
# If your software can interact with users remotely through a computer
# network, you should also make sure that it provides a way for users to
# get its source.  For example, if your program is a web application, its
# interface could display a "Source" link that leads users to an archive
# of the code.  There are many ways you could offer source, and different
# solutions will be better for different programs; see section 13 for the
# specific requirements.
#
# You should also get your employer (if you work as a programmer) or school,
# if any, to sign a "copyright disclaimer" for the program, if necessary.
# For more information on this, and how to apply and follow the GNU AGPL, see
# <http://www.gnu.org/licenses/>.
from datetime import datetime

from rest_framework import fields
from rest_framework.serializers import Serializer, ValidationError


class DefectReportSerializer(Serializer):
    result_id = fields.IntegerField(read_only=True, source='id')
    defect = fields.CharField(read_only=True, source='jira_key')
    plan_id = fields.CharField(read_only=True, source='test.plan_id')
    plan_name = fields.CharField(read_only=True, source='test.plan.name')
    plan_breadcrumbs = fields.SerializerMethodField()
    result_rank = fields.IntegerField(read_only=True, source='rank')
    test_name = fields.CharField(read_only=True, source='test.case.name')
    test_id = fields.IntegerField(read_only=True)
    result_status = fields.CharField(read_only=True, source='status.name')
    latest_result_status = fields.CharField(read_only=True, source='test.last_status.name')
    latest_result_color = fields.CharField(read_only=True, source='test.last_status.color')
    result_status_color = fields.CharField(read_only=True, source='status.color')
    result_date = fields.DateTimeField(read_only=True, source='updated_at')

    def get_plan_breadcrumbs(self, obj):
        return ' -> '.join([plan.name for plan in obj.test.plan.get_ancestors()])


class JiraWebhookDataSerializer(Serializer):
    key = fields.CharField(required=True)
    status = fields.CharField(required=True)
    updated_at = fields.DateTimeField(required=True)

    def validate(self, data):
        issue = self.initial_data.get('issue', {})
        ticket_fields = issue.get('fields', {})
        data['status'] = ticket_fields.get('status', {}).get('name')
        if not data['status']:
            ValidationError('Status is not found')

        data['key'] = issue.get('key')
        if not data['key']:
            ValidationError('key is not found')

        timestamp = self.initial_data.get('timestamp')
        if timestamp and isinstance(timestamp, int):
            data['updated_at'] = datetime.fromtimestamp(timestamp / 1000)
        else:
            data['updated_at'] = datetime.utcnow()

        return data
