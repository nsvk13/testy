# TestY TMS - Test Management System
# Copyright (C) 2024 KNS Group LLC (YADRO)
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
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from testy.core.models import Project
from testy.root.models import BaseModel
from testy.tests_representation.models import Parameter, TestPlan

UserModel = get_user_model()


def default_labels() -> list[str]:
    return ['autotest']


class TaskStatus(models.TextChoices):
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
    IN_PROGRESS = 'IN_PROGRESS'


class ServiceType(BaseModel):
    verbose_name = models.CharField(max_length=255)
    service_code = models.IntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.verbose_name


class UploaderConfigV2(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True)
    plan = models.ForeignKey(TestPlan, on_delete=models.SET_NULL, null=True)
    child_plan = models.CharField(max_length=255, blank=True)
    parameters = models.ManyToManyField(Parameter, blank=True)
    auto_suite_name = models.CharField(max_length=255, blank=True, default='auto')
    jira_projects = models.CharField(max_length=255, blank=True)
    custom_attributes = models.TextField(blank=True)
    envs_to_parse = models.TextField(blank=True)
    additional_parameters = models.JSONField(default=dict, blank=True)
    verbose_name = models.CharField(max_length=255)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    allowed_users = models.ManyToManyField(UserModel, blank=True, related_name='allowed_users')
    labels = ArrayField(models.CharField(max_length=255), default=default_labels)
    add_allure_source = models.BooleanField(default=False)
    skip_creating_case = models.BooleanField(default=False)

    def __str__(self):
        return self.verbose_name


class UserTask(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    plan = models.ForeignKey(TestPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(default=TaskStatus.IN_PROGRESS, choices=TaskStatus.choices)
    error = models.CharField(null=True)
