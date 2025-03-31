import { getUploadUrl } from '@/api/createkb';
import { UPLOAD_FILES_KEY } from '@/components/WorkFlow/config';
import useStore from '@/components/WorkFlow/store';
import { ArrayVariable, createVariableFromObject, Variable } from '@/py2js/variables';
import { InboxOutlined } from '@ant-design/icons';
import {
    ProForm,
    ProFormDependency,
    ProFormSelect,
    ProFormTextArea,
    ProFormUploadDragger,
    ProFormUploadDraggerProps,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { message } from 'antd';
import { useCallback } from 'react';
import { ContentProps } from './types';
import { UploadDragger } from '../../Form/Upload';
import _ from 'lodash';

interface InputItem {
    name: string;
    display_name: string;
    required: boolean;
    sort_order?: number;
    [key: string]: any;
}

const HumanContent = ({ dealtWithInfo, onUpdate, execId }: ContentProps) => {
    const intl = useIntl();
    const inputVar = dealtWithInfo?.node_graph?.data?.input;
    const inputs = inputVar?.properties;
    const requires_upload = dealtWithInfo?.node_graph?.data?.requires_upload;
    const import_to_knowledge_base =
        dealtWithInfo?.node_graph?.data?.import_to_knowledge_base?.input;
    const datasetData = useStore(state => state.datasetData);

    
    const getInitialValues = () => {
        const initialValues: Record<string, any> = {};
        
        if (inputs) {
            const inputItems = Object.values(inputs) as InputItem[];
            inputItems.forEach(item => {
               
                if (item.default_value !== undefined) {
                    initialValues[`variables.${item.name}`] = item.default_value;
                } else if (item.type === 'number') {
                    initialValues[`variables.${item.name}`] = 0;
                } else if (item.type === 'string') {
                    initialValues[`variables.${item.name}`] = '';
                } else if (item.type === 'file') {
                    initialValues[`variables.${item.name}`] = [];
                }
            });
        }
        
        return initialValues;
    };

    if (!inputs) {
        return (
            <>
                {intl.formatMessage({
                    id: 'workflow.requireInputPrompt',
                    defaultMessage: '',
                })}
            </>
        );
    }

    const inputsArr = Object.values(inputs) as InputItem[];

    const handleSubmit = useCallback(
        (values: any) => {
            const input = createVariableFromObject(inputVar);
            if (inputsArr.length > 0) {
                const variables = Object.entries(values).filter(([key]) =>
                    key.startsWith('variables.'),
                );
                variables.forEach(([key, value]) => {
                    if (input.properties) {
                        if(_.isObject(value)){
                          value=value[0]?.response?.data?.file_id||''
                        }
                        input.properties[key.replace('variables.', '')].value = value;
                    }
                });
            }

            // const freeFile = new ArrayVariable(UPLOAD_FILES_KEY, 'array[number]');
            // values.file &&
            //     values.file.forEach((x: any) => {
            //         const fileVariable = new Variable(
            //             x.uid,
            //             'number',
            //             x?.response?.data?.file_id || 0,
            //         );
            //         freeFile.addValue(fileVariable);
            //     });
            // input.addProperty(UPLOAD_FILES_KEY, freeFile);

            const knowledge_base_mapping = dealtWithInfo?.node_graph?.data
                ?.knowledge_base_mapping || {
                input: {},
                output: {},
            };

            Object.entries(values).forEach(([key, value]) => {
                if (key.startsWith('dataset.')) {
                    if (!knowledge_base_mapping.input[UPLOAD_FILES_KEY]) {
                        knowledge_base_mapping.input[UPLOAD_FILES_KEY] = {};
                    }
                    knowledge_base_mapping.input[UPLOAD_FILES_KEY][key.replace('dataset.', '')] =
                        value;
                }
            });

            return onUpdate(execId, {
                operation: 0,
                inputs: input,
                outputs: null,
                correct_prompt: null,
                knowledge_base_mapping,
            });
        },
        [dealtWithInfo, execId, inputVar, inputsArr, onUpdate],
    );


    return (
        <div className="mt-4">
            <ProForm
                submitter={{
                    resetButtonProps: false,
                    submitButtonProps: {
                        className: 'w-full',
                    },
                    searchConfig: {
                        submitText: intl.formatMessage({
                            id: 'workflow.checked',
                            defaultMessage: '',
                        }),
                    },
                }}
                onFinish={handleSubmit}
                initialValues={getInitialValues()}
            >
                {inputsArr
                    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
                    .map(item => {
                        if (item.type === 'file') {
                            return (
                                <UploadDragger
                                    label={item.display_name}
                                    required={item.required}
                                    name={`variables.${item.name}`}
                                    multiple={false}
                                />
                            );
                        }
                        return (
                            <ProFormTextArea
                                key={item.name}
                                label={item.display_name}
                                name={`variables.${item.name}`}
                                required={item.required}
                                rules={[
                                    {
                                        required: item.required,
                                        message: intl.formatMessage({ id: 'workflow.toInput' }),
                                    },
                                ]}
                            />
                        );
                    })}

                {/* {requires_upload && (
                    <ProFormUploadDragger name="file" {...uploadProps}></ProFormUploadDragger>
                )} */}

                <ProFormDependency name={['file']}>
                    {({ file }) =>
                        (import_to_knowledge_base &&
                            file?.length > 0 &&
                            file?.map(x => (
                                <ProFormSelect
                                    key={x.uid}
                                    label={x.name}
                                    name={`dataset.${x.uid}`}
                                    options={datasetData?.list || []}
                                    required={true}
                                    rules={[
                                        {
                                            required: true,
                                            message: intl.formatMessage({
                                                id: 'workflow.select_to_knowledge_base',
                                            }),
                                        },
                                    ]}
                                ></ProFormSelect>
                            ))) ||
                        null
                    }
                </ProFormDependency>
            </ProForm>
        </div>
    );
};

export default HumanContent;
