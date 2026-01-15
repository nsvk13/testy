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
import logging
import os

from celery import shared_task
from django.db import DatabaseError, transaction
from django.utils import timezone
from testy.tests_representation.models import TestPlan
import test_plan_exporter.report.plan
import test_plan_exporter.report.result
from test_plan_exporter import report
from .models import DocumentRequest

from test_plan_exporter.selectors import TestPlanSelector, TestResultsSelector, map_attachments

CAN_USE_DEFECT_REPORT = False
try:
    from defect_report.selectors import DefectReportSelector
    CAN_USE_DEFECT_REPORT = True
except ImportError:
    pass

logger = logging.getLogger(__name__)


@shared_task()
def generate_testplan_document(document_request_id):
    try:
        with transaction.atomic():
            doc_request = DocumentRequest.objects.select_for_update().get(
                id=document_request_id,
                status=DocumentRequest.Status.PENDING,
            )
            doc_request.status = DocumentRequest.Status.IN_PROGRESS
            doc_request.save()
    except DatabaseError as e:
        logger.error(e)
        return

    params = doc_request.request_params
    testplan_id = params.get('testplan_id')
    selected_test_ids = params.get('selected_test_ids', [])

    node = TestPlan.objects.get(id=testplan_id)

    tests, attachments = TestPlanSelector.get_test_plan_tests(node, selected_test_ids)
    attachments_map = map_attachments(attachments)
    try:
        pdf_buffer = test_plan_exporter.report.plan.generate_report_pdf(node, tests, attachments_map)
        file_path = report.common.save_pdf_to_file(pdf_buffer, node.name, 'testplan')

        doc_request.status = DocumentRequest.Status.DONE
        doc_request.file_path = file_path
        doc_request.file_name = os.path.basename(file_path)

    except Exception as e:
        doc_request.status = DocumentRequest.Status.FAILED
        doc_request.error_message = str(e)

    doc_request.completed_at = timezone.now()
    doc_request.save()


@shared_task()
def generate_testreport_document(document_request_id):
    try:
        with transaction.atomic():
            doc_request = DocumentRequest.objects.select_for_update().get(
                id=document_request_id,
                status=DocumentRequest.Status.PENDING,
            )
            doc_request.status = DocumentRequest.Status.IN_PROGRESS
            doc_request.save()
    except DatabaseError as e:
        logger.error(e)
        return

    params = doc_request.request_params
    project_id = params.get('project_id')
    testplan_id = params.get('testplan_id')
    conclusion = params.get('conclusion', '')

    node = TestPlan.objects.get(id=testplan_id)
    tests, attachments = TestResultsSelector.get_testplan_tests(node)
    attachments_map = map_attachments(attachments)

    if CAN_USE_DEFECT_REPORT:
        try:
            root_plan = TestPlan.objects.get(id=testplan_id)
            all_defects_qs = (
                DefectReportSelector.prepare_defect_list(attributes=['Defects'])
                .filter(project_id=project_id)
                .filter(test__plan__path__descendant=root_plan.path)
            )
        except Exception as e:
            logger.warning(f'Не удалось получить данные о дефектах: {str(e)}')

    try:
        pdf_buffer = test_plan_exporter.report.result.generate_report_pdf(
            node,
            tests,
            attachments_map,
            defects=all_defects_qs,
            conclusion=conclusion,
        )
        file_path = report.common.save_pdf_to_file(pdf_buffer, node.name, 'testreport')

        doc_request.status = DocumentRequest.Status.DONE
        doc_request.file_path = file_path
        doc_request.file_name = os.path.basename(file_path)

    except Exception as e:
        doc_request.status = DocumentRequest.Status.FAILED
        doc_request.error_message = str(e)
        logger.exception(e)

    doc_request.completed_at = timezone.now()
    doc_request.save()
