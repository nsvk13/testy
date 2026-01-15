# TestY TMS - Test Management System
# Copyright (C) 2022 KNS Group LLC (YADRO)
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
import copy
from contextlib import contextmanager
from logging import getLogger
from typing import Any

from celery_progress.backend import ProgressRecorder
from django.db.models import Subquery, fields
from simple_history.models import HistoricalRecords
from testy.users.models import User

logger = getLogger('uploader-utils')


def matched_dict(list_of_dicts: list[dict], conditional_key: str, conditional_val: Any) -> dict[str, Any]:
    """
    Find and return the dictionary from the list of dictionaries that matched the condition.

    key == value

    Args:
        list_of_dicts: the list of dictionaries:  list[dict]
        conditional_key: the key
        conditional_val: the expected value

    Returns:
        the dictionary or None
    """
    if conditional_key.endswith('id'):
        conditional_val = int(conditional_val)
    for dict_item in list_of_dicts:
        if isinstance(dict_item, dict) and dict_item.get(conditional_key) == conditional_val:
            return copy.deepcopy(dict_item)
    return {}


def get_title(plan_name, parameters):
    if not parameters:
        return plan_name
    return '{0} [{1}]'.format(
        plan_name, ', '.join(parameter.data for parameter in parameters)
    )


class ConcatSubquery(Subquery):
    template = 'ARRAY_TO_STRING(ARRAY(%(subquery)s), %(separator)s)'
    output_field = fields.CharField()

    def __init__(self, *args, separator=', ', **kwargs):
        self.separator = separator
        super().__init__(*args, **kwargs)

    def as_sql(self, compiler, connection, template=None, **extra_context):
        extra_context['separator'] = '%s'
        sql, sql_params = super().as_sql(compiler, connection, template, **extra_context)
        sql_params = sql_params + (self.separator,)
        return sql, sql_params


class ProgressRecorderContext(ProgressRecorder):
    def __init__(self, task, total, debug=False, description='Task started'):
        self.debug = debug
        self.current = 0
        self.total = total
        if self.debug:
            return
        super().__init__(task)
        self.set_progress(current=self.current, total=total, description=description)

    def progress_step(self, description: str):
        logger.info(description)
        if self.debug:
            return
        self.current += 1
        self.set_progress(self.current, self.total, description)

    def clear_progress(self):
        self.current = 0


@contextmanager
def set_history_user(user: User | None):
    class MockRequest:
        def __init__(self, user_instance):
            self.user = user_instance
    request = MockRequest(user_instance=user)
    HistoricalRecords.context.request = request
    yield
    if hasattr(HistoricalRecords.context, 'request'):
        del HistoricalRecords.context.request