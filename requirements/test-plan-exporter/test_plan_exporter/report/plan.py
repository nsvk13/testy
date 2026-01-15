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
from collections import defaultdict
from typing import List

from reportlab.platypus import Flowable
from testy.tests_description.models import TestCase, TestCaseStep
from testy.tests_representation.models import TestStepResult

from test_plan_exporter.report.base import (
    BaseLastResultBuilder,
    BasePDFReport,
    BaseStepBuilder,
    BaseTestSectionBuilder,
)
from test_plan_exporter.report.builders.base_builders import (
    LinkBuilder,
    PageBreakBuilder,
    SpacerBuilder,
    StepFieldBoldBuilder,
    TextBuilder,
)


class EmptyLastResultBuilder(BaseLastResultBuilder):
    @classmethod
    def build(cls, test) -> List[Flowable]:
        elements = cls.make_result_title()
        elements.append(SpacerBuilder.build(1, 30))
        return elements


class StepWithOutResultBuilder(BaseStepBuilder):
    @classmethod
    def make_result(cls, step_result: TestStepResult) -> List[Flowable]:
        return [
            StepFieldBoldBuilder.build('Результат'),
            SpacerBuilder.build(1, 20),
        ]


class TestPlanSectionBuilder(BaseTestSectionBuilder):
    _step_builder = StepWithOutResultBuilder
    _last_result_builder = EmptyLastResultBuilder

    @staticmethod
    def calc_case_version(test) -> int:
        return getattr(test, 'version', 1)

    @classmethod
    def get_test_case(cls, test) -> TestCase:
        return test.case

    @classmethod
    def get_steps(cls, test) -> list[TestCaseStep]:
       return test.case.steps.all()


class TestPlanPDFReport(BasePDFReport):
    _test_section_builder = TestPlanSectionBuilder
    _table_of_content_headers = ['Case ID', 'Version', 'Test Name']
    _table_of_content_col_size = [1.0, 1.0, 5.0]

    @staticmethod
    def _group_tests(tests):
        grouped = defaultdict(list)
        for test in tests:
            grouped[test.case.suite.name].append(test)
        return dict(grouped)

    @staticmethod
    def _table_of_content_rows(tests):
        return [
            [
                TextBuilder.build(str(test.case.id)),
                TextBuilder.build(str(getattr(test, 'version', 1))),
                LinkBuilder.build(str(test.case.id), test.case.name),
            ] for test in tests
        ]

    @classmethod
    def _build_story(cls, node, tests, **kwargs):
        elements = []
        grouped_tests = cls._group_tests(tests)

        elements.extend(cls._add_title_page('Отчет о плане тестирования', node.name, ' '))
        elements.extend(cls._add_plan_info(node))
        elements.append(PageBreakBuilder.build())
        elements.extend(cls._add_table_of_contents(grouped_tests))
        elements.extend(cls._add_tests(grouped_tests))

        return elements




def generate_report_pdf(node, tests, attachment_map):
    return TestPlanPDFReport.generate_report(node, tests, attachment_map)
