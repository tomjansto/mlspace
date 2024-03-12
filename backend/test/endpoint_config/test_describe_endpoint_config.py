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

# Testing for the describe_endpoint_config Lambda function
from unittest import mock

from botocore.exceptions import ClientError

from ml_space_lambda.utils.common_functions import generate_html_response

TEST_ENV_CONFIG = {
    "AWS_DEFAULT_REGION": "us-east-1",
}
mock_context = mock.Mock()
# Need to mock the region in order to do the import......
with mock.patch.dict("os.environ", TEST_ENV_CONFIG, clear=True):
    from ml_space_lambda.endpoint_config.lambda_functions import describe as lambda_handler


@mock.patch("ml_space_lambda.endpoint_config.lambda_functions.sagemaker")
def test_describe_endpoint_config_success(mock_sagemaker):
    mock_event = {"pathParameters": {"endpointConfigName": "example_endpoint"}}
    mock_response = {
        "EndpointConfigName": "example_endpoint",
        "ConfigStatus": "Fake",
    }

    mock_sagemaker.describe_endpoint_config.return_value = mock_response
    expected_response = generate_html_response(200, mock_response)

    assert lambda_handler(mock_event, mock_context) == expected_response
    mock_sagemaker.describe_endpoint_config.assert_called_with(
        EndpointConfigName="example_endpoint"
    )


@mock.patch("ml_space_lambda.endpoint_config.lambda_functions.sagemaker")
def test_describe_endpoint_config_client_error(mock_sagemaker):
    mock_event = {"pathParameters": {"endpointConfigName": "example_endpoint"}}
    error_msg = {
        "Error": {"Code": "MissingParameter", "Message": "Dummy error message."},
        "ResponseMetadata": {"HTTPStatusCode": "400"},
    }

    mock_sagemaker.describe_endpoint_config.side_effect = ClientError(
        error_msg, "DescribeEndpointConfig"
    )
    expected_response = generate_html_response(
        "400",
        "An error occurred (MissingParameter) when calling the DescribeEndpointConfig operation: Dummy error message.",
    )

    assert lambda_handler(mock_event, mock_context) == expected_response
    mock_sagemaker.describe_endpoint_config.assert_called_with(
        EndpointConfigName="example_endpoint"
    )


@mock.patch("ml_space_lambda.endpoint_config.lambda_functions.sagemaker")
def test_describe_endpoint_config_missing_parameters(mock_sagemaker):
    expected_response = generate_html_response(400, "Missing event parameter: 'pathParameters'")
    assert lambda_handler({}, mock_context) == expected_response
    mock_sagemaker.describe_endpoint_config.assert_not_called()
