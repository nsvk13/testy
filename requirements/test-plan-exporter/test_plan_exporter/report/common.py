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
import os
import re
from datetime import datetime

from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable

FOOTER_IMAGE = 'test_plan_exporter/img/report_footer_title.png'

def save_pdf_to_file(pdf_buffer, node_name, file_prefix='report'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    node_name_cleared = re.sub(r'[<>:"/\\|?*.]', '', node_name)
    filename = f'{file_prefix}_{node_name_cleared}_{timestamp}.pdf'
    file_path = f'reports/{filename}'
    return default_storage.save(file_path, ContentFile(pdf_buffer.getvalue()))


class BookmarkFlowable(Flowable):
    def __init__(self, key):
        self.key = key

    def draw(self):
        try:
            self.canv.bookmarkPage(self.key)
        except Exception:
            pass

    def wrap(self, availWidth, availHeight):
        return (0, 0)


class FooterCanvas:
    def __init__(self):
        self.style = ParagraphStyle(name='footer', fontSize=8, textColor=colors.gray, fontName=FontManager.regular)
        self.image_path = finders.find(FOOTER_IMAGE)

    def draw_footer(self, canvas, doc):
        page_num = canvas.getPageNumber()

        if page_num == 1 and self.image_path and os.path.exists(self.image_path):
            try:
                canvas.drawImage(self.image_path, 0, 0, width=A4[0], height=200)
            except Exception:
                pass
        else:
            canvas.setFont(self.style.fontName, self.style.fontSize)
            canvas.setFillColor(self.style.textColor)
            canvas.drawRightString(A4[0] - 40, 40, str(page_num))


class FontManager:
    regular: str = 'regular'
    bold: str = 'bold'
    italic: str = 'italic'
    emoji: str = 'emoji'

    _fonts: dict = {
        regular: 'test_plan_exporter/fonts/Inter-VariableFont.ttf',
        bold: 'test_plan_exporter/fonts/Inter-VariableFont.ttf',
        italic: 'test_plan_exporter/fonts/Inter-VariableFont.ttf',
        emoji: 'test_plan_exporter/fonts/Inter-VariableFont.ttf',
    }

    @staticmethod
    def setup_fonts():
        for font_key, font_path in FontManager._fonts.items():
            full_font_path = finders.find(font_path)
            if full_font_path and os.path.exists(full_font_path):
                pdfmetrics.registerFont(TTFont(font_key, full_font_path))
