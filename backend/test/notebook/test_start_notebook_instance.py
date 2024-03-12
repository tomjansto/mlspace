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

# Testing for the start_notebook_instance Lambda function
from unittest import mock

from botocore.exceptions import ClientError

from ml_space_lambda.utils.common_functions import generate_html_response

TEST_ENV_CONFIG = {
    "AWS_DEFAULT_REGION": "us-iso-east-1",
}
# Need to mock the region in order to do the import......
with mock.patch.dict("os.environ", TEST_ENV_CONFIG, clear=True):
    from ml_space_lambda.notebook.lambda_functions import start as lambda_handler

mock_event = {
    "pathParameters": {"notebookName": "sample-notebook"},
}
mock_context = mock.Mock()

mock_sagemaker_response_success = {
    "NotebookInstanceStatus": "Running",
}


@mock.patch("ml_space_lambda.notebook.lambda_functions.sagemaker")
def test_start_notebook_instance_success(mock_sagemaker):
    expected_response = generate_html_response(200, mock_sagemaker_response_success)
    mock_sagemaker.start_notebook_instance.return_value = mock_sagemaker_response_success
    assert lambda_handler(mock_event, mock_context) == expected_response
    mock_sagemaker.start_notebook_instance.assert_called_with(
        NotebookInstanceName="sample-notebook",
    )


@mock.patch("ml_space_lambda.notebook.lambda_functions.sagemaker")
def test_start_notebook_instance_failed_sagemaker(mock_sagemaker):
    error_msg = {
        "Error": {"Code": "MissingParameter", "Message": "Dummy error message."},
        "ResponseMetadata": {"HTTPStatusCode": "400"},
    }
    expected_response = generate_html_response(
        "400",
        "An error occurred (MissingParameter) when calling the StartNotebookInstance operation: Dummy error message.",
    )
    error_response = ClientError(error_msg, "StartNotebookInstance")
    mock_sagemaker.start_notebook_instance.side_effect = error_response
    assert lambda_handler(mock_event, mock_context) == expected_response
    mock_sagemaker.start_notebook_instance.assert_called_with(
        NotebookInstanceName="sample-notebook",
    )


@mock.patch("ml_space_lambda.notebook.lambda_functions.sagemaker")
def test_start_notebook_instance_missing_parameters(mock_sagemaker):
    expected_response = generate_html_response(400, "Missing event parameter: 'pathParameters'")
    assert lambda_handler({}, mock_context) == expected_response
    mock_sagemaker.start_notebook_instance.assert_not_called()
