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

import React, { RefObject, useEffect, useRef } from 'react';
import { defaultColumns, visibleColumns, visibleContentPreference } from './model.columns';
import { getProjectModels, loadingModelsList, modelsList, clearModelsList } from './model.reducer';
import { useAppDispatch, useAppSelector } from '../../config/store';
import Table from '../../modules/table';
import { setBreadcrumbs } from '../../shared/layout/navigation/navigation.reducer';
import ModelActions from './model.actions';
import { useParams } from 'react-router-dom';
import { getBase } from '../../shared/util/breadcrumb-utils';
import { DocTitle, scrollToPageHeader } from '../../../src/shared/doc';
import { focusOnCreateButton } from '../../shared/util/url-utils';
import { ModelResourceMetadata } from '../../shared/model/resource-metadata.model';

export const Model = () => {
    const { projectName } = useParams();
    const modelList: ModelResourceMetadata[] = useAppSelector(modelsList);
    const loadingModels = useAppSelector(loadingModelsList);
    const createModelRef: RefObject<HTMLInputElement> = useRef(null);

    const dispatch = useAppDispatch();

    DocTitle(projectName!.concat(' Models'));

    useEffect(() => {
        dispatch(
            setBreadcrumbs([
                getBase(projectName),
                { text: 'Models', href: `#/project/${projectName}/model` },
            ])
        );
        if (focusOnCreateButton()) {
            createModelRef.current?.focus();
        } else {
            scrollToPageHeader('h1', 'Models');
        }
    }, [dispatch, projectName]);

    return (
        <Table
            tableName='Model'
            tableType='single'
            trackBy='resourceId'
            actions={ModelActions}
            focusProps={{ createModelRef: createModelRef }}
            allItems={modelList}
            columnDefinitions={defaultColumns}
            visibleColumns={visibleColumns}
            visibleContentPreference={visibleContentPreference}
            loadingItems={loadingModels}
            serverFetch={getProjectModels}
            storeClear={clearModelsList}
        />
    );
};

export default Model;
