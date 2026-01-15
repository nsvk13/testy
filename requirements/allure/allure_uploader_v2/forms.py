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
from django import forms
from django.contrib.auth import get_user_model
from testy.tests_representation.models import Parameter, TestPlan

from allure_uploader_v2.models import ServiceType, UploaderConfigV2
from allure_uploader_v2.uploader_lib.services import UploaderUserService

UserModel = get_user_model()


class ParsingSubmitForm(forms.Form):
    config = forms.ModelChoiceField(
        UploaderConfigV2.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    allure_url = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start typing'}))
    allure_archive = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['config'].queryset = UploaderUserService.config_list(request.user)


class UploaderConfigForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        ServiceType.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    field_order = (
        'verbose_name',
        'project', 'plan',
        'child_plan',
        'parameters',
        'auto_suite_name',
        'jira_projects',
        'custom_attributes',
        'envs_to_parse',
        'additional_parameters',
        'allowed_users',
        'owner',
        'labels',
        'add_allure_source',
    )

    class Meta:
        model = UploaderConfigV2
        fields = ('project', 'plan', 'child_plan', 'parameters', 'auto_suite_name', 'jira_projects',
                  'custom_attributes', 'envs_to_parse', 'additional_parameters', 'verbose_name', 'owner',
                  'allowed_users', 'labels', 'service', 'add_allure_source', 'skip_creating_case')
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'plan': forms.Select(attrs={'placeholder': 'Start typing'}),
            'child_plan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inner test plan name'}),
            'auto_suite_name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_projects': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TST-,TMS-,STOR-'}),
            'custom_attributes': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Version,Stand,Device'}
            ),
            'envs_to_parse': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': """REAL_NAME:desired name\nPORT\n"""},
            ),
            'additional_parameters': forms.Textarea(attrs={'class': 'form-control'}),
            'verbose_name': forms.TextInput(attrs={'class': 'form-control'}),
            'labels': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto,release,ver 1.2.1'}),
            'owner': forms.HiddenInput(),
            'add_allure_source': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'skip_creating_case': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].initial = request.user
        self.fields['plan'].queryset = TestPlan.objects.none()
        if 'project' in self.data:
            try:
                project_id = int(self.data.get('project'))
                self.fields['plan'].queryset = TestPlan.objects.filter(
                    project_id=project_id,
                    is_archive=False
                ).order_by('name')
                self.fields['parameters'].queryset = Parameter.objects.filter(
                    project_id=project_id,
                ).order_by('group_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['allowed_users'].queryset = self.instance.allowed_users
            self.fields['plan'].queryset = TestPlan.objects.filter(
                project=self.instance.project,
                is_archive=False
            ).order_by('name')
            self.fields['parameters'].queryset = Parameter.objects.filter(
                project=self.instance.project,
            ).order_by('group_name')
