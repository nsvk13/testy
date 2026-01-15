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
# interface could display a 'Source' link that leads users to an archive
# of the code.  There are many ways you could offer source, and different
# solutions will be better for different programs; see section 13 for the
# specific requirements.
#
# You should also get your employer (if you work as a programmer) or school,
# if any, to sign a 'copyright disclaimer' for the program, if necessary.
# For more information on this, and how to apply and follow the GNU AGPL, see
# <http://www.gnu.org/licenses/>.
from rest_framework import serializers
from testy.tests_representation.api.v2.serializers import (
    TestPlanOutputSerializer,
    TestSerializer,
)
from testy.tests_representation.models import Test, TestPlan

from test_plan_exporter.models import DocumentRequest

TESTPLAN = 'testplan'
TESTREPORT = 'testreport'


class TestTreeSerializer(TestSerializer):
    name = serializers.CharField(source='case.name')

    class Meta:
        model = Test
        fields = ('id', 'name')


class TestPlanSerializer(TestPlanOutputSerializer):
    tests = TestTreeSerializer(many=True, read_only=True)

    class Meta:
        model = TestPlan
        fields = ('tests', 'id', 'name', 'parent')
        read_only_fields = fields


class BaseDocumentInputParamsSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(min_value=1)
    testplan_id = serializers.IntegerField(min_value=1)


class TestPlanDocumentInputParamsSerializer(BaseDocumentInputParamsSerializer):
    selected_test_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, min_length=1,
    )


class TestReportDocumentInputParamsSerializer(BaseDocumentInputParamsSerializer):
    conclusion = serializers.CharField(max_length=5000, allow_blank=True, required=False, default='')


class DocumentRequestSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    can_download = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    project_id = serializers.IntegerField(source='project_id', read_only=True)
    testplan_id = serializers.IntegerField(source='testplan_id', read_only=True)

    class Meta:
        model = DocumentRequest
        fields = [
            'id',
            'document_type',
            'document_type_display',
            'status',
            'status_display',
            'project_id',
            'testplan_id',
            'request_params',
            'file_name',
            'error_message',
            'task_id',
            'created_at',
            'updated_at',
            'completed_at',
            'can_download',
            'download_url',
        ]
        read_only_fields = [
            'id',
            'status',
            'file_name',
            'error_message',
            'task_id',
            'created_at',
            'updated_at',
            'completed_at',
        ]

    def get_can_download(self, obj):
        return obj.status == DocumentRequest.Status.DONE and obj.file_path

    def get_download_url(self, obj):
        if self.get_can_download(obj):
            return f'/plugins/test-plan-exporter/api/download/{obj.id}/'
        return None
