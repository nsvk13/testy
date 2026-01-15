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
from defect_report.filters import DefectReportFilter
from defect_report.models import JiraTicketStatus
from defect_report.selectors import DefectReportSelector
from defect_report.serializers import DefectReportSerializer
from defect_report.tasks import handle_jira_ticket_change
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from testy.core.selectors.projects import ProjectSelector
from testy.paginations import StandardSetPagination
from testy.tests_representation.models import TestResult


@method_decorator(csrf_exempt, name='dispatch')
class JiraTicketChangeView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        handle_jira_ticket_change.delay(data=request.data)
        return Response(status=status.HTTP_200_OK)


class DefectReportPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(
            request,
            template_name='defect_report_page.html',
            context={
                'projects': [x for x in ProjectSelector(request.user).project_list_statistics() if x.is_visible],
            },
        )


class DefectReportViewSet(ListModelMixin, GenericViewSet):
    serializer_class = DefectReportSerializer
    queryset = TestResult.objects.none()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardSetPagination
    filterset_class = DefectReportFilter

    def get_queryset(self):
        attributes = self.request.GET.getlist('attributes', ['Defects'])
        return DefectReportSelector.prepare_defect_list(attributes=attributes)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated_data = self.paginator.get_paginated_response(serializer.data).data
        return JsonResponse(paginated_data)
