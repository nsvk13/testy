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
from reportlab.lib import colors, units
from reportlab.platypus import TableStyle, Flowable, LongTable

from test_plan_exporter.report.builders.base_builders import PDFElementBuilder
from test_plan_exporter.report.common import FontManager


class TableOfContentBuilder(PDFElementBuilder):
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (1, 1), (-1, -1), FontManager.regular),
        ('FONTNAME', (0, 0), (-1, 1), FontManager.bold),
    ])
    max_width = 7

    @classmethod
    def build(cls, headers: list[str], data_rows: list[list[str]], col_widths: list[int] = None) -> Flowable:
        data = [headers] + data_rows
        if not col_widths:
            col_widths = [cls.max_width / len(headers)] * len(headers)
        col_widths_calculated = [w * units.inch for w in col_widths]
        table = LongTable(data, colWidths=col_widths_calculated, repeatRows=1)
        table.setStyle(cls.style)
        return table
