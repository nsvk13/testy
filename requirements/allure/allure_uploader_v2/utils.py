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
from hashlib import md5
from pathlib import Path

from django.core import serializers

from allure_uploader_v2.models import UploaderConfigV2


def get_md5_from_value(value: str) -> str:
    return md5(str(value).encode()).hexdigest()


def upload_file_to_system(tmp_filepath: Path, archive_name: str, file) -> Path:
    if not tmp_filepath.exists():
        tmp_filepath.mkdir(exist_ok=True, parents=True)
    filepath = tmp_filepath / archive_name
    with open(filepath, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return filepath


def config_json_snapshot(config: UploaderConfigV2) -> str:
    return serializers.serialize('json', [config], use_natural_foreign_keys=True, indent=4)


def config_from_json_snapshot(json_snapshot: str) -> UploaderConfigV2:
    if json_snapshot:
        config_list = [conf.object for conf in serializers.deserialize('json', json_snapshot)]
        if config_list:
            return config_list[0]
    return None
