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
import shutil
import zipfile
import tarfile
from logging import getLogger
from pathlib import Path

import requests

from allure_uploader_v2.uploader_lib.utils import ProgressRecorderContext

logger = getLogger('downloader')


class Downloader:
    """Class for downloading allure report."""
    error_msg = 'An error occurred during downloading and unpacking allure report. Following error occurred {0}'

    def __init__(
        self,
        progress_recorder: ProgressRecorderContext,
        temp_file_path: Path,
        *,
        allure_url: str | None = None,
        archive_path: Path | None = None,
        archive_strategy = None
    ):
        self.progress_recorder = progress_recorder
        self.error: Exception | None = None
        self.archive_path = archive_path
        self.allure_url = self._format_archive_url(allure_url)

        if archive_strategy:
            self.archive_strategy = archive_strategy
        else:
            self.archive_strategy = 'tar.gz' if allure_url and allure_url.endswith('tar.gz') else 'zip'

        self.temp_file_path = temp_file_path
        if not self.archive_path and not allure_url:
            raise OSError('No allure report source was specified')

    def __enter__(self) -> Path | Exception:
        try:
            if not self.temp_file_path.exists():
                self.temp_file_path.mkdir(parents=True, exist_ok=True)

            archive_path = self.archive_path

            if self.allure_url:
                archive_path = self._download_allure_report()

            if not archive_path:
                raise OSError('No archive path provided.')

            return self._unpack_archive(archive_path)

        except Exception as error:
            logger.warning(self.error_msg.format(str(self.error)))
            return error

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Remove tmp directory and all its contents."""
        logger.debug('Cleaning up files')
        if self.temp_file_path.exists():
            shutil.rmtree(self.temp_file_path)

    @classmethod
    def _format_archive_url(cls, url: str | None) -> str | None:
        """
        Removes trailing slash from allure url.
        """
        if url is None:
            return None
        return url if not url.endswith('/') else url[:-1]

    def _download_allure_report(self) -> Path:
        archive_path = self.temp_file_path / f'report.{self.archive_strategy}'
        self.progress_recorder.progress_step(f'Downloading allure report from {self.allure_url}')
        with requests.get(self.allure_url, stream=True, verify=False) as response:
            with open(archive_path, 'wb') as archive:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    archive.write(chunk)
        self.progress_recorder.progress_step('Allure download finished')
        return archive_path

    def _unpack_archive(self, archive_path: Path) -> Path:
        self.progress_recorder.progress_step('Unpacking report')

        if self.archive_strategy == 'zip':
            unpacked_path = self.temp_file_path / 'unzipped'
            if not unpacked_path.exists():
                unpacked_path.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive_path, 'r') as archive:
                archive.extractall(unpacked_path)

        if self.archive_strategy == 'tar.gz':
            unpacked_path = self.temp_file_path / 'untarred'
            if not unpacked_path.exists():
                unpacked_path.mkdir(parents=True, exist_ok=True)
            with tarfile.open(archive_path, 'r') as archive:
                archive.extractall(unpacked_path)

        self.progress_recorder.progress_step('Unpacking finished')
        return next(unpacked_path.iterdir())
