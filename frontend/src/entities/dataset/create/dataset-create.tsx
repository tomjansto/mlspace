/**
  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Form from '@cloudscape-design/components/form';
import {
    Button,
    SpaceBetween,
    Header,
    FormField,
    Input,
    Container,
    Select,
    ContentLayout,
    Popover,
    StatusIndicator,
    Alert,
    Textarea,
} from '@cloudscape-design/components';
import { useAppDispatch } from '../../../config/store';
import { setBreadcrumbs } from '../../../shared/layout/navigation/navigation.reducer';
import {
    IDataset,
    defaultDataset,
    DatasetType,
} from '../../../shared/model/dataset.model';
import { enumToOptions, initCap } from '../../../shared/util/enum-utils';
import './dataset-create.styles.css';
import { ManageFiles } from '../manage/dataset.files';
import { IDatasetFile } from '../../../shared/model/datasetfile.model';
import { useAuth } from 'react-oidc-context';
import { buildS3Keys, createDataset, determineScope, uploadFiles } from '../dataset.service';
import NotificationService from '../../../shared/layout/notification/notification.service';
import { z } from 'zod';
import { createDatasetFromForm } from './dataset-create-functions';
import { getBase } from '../../../shared/util/breadcrumb-utils';
import { scrollToInvalid, useValidationState } from '../../../shared/validation';
import { DocTitle, scrollToPageHeader } from '../../../shared/doc';

const formSchema = z.object({
    name: z
        .string()
        .min(1)
        .max(255)
        .regex(/^[a-zA-Z0-9-]*$/, {
            message:
                'Dataset name must not be empty, can contain only alphanumeric characters, and be between 1 and 255 characters',
        }),
    description: z
        .string()
        .regex(/^[\w\-\s'.]+$/, {
            message: 'Dataset description can contain only alphanumeric characters.',
        })
        .max(254),
    type: z.string({ invalid_type_error: 'A type must be selected.' }),
});

export function DatasetCreate () {
    const [dataset] = useState(defaultDataset as IDataset);
    const [datasetFileList, setDatasetFileList] = useState([] as IDatasetFile[]);
    const { projectName } = useParams();
    const auth = useAuth();
    const username = auth.user!.profile.preferred_username;

    scrollToPageHeader();
    DocTitle('Create Dataset');

    const dispatch = useAppDispatch();
    const navigate = useNavigate();
    const basePath = projectName ? `/project/${projectName}` : '/personal';
    const notificationService = NotificationService(dispatch);

    const { updateForm, touchFieldHandler, setState, state } = useValidationState(formSchema, {
        validateAll: false,
        needsValidation: false,
        datasets: {},
        form: {
            name: '',
            description: '',
            type: null,
        },
        touched: {
            inputDataConfig: [],
        },
        formErrors: {} as any,
        formValid: false,
        formSubmitting: false,
    });

    useEffect(() => {
        dispatch(
            setBreadcrumbs([
                getBase(projectName),
                { text: 'Datasets', href: `#${basePath}/dataset` },
                { text: 'Create dataset', href: `#${basePath}/dataset/create` },
            ])
        );

        scrollToPageHeader('h1', 'dataset');
    }, [dispatch, basePath, projectName]);

    async function handleSubmit () {
        if (state.formValid) {
            setState({type: 'updateState', payload: { formSubmitting: true } });

            // create new dataset from state.form
            const newDataset = createDatasetFromForm(state.form, datasetFileList);
            newDataset.scope = determineScope(newDataset.type, projectName, username!);
            const response = await createDataset(newDataset).catch(() => {
                // if dataset exists display message to user
                notificationService.generateNotification(
                    `Failed to create dataset, dataset already exists with the name: ${newDataset.name}`,
                    'error'
                );
            });
            if (response?.status === 200) {
                const s3Keys = buildS3Keys(datasetFileList, newDataset, projectName, username!);
                await uploadFiles(s3Keys, newDataset, notificationService, datasetFileList);
                // Need to clear state/reset the form
                navigate(`${basePath}/dataset/${newDataset.scope}/${newDataset.name}`);
            }
            setState({type: 'updateState', payload: { formSubmitting: false } });
        } else {
            scrollToInvalid();
        }
    }

    return (
        <ContentLayout
            header={
                <Header
                    variant='h1'
                    description='A Dataset is a collection of artifacts that contain data to be used in SageMaker. This can can include Training, HPO, and Batch Transform jobs.'
                >
                    Create dataset
                </Header>
            }
        >
            <Form
                actions={
                    <SpaceBetween direction='horizontal' size='xl'>
                        <Button
                            formAction='none'
                            variant='link'
                            onClick={() =>
                                navigate(`${basePath}/dataset`, {
                                    state: { prevPath: window.location.hash },
                                })
                            }
                        >
                            Cancel
                        </Button>
                        <Popover
                            dismissAriaLabel='Close'
                            triggerType='custom'
                            content={
                                state.formValid ? (
                                    <StatusIndicator type='info'>
                                        Do not navigate away while dataset is being created.
                                    </StatusIndicator>
                                ) : (
                                    <StatusIndicator type='error'>
                                        All sections must be filled out.
                                    </StatusIndicator>
                                )
                            }
                        >
                            <Button
                                data-cy='dataset-submit-button'
                                loading={state.formSubmitting}
                                variant='primary'
                                onClick={() => {
                                    setState({ type: 'validateAll' });
                                    handleSubmit();
                                }}
                                disabled={state.formSubmitting}
                            >
                                Create dataset
                            </Button>
                        </Popover>
                    </SpaceBetween>
                }
            >
                <Container>
                    <SpaceBetween direction='vertical' size='s'>
                        <FormField
                            description='Maximum of 255 characters. Must be unique to the type that you choose. The dataset name must be unique to the scope (Global/Private/Project).'
                            errorText={state.formErrors.name}
                            label='Dataset name'
                        >
                            <Input
                                data-cy='dataset-name-input'
                                value={state.form.name}
                                onChange={(event) => {
                                    updateForm({ name: event.detail.value });
                                }}
                                onBlur={touchFieldHandler('name')}
                            />
                        </FormField>
                        <FormField
                            description='Description is required.'
                            errorText={state.formErrors.description}
                            label='Description'
                        >
                            <Textarea
                                data-cy='dataset-description-textarea'
                                value={state.form.description}
                                onChange={(event) => {
                                    updateForm({ description: event.detail.value });
                                }}
                                onBlur={touchFieldHandler('description')}
                            />
                        </FormField>
                        <FormField
                            description={
                                window.env.MANAGE_IAM_ROLES ? (
                                    'Global datasets are accessible from any project, project datasets ' +
                                    'are accessible only to the project they were created in, and ' +
                                    'private datasets are accessible to the user that created them.'
                                ) : (
                                    <Alert
                                        statusIconAriaLabel='Info'
                                        header='Dataset Access Limitations'
                                    >
                                        Dataset Type is used as a convention to organize data within
                                        S3 but <strong>does not</strong> prevent other ${window.env.APPLICATION_NAME} users
                                        from accessing data. Making a &quot;Private&quot; or
                                        &quot;Project&quot; dataset is merely a convention and does
                                        not enforce access control.
                                    </Alert>
                                )
                            }
                            errorText={state.formErrors.type}
                            label='Dataset Type'
                        >
                            <Select
                                data-cy='dataset-type-select'
                                selectedOption={{
                                    label: initCap(state.form.type || ''),
                                    value: state.form.type,
                                }}
                                onChange={({ detail }) => {
                                    updateForm({
                                        type: detail.selectedOption.value! as DatasetType,
                                    });
                                }}
                                options={
                                    projectName!
                                        ? enumToOptions(DatasetType, true)
                                        : [
                                            { label: 'Global', value: 'global' },
                                            { label: 'Private', value: 'private' },
                                        ]
                                }
                                onBlur={touchFieldHandler('type')}
                            />
                        </FormField>
                    </SpaceBetween>
                </Container>
                <br />
                <Container>
                    <ManageFiles
                        dataset={dataset}
                        filesOverride={datasetFileList}
                        setFilesOverride={setDatasetFileList}
                        readOnly={false}
                    />
                </Container>
            </Form>
        </ContentLayout>
    );
}

export default DatasetCreate;
