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

# Testing for the describe_labeling_job Lambda function.
from unittest import mock

from botocore.exceptions import ClientError

from ml_space_lambda.utils.common_functions import generate_html_response

TEST_ENV_CONFIG = {
    "AWS_DEFAULT_REGION": "us-east-1",
}

with mock.patch.dict("os.environ", TEST_ENV_CONFIG, clear=True):
    from ml_space_lambda.labeling_job.lambda_functions import describe as lambda_handler

labeling_job_name = "example_labeling_job_name"

mock_event = {"pathParameters": {"jobName": f"{labeling_job_name}"}}
mock_context = mock.Mock()

mock_response = {
    "LabelingJobArn": "example_arn",
    "LabelingJobName": f"{labeling_job_name}",
}


@mock.patch("ml_space_lambda.labeling_job.lambda_functions.sagemaker")
def test_describe_labeling_job_success(mock_sagemaker):
    mock_sagemaker.describe_labeling_job.return_value = mock_response

    expected_response = generate_html_response(200, mock_response)

    assert lambda_handler(mock_event, mock_context) == expected_response

    mock_sagemaker.describe_labeling_job.assert_called_with(LabelingJobName=labeling_job_name)


@mock.patch("ml_space_lambda.labeling_job.lambda_functions.sagemaker")
def test_describe_labeling_job_client_error(mock_sagemaker):
    error_msg = {
        "Error": {"Code": "ThrottlingException", "Message": "Dummy error message."},
        "ResponseMetadata": {"HTTPStatusCode": 400},
    }

    expected_response = generate_html_response(
        400,
        "An error occurred (ThrottlingException) when calling the DescribeLabelingJob operation: Dummy error message.",
    )

    mock_sagemaker.describe_labeling_job.side_effect = ClientError(error_msg, "DescribeLabelingJob")

    assert lambda_handler(mock_event, mock_context) == expected_response

    mock_sagemaker.describe_labeling_job.assert_called_with(LabelingJobName=labeling_job_name)


@mock.patch("ml_space_lambda.labeling_job.lambda_functions.sagemaker")
def test_describe_labeling_job_missing_parameters(mock_sagemaker):
    expected_response = generate_html_response(400, "Missing event parameter: 'pathParameters'")
    assert lambda_handler({}, mock_context) == expected_response
    mock_sagemaker.describe_labeling_job.assert_not_called()