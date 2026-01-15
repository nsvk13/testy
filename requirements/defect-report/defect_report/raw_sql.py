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
ATTRIBUTE_CASE_SQL = """
                        WHEN jsonb_typeof(tests_representation_testresult.attributes->'{attribute}') = 'array' THEN
                            ARRAY(SELECT jsonb_array_elements_text(tests_representation_testresult.attributes->'{attribute}'))
                        WHEN jsonb_typeof(tests_representation_testresult.attributes->'{attribute}') = 'string' THEN
                            regexp_split_to_array(tests_representation_testresult.attributes->>'{attribute}', '[{array_splits}]')

"""

ARRAY_UNPACK_SQL = """
    ARRAY(
        WITH defects_source AS (
            SELECT 
                unnest(
                    CASE 
                        {attribute_cases}
                        ELSE
                            ARRAY[]::text[]
                    END
                ) AS defect_item
        ),
        jira_keys as (
            SELECT DISTINCT (regexp_matches(defect_item, '({jira_key_regex})', 'g'))[1] as jira_key
            FROM defects_source
            WHERE defect_item IS NOT NULL
              AND defect_item ~ '({jira_key_regex})'
        )
        select jira_key
        from jira_keys
        where 1=1 
        {search_condition}
    )"""  # noqa: W291 E501
