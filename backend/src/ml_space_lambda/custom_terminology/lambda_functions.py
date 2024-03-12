#
#   Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import logging

import boto3

from ml_space_lambda.utils.common_functions import (
    api_wrapper,
    list_custom_terminologies_for_project,
    retry_config,
)

translate = boto3.client("translate", config=retry_config)
log = logging.getLogger(__name__)


@api_wrapper
def list(event, context):
    return list_custom_terminologies_for_project(
        client=translate,
        fetch_all=False,
        paging_options=event["queryStringParameters"] if "queryStringParameters" in event else None,
    )
