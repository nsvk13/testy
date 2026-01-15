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
from django_filters import rest_framework as filters

from testy.tests_representation.models import TestPlan, TestResult
from .selectors import DefectReportSelector


class DefectReportFilter(filters.FilterSet):
    plan_id = filters.NumberFilter(field_name='test__plan_id', required=False, method='search_plan')
    project_id = filters.NumberFilter(required=True)
    just_last_result = filters.BooleanFilter(method='search_last_result')
    search = filters.CharFilter(method='filter_by_attributes')

    def search_plan(self, queryset, name, value):
        root_plan = TestPlan.objects.get(id=value)
        return queryset.filter(test__plan__path__descendant=root_plan.path)

    def search_last_result(self, queryset, name, value):
        if value:
            return queryset.filter(rank=1)
        return queryset

    def filter_by_attributes(self, queryset, name, value):
        filtered_by_jira_key = DefectReportSelector.filter_jira_key(queryset, jira_key=value)
        return queryset.filter(test__case__name__icontains=value).union(filtered_by_jira_key)

    class Meta:
        model = TestResult
        fields = ['project_id', 'plan_id', 'just_last_result']
