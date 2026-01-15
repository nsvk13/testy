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
import json
from typing import List

from django.utils import timezone
from reportlab.platypus import Flowable
from testy.core.models import Attachment
from testy.tests_representation.models import TestPlan

from test_plan_exporter.report.builders.base_builders import (
    BoldTextBuilder,
    ImageBuilder,
    LogoBuilder,
    PageBreakBuilder,
    PDFElementBuilder,
    SectionHeaderBuilder,
    SpacerBuilder,
    TextBuilder,
    TitlePageHeaderBuilder,
    TitlePageSubtitleBuilder,
    StepFieldBuilder,
    StepFieldBoldBuilder,
)
from test_plan_exporter.report.builders.markdown import MarkdownConverter


class MarkDownTextBuilder(PDFElementBuilder):
    @classmethod
    def build(cls, text: str, text_builder_class=TextBuilder, **builder_params) -> list[Flowable]:
        con = MarkdownConverter(text_builder_class=text_builder_class, **builder_params)
        elems = con.convert(str(text))
        if elems:
            return elems
        else:
            return [text_builder_class.build(text)]


class TextFieldPairBuilder(PDFElementBuilder):

    @classmethod
    def build(cls, label: str, value: str, is_md_format: bool = False) -> List[Flowable]:
        elements = [BoldTextBuilder.build(label)]
        if is_md_format:
            elements.extend(MarkDownTextBuilder.build(value))
        else:
            elements.append(TextBuilder.build(value))

        return elements


class StepTextFieldPairBuilder(PDFElementBuilder):

    @classmethod
    def build(cls, label: str, value: str, is_md_format: bool = False) -> List[Flowable]:
        elements = [StepFieldBoldBuilder.build(label)]
        if is_md_format:
            elements.extend(MarkDownTextBuilder.build(value, text_builder_class=StepFieldBuilder))
        else:
            elements.append(StepFieldBuilder.build(value))

        return elements


class AttachmentsBuilder(PDFElementBuilder):

    @classmethod
    def build(cls, attachments: list[Attachment]) -> List[Flowable]:
        elements = []
        for attachment in attachments:
            elements.extend(ImageBuilder.build(attachment.file.path, filename=attachment.filename))
        if elements:
            return [
                BoldTextBuilder.build('Вложения:'),
                *elements,
                SpacerBuilder.build(1, 5)
            ]
        return []


class CommentBlockBuilder(PDFElementBuilder):
    @classmethod
    def build(cls, text, attachments: list[Attachment], block_name: str = 'Комментарий') -> List[Flowable]:

        elements = []
        for attachment in attachments:
            elements.extend(ImageBuilder.build(attachment.file.path, filename=attachment.filename))

        if text or elements:
            return [
                *TextFieldPairBuilder.build(block_name, text, is_md_format=True),
                *elements,
                SpacerBuilder.build(1, 5)
            ]
        return []


class TitlePageBuilder(PDFElementBuilder):

    @classmethod
    def build(cls, report_name: str, plan_name: str, description: str) -> List[Flowable]:
        date_text = f'Дата формирования: {timezone.now().strftime("%d.%m.%Y")}'
        return [
            LogoBuilder.build(),
            SpacerBuilder.build(1, 50),
            TitlePageHeaderBuilder.build(report_name),
            TitlePageSubtitleBuilder.build(plan_name),
            SpacerBuilder.build(1, 10),
            TextBuilder.build(description),
            SpacerBuilder.build(1, 20),
            TextBuilder.build(date_text),
            PageBreakBuilder.build(),
        ]


class PlanInfoBuilder(PDFElementBuilder):

    @classmethod
    def build(cls, node: TestPlan) -> List[Flowable]:
        elements = [SectionHeaderBuilder.build('Информация о плане')]
        elements.extend(TextFieldPairBuilder.build('ID плана', str(node.id)))

        start_date = node.started_at.strftime('%d.%m.%Y') if node.started_at else ''
        finish_date = node.due_date.strftime('%d.%m.%Y') if node.due_date else ''
        elements.extend(TextFieldPairBuilder.build('Дата начала', start_date))
        elements.extend(TextFieldPairBuilder.build('Дата завершения', finish_date))

        elements.extend(TextFieldPairBuilder.build('Описание', node.description, is_md_format=True))
        attachments = node.attachments.all()
        elements.extend(AttachmentsBuilder.build(attachments))

        elements.append(SpacerBuilder.build(1, 20))
        return elements


class AttributesBuilder(PDFElementBuilder):
    _key_width = 70

    @classmethod
    def build(cls, attributes: dict) -> list[Flowable]:
        data = []
        for key, value in attributes.items():
            data.extend(
                    TextFieldPairBuilder.build(
                        key.ljust(cls._key_width),
                        json.dumps(value, indent=4, ensure_ascii=False) if isinstance(value, (dict, list)) else value,
                        is_md_format=True,
                    )
            )

        return data
