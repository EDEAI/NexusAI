/*
 * @LastEditors: biz
 */
import { getUploadUrl } from '@/api/createkb';
import { getDealtWithInfo, updateDealtWith } from '@/api/workflow';
import { Prompt } from '@/py2js/prompt';
import { ArrayVariable, createVariableFromObject, Variable } from '@/py2js/variables';
import useUserStore from '@/store/user';
import useSocketStore from '@/store/websocket';
import { CheckOutlined, CloseOutlined, InboxOutlined } from '@ant-design/icons';
import {
    ProCard,
    ProForm,
    ProFormDependency,
    ProFormSelect,
    ProFormTextArea,
    ProFormUploadDragger,
    ProFormUploadDraggerProps,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useRequest, useUpdateEffect } from 'ahooks';
import { Alert, Button, List, message, Typography } from 'antd';
import _, { set } from 'lodash';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import { NOT_SHOW_INPUT_RESULT_NODE, UPLOAD_FILES_KEY } from '../../config';
import useStore from '../../store';
import { BlockEnum } from '../../types';
import CodeEditor from '../Editor/CodeEditor';

import useSaveWorkFlow from '../../saveWorkFlow';
const { Text } = Typography;
const { ErrorBoundary } = Alert;
export default memo((props: any) => {
    const intl = useIntl();
    const [show, setShow] = useState(false);
    const dealtWithData = useUserStore(state => state.dealtWithData);
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setPrevConfirmDealtWith= useUserStore(state => state.setPrevConfirmDealtWith);
    const setSubmitPromptId = useUserStore(state => state.setSubmitPromptId);
    const setFlowMessage = useSocketStore(state => state.setFlowMessage);
    const getNeedHumanConfirmMessage = useSocketStore(state => state.getNeedHumanConfirmMessage);
    const flowMessage = useSocketStore(state => state.flowMessage);
    const [dealtWithInfo, setDealtWithInfo] = useState<any>(null);
    const [execId, setExecId] = useState<string>('');
    const [buttonLoading, setButtonLoading] = useState(false);

    const { loading, runAsync } = useRequest(getDealtWithInfo, {
        manual: true,
    });
    useEffect(() => {
        setShow(!!dealtWithData);
        // setPrevConfirmDealtWith(null)
        const id = dealtWithData?.exec_id;
        console.log(dealtWithData, id);
        setExecId(id);
        if (id) {
            getHumanMessage(id);
        }
        return () => {
            setShow(false);
        };
    }, [dealtWithData]);
    // useWhyDidYouUpdate('dealtWithData', dealtWithData);

    const getHumanMessage = id => {
        if (loading) return;
        runAsync(id).then(res => {
            console.log(res);

            if (res.data) {
                setDealtWithInfo(res.data);
                setButtonLoading(false);
            }
        });
    };

    useUpdateEffect(() => {
        console.log(flowMessage, execId);
        const newHumanMessage = flowMessage.find(
            item => item?.data?.node_exec_data?.node_exec_id == execId,
        );
        console.log(newHumanMessage);

        if (newHumanMessage) {
            getHumanMessage(execId);
        }
    }, [flowMessage]);

    const submitPrompt = e => {
        setButtonLoading(true);
        updateDealtWith(execId, {
            correct_prompt: new Prompt('', e.prompt, ''),
            operation: 1,
            outputs: dealtWithInfo?.outputs || null,
        }).then(res => {
            if (res.code == 0) {
                setShow(false);
                props?.onSubmit?.(execId);
                setSubmitPromptId(execId);
                setPrevConfirmDealtWith(dealtWithData)
                setDealtWithData(null);
            }
        });
    };
    const delHumanMessage = id => {
        const newFlowMessage = flowMessage.filter(
            item =>
                !(
                    item?.data?.node_exec_data?.node_exec_id == id &&
                    item?.type == 'workflow_need_human_confirm'
                ),
        );
        setFlowMessage(newFlowMessage);
    };

    const confirmDealtWith = () => {
        updateDealtWith(execId, {
            operation: 0,
            outputs: dealtWithInfo?.outputs || null,
        }).then(res => {
            if (res.code == 0) {
                setShow(false);
                setSubmitPromptId(execId);
                delHumanMessage(execId);
                setPrevConfirmDealtWith(dealtWithData)
                setDealtWithData(null);
            }
        });
    };

    const LLMContent = useCallback(() => {
        const nodeType = dealtWithInfo?.node_type;
        console.log(dealtWithInfo, nodeType);

        return (
            <>
                <div className="flex flex-col gap-2 mt-4">
                    {nodeType != BlockEnum.LLM && (
                        <div className="h-80">
                            <CodeEditor
                                language="python3"
                                value={dealtWithInfo?.inputs}
                                readOnly
                                isJSONStringifyBeauty
                                onChange={() => {}}
                                title={`input`}
                            ></CodeEditor>
                        </div>
                    )}
                    {dealtWithInfo?.correct_llm_history?.length > 0 && (
                        <List
                            header={
                                <Typography.Title level={5}>
                                    {intl.formatMessage({
                                        id: 'workflow.historyPrompt',
                                        defaultMessage: 'prompt',
                                    })}
                                </Typography.Title>
                            }
                            dataSource={dealtWithInfo?.correct_llm_history}
                            renderItem={item => (
                                <List.Item>{item?.correct_prompt?.user?.value}</List.Item>
                            )}
                        ></List>
                    )}

                    <div className="h-80">
                        <CodeEditor
                            language="python3"
                            value={dealtWithInfo?.outputs}
                            readOnly
                            isJSONStringifyBeauty
                            onChange={() => {}}
                            title={`output`}
                        ></CodeEditor>
                    </div>
                </div>
                <ProForm
                    submitter={{
                        resetButtonProps: false,
                        submitButtonProps: {
                            className: 'w-full',
                            // type:'default'
                        },
                        searchConfig: {
                            submitText: intl.formatMessage({ id: 'workflow.xz' }),
                        },
                    }}
                    loading={buttonLoading}
                    onFinish={submitPrompt}
                >
                    <div className="flex ">
                        <div className="flex-1 pt-2 border-stone-300 border rounded-md my-2">
                            <div className="px-2 flex justify-between cursor-default">
                                <div>
                                    <div className="text-sm text-gray-500 font-bold pb-1">
                                        Prompt
                                    </div>
                                </div>
                                <div></div>
                            </div>
                            <div className=" pb-6">
                                <ProFormTextArea
                                    formItemProps={{
                                        className: 'mb-0',
                                    }}
                                    name="prompt"
                                    fieldProps={{
                                        variant: 'borderless',
                                        placeholder: intl.formatMessage({
                                            id: 'workflow.requireInputPrompt',
                                        }),
                                        autoSize: { minRows: 2, maxRows: 40 },
                                        count: {
                                            show: ({ value, count, maxLength }) => {
                                                return (
                                                    <div className="pr-2 text-blue-400">
                                                        {count}
                                                    </div>
                                                );
                                            },
                                        },
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                </ProForm>
            </>
        );
    }, [dealtWithInfo]);

    const HumanContent = useCallback(() => {
        const inputVar = dealtWithInfo?.node_graph?.data?.input;
        const inputs = inputVar?.properties;
        const requires_upload = dealtWithInfo?.node_graph?.data?.requires_upload;
        const import_to_knowledge_base =
            dealtWithInfo?.node_graph?.data?.import_to_knowledge_base?.input;
        console.log('requires_upload', dealtWithInfo, requires_upload);

        const datasetData = useStore(state => state.datasetData);

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
        const inputsArr = Object.values(inputs);
        const submitHuman = e => {
            console.log(e);
            const input = createVariableFromObject(inputVar);
            if (inputsArr.length > 0) {
                const variables = Object.entries(e).filter(([key, value]) =>
                    key.startsWith('variables.'),
                );
                variables.forEach(([key, value]) => {
                    input.properties[key.replace('variables.', '')].value = value;
                });
            }
            const freeFile = new ArrayVariable(UPLOAD_FILES_KEY, 'array[number]');
            e.file &&
                e.file.forEach(x => {
                    const fileVariable = new Variable(
                        x.uid,
                        'number',
                        x?.response?.data?.file_id || 0,
                    );
                    freeFile.addValue(fileVariable);
                });
            input.addProperty(UPLOAD_FILES_KEY, freeFile);
            console.log(input, freeFile);

            const knowledge_base_mapping = dealtWithInfo?.node_graph?.data
                ?.knowledge_base_mapping || {
                input: {},
                output: {},
            };
            Object.entries(e).forEach(([key, value]) => {
                if (key.startsWith('dataset.')) {
                    if (!knowledge_base_mapping.input[UPLOAD_FILES_KEY]) {
                        knowledge_base_mapping.input[UPLOAD_FILES_KEY] = {};
                    }
                    knowledge_base_mapping.input[UPLOAD_FILES_KEY][key.replace('dataset.', '')] =
                        value;
                }
            });
            console.log(knowledge_base_mapping);
            updateDealtWith(execId, {
                operation: 0,
                inputs: input,
                outputs: null,
                correct_prompt: null,
                knowledge_base_mapping,
            }).then(res => {
                if (res.code == 0) {
                    setShow(false);
                    setPrevConfirmDealtWith(dealtWithData)
                    setDealtWithData(null);
                    setSubmitPromptId(execId);
                    delHumanMessage(execId);
                }
            });
        };

        const uploadProps: ProFormUploadDraggerProps = {
            icon: <InboxOutlined></InboxOutlined>,
            title: intl.formatMessage({
                id: 'workflow.uploadFileText',
                defaultMessage: '，',
            }),
            description: intl.formatMessage({ id: 'workflow.uploadFileDes' }),

            accept: '.txt,.md,.pdf,.html,.xlsx,.xls,.docx,.csv',

            fieldProps: {
                listType: 'picture',
                name: 'file',
                multiple: true,
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                },
                action: getUploadUrl,
                beforeUpload(file) {
                    // const allowedTypes = [
                    //     'text/plain', // TXT
                    //     'text/markdown', // MARKDOWN
                    //     'application/pdf', // PDF
                    //     'text/html', // HTML
                    //     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // XLSX
                    //     'application/vnd.ms-excel', // XLS
                    //     'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // DOCX
                    //     'text/csv', // CSV
                    // ];

                    // // Check if the file type is allowed
                    // const isAllowedType = allowedTypes.includes(file.type);
                    // if (!isAllowedType) {
                    //     message.error('');
                    // }

                    // Check if the file size is less than 15MB
                    const isLt15M = file.size / 1024 / 1024 < 15;
                    if (!isLt15M) {
                        message.error(intl.formatMessage({ id: 'workflow.uploadFileErrorText' }));
                    }

                    return isLt15M;
                },
            },
        };
        return (
            <div className="mt-4">
                <ProForm
                    // layout="horizontal"
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
                    onFinish={submitHuman}
                >
                    {inputsArr.map(item => {
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
                    {requires_upload && (
                        <ProFormUploadDragger name="file" {...uploadProps}></ProFormUploadDragger>
                    )}
                    <ProFormDependency name={['file']}>
                        {({ file }) =>
                            (import_to_knowledge_base &&
                                file?.length > 0 &&
                                file?.map(x => {
                                    return (
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
                                    );
                                })) ||
                            null
                        }
                    </ProFormDependency>
                </ProForm>
            </div>
        );
    }, [dealtWithInfo]);
    const flattenObjectProperties = obj => {
        if (obj.type !== 'object' || !obj.properties) {
            return [obj];
        }

        const result = [];

        const flatten = (item, parentKey = '') => {
            _.forOwn(item, (value, key) => {
                const newKey = parentKey ? `${parentKey}.${key}` : key;
                if (value.type === 'object' && value.properties) {
                    flatten(value.properties, newKey);
                } else {
                    result.push({ ...value, name: newKey });
                }
            });
        };

        flatten(obj.properties);
        return result;
    };
    const arrayToObject = arr => {
        return arr.reduce((acc, item) => {
            acc[item.name] = item.value;
            return acc;
        }, {});
    };
    const CustomContent = useCallback(() => {
        console.log(dealtWithInfo);
        const input = dealtWithInfo?.inputs;
        const formRef = useRef(null);
        const [outputs, setOutputs] = useState([]);
        const [outputsValue, setOutputsValue] = useState({});
        const [messageApi, contextHolder] = message.useMessage();
        useMount(() => {
            if (dealtWithInfo?.outputs) {
                console.log(input, flattenObjectProperties(dealtWithInfo?.outputs));
                setOutputs(flattenObjectProperties(dealtWithInfo?.outputs));
                setOutputsValue(JSON.stringify(flattenObjectProperties(dealtWithInfo?.outputs)));

                // setTimeout(() => {
                //     console.log(arrayToObject(flattenObjectProperties(dealtWithInfo?.outputs)));
                //     formRef?.current?.setFieldsValue(
                //         arrayToObject(flattenObjectProperties(dealtWithInfo?.outputs)),
                //     );
                // }, 1000);
            }
        });
        const submitOutputs = () => {
            let outputs = {};
            try {
                outputs = JSON.parse(outputsValue);
                console.log(outputs, outputs[0]);
                updateDealtWith(execId, {
                    outputs: _.isArray(outputs) ? outputs[0] : outputs,
                }).then(res => {
                    if (res.code == 0) {
                        messageApi.success(
                            intl.formatMessage({
                                id: 'workflow.checkSc',
                                defaultMessage: '',
                            }),
                        );
                        setShow(false);
                        setSubmitPromptId(execId);
                        delHumanMessage(execId);
                        setPrevConfirmDealtWith(dealtWithData)
                        setDealtWithData(null);
                    }
                });
            } catch (error) {
                console.log(error);
                messageApi.error(
                    intl.formatMessage({
                        id: 'workflow.checkOutputMessageError',
                        defaultMessage: ',',
                    }),
                );
            }
        };
        return (
            <div>
                {contextHolder}
                <div className="flex flex-col gap-2 pt-4">
                    {!NOT_SHOW_INPUT_RESULT_NODE.includes(dealtWithInfo?.node_type) && (
                        <div>
                            <Typography.Title level={5}>Inputs</Typography.Title>
                            <div className="h-80">
                                <CodeEditor
                                    language="python3"
                                    value={dealtWithInfo?.inputs}
                                    readOnly
                                    isJSONStringifyBeauty
                                    onChange={value => {
                                        setOutputsValue(value);
                                    }}
                                    // title={`input`}
                                ></CodeEditor>
                            </div>
                        </div>
                    )}
                    <Typography.Title level={5}>
                        Outputs(
                        {intl.formatMessage({ id: 'workflow.toEdit', defaultMessage: '' })})
                    </Typography.Title>
                    <div className="h-80">
                        <CodeEditor
                            language="python3"
                            value={dealtWithInfo?.outputs}
                            isJSONStringifyBeauty
                            onChange={value => {
                                setOutputsValue(value);
                            }}
                            // title={`output`}
                        ></CodeEditor>
                        {/* <ProForm
                            formRef={formRef}
                            submitter={{
                                searchConfig: {
                                    submitText: '',
                                },
                                submitButtonProps: {
                                    className: 'w-full',
                                },
                                resetButtonProps: false,
                            }}
                        >
                            {outputs.map((item) => {
                                return (
                                    <ProFormTextArea
                                        key={item.name}
                                        label={item.name}
                                        name={`${item.name}`}
                                        required={true}
                                        rules={[{ required: true, message: '' }]}
                                    ></ProFormTextArea>
                                );
                            })}
                        </ProForm> */}
                    </div>
                    <Button type="primary" onClick={submitOutputs} className="w-full mt-4">
                        {intl.formatMessage({ id: 'workflow.checked', defaultMessage: '' })}
                    </Button>
                    {/* {
                    inputs?.map((item)=>{
                        return (
                            <div className='border rounded-md p-2 '>
                                <div>{item.name}</div>
                                <div>{item.value}</div>
                            </div>
                        )
                    })
                 } */}
                </div>
            </div>
        );
    }, [dealtWithInfo]);
    const saveWorkFlow = useSaveWorkFlow();
    const [submitErrorLoading, setSubmitErrorLoading] = useState(false);
    const RenderContent = useCallback(() => {
        const nodeType = dealtWithInfo?.node_type;

        if (dealtWithInfo?.status == 4) {
            return (
                <div>
                    <Alert
                        message={`${dealtWithInfo?.error}`}
                        type="error"
                        className="mt-4"
                    ></Alert>
                    <Button
                        type="primary"
                        variant="solid"
                        className="w-full mt-4"
                        loading={submitErrorLoading}
                        onClick={async e => {
                            setSubmitErrorLoading(true);
                            await saveWorkFlow();
                            updateDealtWith(dealtWithInfo.exec_id, {}).then(async res => {
                                if (res.code == 0) {
                                    // message.success('');
                                }
                                delHumanMessage(dealtWithInfo.exec_id);
                                setShow(false);
                                setPrevConfirmDealtWith(dealtWithData)
                                setDealtWithData(null);
                                props?.onSubmit?.(execId);
                                setSubmitPromptId(execId);
                                setSubmitErrorLoading(false);
                            });
                        }}
                    >
                        {intl.formatMessage({
                            id: 'workflow.resetRun',
                            defaultMessage: '',
                        })}
                    </Button>
                </div>
            );
        }
        if (nodeType == BlockEnum.Human) {
            return <HumanContent></HumanContent>;
        } else if (
            nodeType == BlockEnum.LLM ||
            nodeType == BlockEnum.Agent ||
            nodeType == BlockEnum.TaskGeneration
        ) {
            return <LLMContent></LLMContent>;
        }
        return <CustomContent></CustomContent>;
    }, [dealtWithInfo]);
    const ConfirmDealtWithBtn = () => {
        const nodeType = dealtWithInfo?.node_type;
        if (
            nodeType == BlockEnum.LLM ||
            nodeType == BlockEnum.Agent ||
            nodeType == BlockEnum.TaskGeneration
        ) {
            return (
                <Button
                    type="text"
                    onClick={confirmDealtWith}
                    className="text-green-500"
                    disabled={buttonLoading}
                    icon={<CheckOutlined></CheckOutlined>}
                >
                    {intl.formatMessage({
                        id: 'workflow.checkBackLogs',
                        defaultMessage: '',
                    })}
                </Button>
            );
        }
        return null;
    };
    return show ? (
        <ProCard
            className="w-[400px] border border-blue-300 fixed  top-[65px] right-2 z-20 run_workflow"
            style={{ height: 'calc(100vh - 10px - 75px)' }}
            extra={
                <div className="flex gap-2">
                    {<ConfirmDealtWithBtn></ConfirmDealtWithBtn>}
                    <Button
                        onClick={() => {
                            setShow(false);
                            setDealtWithData(null);
                        }}
                        type="text"
                        icon={<CloseOutlined></CloseOutlined>}
                    ></Button>
                </div>
            }
            title={
                <Typography.Title level={5}>
                    {intl.formatMessage({ id: 'workflow.backlogs', defaultMessage: '' })}
                </Typography.Title>
            }
            bodyStyle={{
                overflowY: 'auto',
                marginTop: '20px',
                boxSizing: 'border-box',
              height:'100%'
            }}
        >
            <div>
                <div>
                    <Typography.Title level={5}>
                        {dealtWithInfo?.node_graph?.data?.title}
                    </Typography.Title>
                </div>
                <div>
                    <Typography.Text>{dealtWithInfo?.node_graph?.data?.desc}</Typography.Text>
                </div>
                {RenderContent()}

            </div>
        </ProCard>
    ) : null;
});
