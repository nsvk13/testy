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
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import FileField, ModelSerializer, PrimaryKeyRelatedField, Serializer

from allure_uploader_v2.models import UploaderConfigV2, UserTask


class AllureUploaderSerializerV2(Serializer):
    allure_url = CharField(required=False)
    allure_file = FileField(required=False)
    plans_hierarchy = CharField(required=False)
    hierarchy_separator = CharField(required=False, default='->')
    config = PrimaryKeyRelatedField(queryset=UploaderConfigV2.objects.all(), many=False, required=True)

    def validate(self, attrs):
        if not attrs.get('allure_url') and not attrs.get('allure_file'):
            raise ValidationError('Allure report source was not provided')
        return attrs


class APITaskResponseSerializerV2(Serializer):
    task_id = CharField()


class AllureUploaderConfigV2Serializer(ModelSerializer):
    class Meta:
        model = UploaderConfigV2
        exclude = ['is_deleted', 'deleted_at', 'created_at', 'updated_at']


class UserTaskSerializer(ModelSerializer):
    class Meta:
        model = UserTask
        fields = '__all__'
