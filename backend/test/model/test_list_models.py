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

from typing import Optional
from unittest import mock

from botocore.exceptions import ClientError

from ml_space_lambda.data_access_objects.resource_metadata import PagedMetadataResults, ResourceMetadataModel
from ml_space_lambda.enums import ResourceType
from ml_space_lambda.utils.common_functions import generate_html_response

TEST_ENV_CONFIG = {
    "AWS_DEFAULT_REGION": "us-east-1",
}
MOCK_PROJECT_NAME = "mock_models"
MOCK_USERNAME = "jdoe@amazon.com"
# Need to mock the region in order to do the import......
with mock.patch.dict("os.environ", TEST_ENV_CONFIG, clear=True):
    from ml_space_lambda.model.lambda_functions import list_resources as lambda_handler

mock_context = mock.Mock()


def _mock_model_metadata(identifier: str, username: Optional[str] = MOCK_USERNAME) -> ResourceMetadataModel:
    return ResourceMetadataModel(
        identifier,
        ResourceType.MODEL,
        username,
        MOCK_PROJECT_NAME,
        {
            "ModelArn": f"arn:aws:us-east-1:sagemaker:model/{identifier}",
            "CreationTime": "2023-08-11 09:33:05.109000+00:00",
        },
    )


@mock.patch("ml_space_lambda.model.lambda_functions.resource_metadata_dao")
def test_list_models_success(mock_resource_metadata_dao):
    mock_event = {
        "pathParameters": {"projectName": MOCK_PROJECT_NAME},
        "queryStringParameters": {"pageSize": "2", "resourceStaus": "ModelsDoNotHaveStatus"},
    }

    mock_resource_metadata_dao.get_all_for_project_by_type.return_value = PagedMetadataResults(
        [
            _mock_model_metadata("model1"),
            _mock_model_metadata("model2"),
        ],
    )

    expected_response = generate_html_response(
        200,
        {
            "records": [
                _mock_model_metadata("model1").to_dict(),
                _mock_model_metadata("model2").to_dict(),
            ],
        },
    )
    assert lambda_handler(mock_event, mock_context) == expected_response

    mock_resource_metadata_dao.get_all_for_project_by_type.assert_called_with(
        MOCK_PROJECT_NAME, ResourceType.MODEL, limit=2, next_token=None
    )


@mock.patch("ml_space_lambda.model.lambda_functions.resource_metadata_dao")
def test_list_models_client_error(mock_resource_metadata_dao):
    mock_event = {"pathParameters": {"projectName": MOCK_PROJECT_NAME}}

    error_msg = {
        "Error": {"Code": "ThrottlingException", "Message": "Dummy error message."},
        "ResponseMetadata": {"HTTPStatusCode": 400},
    }

    exception_response = ClientError(error_msg, "Query")
    mock_resource_metadata_dao.get_all_for_project_by_type.side_effect = exception_response
    expected_response = generate_html_response(
        400,
        "An error occurred (ThrottlingException) when calling the Query operation: Dummy error message.",
    )
    assert lambda_handler(mock_event, mock_context) == expected_response

    mock_resource_metadata_dao.get_all_for_project_by_type.assert_called_with(
        MOCK_PROJECT_NAME, ResourceType.MODEL, limit=100, next_token=None
    )


@mock.patch("ml_space_lambda.model.lambda_functions.resource_metadata_dao")
def test_list_models_generic_error(mock_resource_metadata_dao):
    expected_response = generate_html_response(400, "Missing event parameter: 'pathParameters'")
    assert lambda_handler({}, mock_context) == expected_response
    mock_resource_metadata_dao.get_all_for_project_by_type.assert_not_called()
