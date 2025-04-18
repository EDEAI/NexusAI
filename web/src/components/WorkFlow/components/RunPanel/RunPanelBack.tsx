/*
 * @LastEditors: biz
 */
import { getUploadUrl } from '@/api/createkb';
import { runWorkFlow, updateDealtWith } from '@/api/workflow';
import { ArrayVariable, ObjectVariable, Variable } from '@/py2js/variables.js';
import useSocketStore from '@/store/websocket';
import {
    CheckCircleOutlined,
    CloseOutlined,
    DownloadOutlined,
    LoadingOutlined,
    SyncOutlined,
} from '@ant-design/icons';
import {
    ProCard,
    ProForm,
    ProFormDateTimePicker,
    ProFormDependency,
    ProFormDigit,
    ProFormSelect,
    ProFormText,
    ProFormTextArea,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import { Alert, Button, Collapse, Divider, message, Tag, Tooltip, Typography } from 'antd';
import _ from 'lodash';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import CodeEditor from '../Editor/CodeEditor';
import { TextareaRunName } from '../Form/Input';
import { UploadDragger } from '../Form/Upload';
import {
    NOT_SHOW_INPUT_RESULT_NODE,
    NOT_SHOW_OUTPUT_RESULT_NODE,
    UPLOAD_FILES_KEY,
} from '../../config';
import useSaveWorkFlow from '../../saveWorkFlow';
import useStore from '../../store';
import { BlockEnum } from '../../types';
import FileDownloadList from '@/components/common/FileDownloadList';
const { Text } = Typography;
const { ErrorBoundary } = Alert;
export default memo(() => {
    const intl = useIntl();
    const runPanelShow = useStore(state => state.runPanelShow);
    const setRunPanelShow = useStore(state => state.setRunPanelShow);
    const setDealtWithData = useSocketStore(state => state.setDealtWithData);
    const setFlowMessage = useSocketStore(state => state.setFlowMessage);
    const flowMessage = useSocketStore(state => state.flowMessage);
    const [hasResult, setHasResult] = useState(false);
    const [runResultInfo, setRunResultInfo] = useState(null);
    // const getDebugMessage = useSocketStore(state => state.getDebugMessage);
    const [runList, setRunList] = useState([]);
    const [tabKey, setTabKey] = useState('1');
    const [endRun, setEndRun] = useState(null);
    const [loading, setLoading] = useState(true);

    const runResult = e => {
        setRunList([]);
        setRunResultInfo(e.data);
        setHasResult(true);
        setTabKey('4');
    };

    useUpdateEffect(() => {
        // setLoading(false);

        if (runResultInfo?.app_run_id) {
            const humanList = flowMessage.filter(item => {
                return (
                    item.type == 'workflow_need_human_confirm' &&
                    item.data.app_run_id == runResultInfo?.app_run_id
                );
            });
            let list = flowMessage
                .filter(item => {
                    return (
                        item.type == 'workflow_run_debug' &&
                        item.data.app_run_id == runResultInfo?.app_run_id
                    );
                })
                .map(item => {
                    return {
                        ...item,
                        human: humanList.some(x => {
                            return (
                                x.data.node_exec_data.node_exec_id ==
                                    item.data.node_exec_data.node_exec_id ||
                                x.data.node_exec_data.first_task_exec_id ==
                                    item.data.node_exec_data.node_exec_id
                            );
                        }),
                    };
                });
            let runList = list.filter(x => {
                if (x.data?.node_exec_data?.parent_exec_id) {
                    const index = list.findIndex(
                        y =>
                            y.data.node_exec_data.node_exec_id ==
                            x.data.node_exec_data.parent_exec_id,
                    );
                    if (index > -1) {
                        if (!list[index]['children']) {
                            list[index]['children'] = [];
                        }
                        list[index]['children'].push(x);
                    }
                    return false;
                }

                return true;
            });

            const mergeData = list => {
                return list.filter((x, i) => {
                    const findMeIndex = list.findIndex(
                        y =>
                            y.data.node_exec_data.node_exec_id ==
                                x.data.node_exec_data.first_task_exec_id ||
                            y.data.node_exec_data.node_exec_id ==
                                x.data.node_exec_data.node_exec_id,
                    );
                    if (list[i]?.['children']?.length) {
                        list[i]['children'] = mergeData(list[i]['children']);
                    }
                    if (findMeIndex > -1 && findMeIndex < i) {
                        list[findMeIndex].data = x.data;
                        return false;
                    }
                    return true;
                });
            };

            runList = mergeData(runList);

            // const list = getDebugMessage({
            //     app_run_id: runResultInfo.app_run_id,
            // });
            runList = runList.filter((x, i) => {
                // if (x.data.node_exec_data?.first_task_exec_id != 0) {
                const findMeIndex = runList.findIndex(
                    y =>
                        y.data.node_exec_data.node_exec_id ==
                            x.data.node_exec_data.first_task_exec_id ||
                        y.data.node_exec_data.node_exec_id == x.data.node_exec_data.node_exec_id,
                );
                if (runList[i]?.['children']?.length) {
                }
                if (findMeIndex > -1 && findMeIndex < i) {
                    runList[findMeIndex].data = x.data;
                    return false;
                }
                // }

                return true;
            });
            console.log(_.cloneDeep(runList));

            const endRun = runList.find(x => x?.data?.status == 2);
            if (endRun) {
                setEndRun(runList[runList.length - 1]);
                console.log('endRun');
            }

            setRunList(runList);
        }
    }, [flowMessage]);

    const ResultContent = memo(() => {
        return (
            <>
                <Alert
                    message={JSON.stringify(endRun?.data?.node_exec_data?.outputs || {})}
                    type="success"
                ></Alert>
            </>
        );
    });

    const TrackContent = memo(props => {
        return (
            <div className="grid gap-2">
                {props?.runList?.map((item, index) => {
                    const nodeInfo = item?.data?.node_exec_data;
                    const NodeChildren = useCallback(() => {
                        if (!nodeInfo) return null;

                        if (nodeInfo.node_type == BlockEnum.Human) {
                            if (item.human) {
                                return (
                                    <div>{intl.formatMessage({ id: 'workflow.toBackLogs' })}</div>
                                );
                            }
                            return (
                                <Alert
                                    message={intl.formatMessage({
                                        id: 'workflow.checkedBackLogsMessage',
                                    })}
                                    type="success"
                                    className="text-green-700"
                                ></Alert>
                            );
                        }

                        if (nodeInfo.status == 3 || (nodeInfo.status == 2 && item?.children)) {
                            return (
                                <div className="flex flex-col gap-2">
                                    {nodeInfo?.prompt_data?.length > 0 && (
                                        <div className="h-80">
                                            <CodeEditor
                                                language="python3"
                                                value={nodeInfo?.prompt_data}
                                                // mdValue={nodeInfo?.outputs_md}
                                                readOnly
                                                isJSONStringifyBeauty
                                                onChange={() => {}}
                                                title={intl.formatMessage({
                                                    id: 'workflow.historyPrompt',
                                                })}
                                            ></CodeEditor>
                                        </div>
                                    )}
                                    {nodeInfo.inputs &&
                                        !NOT_SHOW_INPUT_RESULT_NODE.includes(
                                            nodeInfo.node_type,
                                        ) && (
                                            <div className="h-80">
                                                <CodeEditor
                                                    language="python3"
                                                    value={nodeInfo?.inputs}
                                                    readOnly
                                                    isJSONStringifyBeauty
                                                    onChange={() => {}}
                                                    title={intl.formatMessage({
                                                        id: 'workflow.inputs',
                                                    })}
                                                ></CodeEditor>
                                            </div>
                                        )}
                                    {item?.children && (
                                        <TrackContent runList={item?.children}></TrackContent>
                                    )}
                                    {nodeInfo.outputs &&
                                        !NOT_SHOW_OUTPUT_RESULT_NODE.includes(
                                            nodeInfo.node_type,
                                        ) && (
                                            <div className="h-80 w-[314px]">
                                                <CodeEditor
                                                    language="python3"
                                                    value={nodeInfo?.outputs}
                                                    mdValue={nodeInfo?.outputs_md}
                                                    readOnly
                                                    isJSONStringifyBeauty
                                                    onChange={() => {}}
                                                    title={intl.formatMessage({
                                                        id: 'workflow.outputs',
                                                    })}
                                                ></CodeEditor>
                                            </div>
                                        )}

                                    {nodeInfo.file_list && nodeInfo.file_list.length > 0 && (
                                        <FileDownloadList 
                                            files={nodeInfo.file_list} 
                                            title={intl.formatMessage({ id: 'skill.downloadFiles' })}
                                            className="w-[314px]"
                                        />
                                    )}
                                </div>
                            );
                        } else if (nodeInfo.status == 4) {
                            return (
                                <Alert
                                    message={
                                        item?.data?.error ||
                                        intl.formatMessage({ id: 'workflow.nodeRunError' })
                                    }
                                    type="error"
                                    className="text-red-700 break-all"
                                ></Alert>
                            );
                        }

                        return null;
                    }, [item]);

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

                    const NodeExtra = useCallback(() => {
                        const saveWorkFlow = useSaveWorkFlow();
                        if (item.human) {
                            if (nodeInfo?.status == 4) {
                                return (
                                    <Tooltip
                                        title={intl.formatMessage({
                                            id: 'workflow.nodeRunErrorDes',
                                        })}
                                    >
                                        <Tag
                                            icon={<SyncOutlined spin />}
                                            color="error"
                                            className="mr-0"
                                            onClick={async e => {
                                                e.stopPropagation();
                                                await saveWorkFlow();
                                                updateDealtWith(
                                                    item.data.node_exec_data.node_exec_id,
                                                    {},
                                                ).then(async res => {
                                                    if (res.code == 0) {
                                                        delHumanMessage(
                                                            item.data.node_exec_data.node_exec_id,
                                                        );
                                                    }
                                                });
                                            }}
                                        >
                                            {intl.formatMessage({ id: 'workflow.resetRun' })}
                                        </Tag>
                                    </Tooltip>
                                );
                            }
                            return (
                                <Tooltip
                                    title={intl.formatMessage({ id: 'workflow.clickToBackLogs' })}
                                >
                                    <Tag
                                        icon={<SyncOutlined spin />}
                                        color="processing"
                                        className="mr-0"
                                        onClick={e => {
                                            e.stopPropagation();
                                            setDealtWithData(item);
                                        }}
                                    >
                                        {intl.formatMessage({ id: 'workflow.backlogs' })}
                                    </Tag>
                                </Tooltip>
                            );
                        }

                        // if (nodeInfo.node_type == BlockEnum.TaskExecution) {
                        //     return <></>;
                        // }

                        if (nodeInfo.node_type == BlockEnum.Human) {
                            return (
                                <Tag
                                    icon={<CheckCircleOutlined></CheckCircleOutlined>}
                                    color="success"
                                    className="mr-0"
                                >
                                    {intl.formatMessage({ id: 'workflow.checkedBackLogs' })}
                                </Tag>
                            );
                        }
                        if (nodeInfo?.status == 0) {
                        }
                        if (nodeInfo?.status == 1) {
                        }
                        if (nodeInfo?.status == 2) {
                            return <LoadingOutlined />;
                        }
                        if (nodeInfo?.status == 3) {
                            return (
                                <>
                                    <span>
                                        {_.clamp(
                                            item?.data?.node_exec_data?.elapsed_time,
                                            0.00001,
                                            999999,
                                        ).toFixed(5)}
                                        S
                                    </span>
                                    <CheckCircleOutlined className="text-green-400"></CheckCircleOutlined>
                                </>
                            );
                        } else if (nodeInfo?.status == 4) {
                            return <span className="text-red-500">ERROR</span>;
                        }

                        return null;
                    }, [item]);
                    return (
                        <Collapse
                            key={index}
                            defaultActiveKey={
                                item?.children?.length && nodeInfo.status == 2 ? '1' : '2'
                            }
                            items={[
                                {
                                    key: '1',
                                    // extra: <>9.1131ms·0 tokens</>,
                                    label: (
                                        <div className="flex items-center gap-2">
                                            <div className=" bg-gray-300 size-7 rounded-md flex justify-center items-center">
                                                <img
                                                    src={`/icons/${item.data.node_exec_data.node_type}.svg`}
                                                    className="size-6"
                                                    alt=""
                                                />
                                            </div>
                                            <div className="flex-1 shrink-0">
                                                {item.data.node_exec_data.node_name}
                                                <div>{item.finished_time}</div>
                                            </div>
                                            <NodeExtra></NodeExtra>
                                        </div>
                                    ),
                                    children: <NodeChildren></NodeChildren>,
                                },
                            ]}
                        />
                    );
                })}
            </div>
        );
    });

    return runPanelShow ? (
        <ProCard
            className="w-[400px] border user_pro_card_overflow_y border-blue-300 fixed z-10  top-[105px] right-2 "
            style={{ height: 'calc(100vh - 10px - 100px)' }}
            extra={
                <Button
                    type="text"
                    onClick={() => setRunPanelShow(false)}
                    icon={<CloseOutlined></CloseOutlined>}
                ></Button>
            }
            title={
                <Typography.Title level={5}>
                    {intl.formatMessage({ id: 'workflow.run' })}
                </Typography.Title>
            }
            bodyStyle={{
                overflowY: 'auto',
            }}
            tabs={{
                tabPosition: 'top',
                activeKey: tabKey,

                items: [
                    {
                        label: intl.formatMessage({ id: 'workflow.inputs' }),
                        key: '1',
                        children: (
                            <InputContent loading={loading} onRunResult={runResult}></InputContent>
                        ),
                    },
                    // {
                    //     label: intl.formatMessage({ id: 'workflow.result' }),
                    //     key: '2',
                    //     disabled: !endRun,
                    //     children: <ResultContent></ResultContent>,
                    // },
                    {
                        label: intl.formatMessage({ id: 'workflow.result' }),
                        key: '3',
                        disabled: !endRun,
                        children: <DetailContent endRun={endRun}></DetailContent>,
                    },
                    {
                        label: intl.formatMessage({ id: 'workflow.backTo' }),
                        key: '4',
                        disabled: !hasResult,
                        children: (
                            <div className="">
                                <TrackContent key="4" runList={runList}></TrackContent>
                            </div>
                        ),
                    },
                ],
                onChange: setTabKey,
            }}
        ></ProCard>
    ) : null;
});
type InputContentProps = {
    onRunResult: (res: any) => void;
    loading?: boolean;
};
const InputContent = memo(({ onRunResult, loading }: InputContentProps) => {
    const intl = useIntl();
    const nodes = useStore(state => state.nodes);
    const getOutputVariables = useStore(state => state.getOutputVariables);
    const app_id = useStore(state => state.app_id);
    const [submitLoading, setSubmitLoading] = useState(false);
    const saveWorkFlow = useSaveWorkFlow();
    const datasetData = useStore(state => state.datasetData);
    useMount(() => {
        console.log(999);

        console.log(getOutputVariables(nodes[0].id));
    });

    useUpdateEffect(() => {
        if (loading == false) {
            setSubmitLoading(false);
        }
    }, [loading]);

    const run = async value => {
        const findEnd = nodes.find(x => x.type == BlockEnum.End);
        if (!findEnd) {
            return message.error(intl.formatMessage({ id: 'workflow.notEnd', defaultMessage: '' }));
        }

        setSubmitLoading(true);
        await saveWorkFlow();
        const input = new ObjectVariable('input_var');
        const vals = getOutputVariables(nodes[0].id);
        const regex = /^(file|run_name|dataset\..*)/;
        for (const key in value) {
            const item = value[key];
            if (key.startsWith('var.')) {
                const varName = key.replace('var.', '');
                const val = vals.find(x => x.createVar.name == varName);
                const variable = new Variable(varName, val?.createVar.type, item);
                input.addProperty(varName, variable);
            }
        }
        const freeFile = new ArrayVariable(UPLOAD_FILES_KEY, 'array[number]');
        value.file &&
            value.file.forEach(x => {
                const fileVariable = new Variable(x.uid, 'number', x?.response?.data?.file_id || 0);
                freeFile.addValue(fileVariable);
            });
        input.addProperty(UPLOAD_FILES_KEY, freeFile);
        const knowledge_base_mapping = nodes[0]?.data?.knowledge_base_mapping || {
            input: {},
            output: {},
        };
        Object.entries(value).forEach(([key, value]) => {
            if (key.startsWith('dataset.')) {
                if (!knowledge_base_mapping.input[UPLOAD_FILES_KEY]) {
                    knowledge_base_mapping.input[UPLOAD_FILES_KEY] = {};
                }
                knowledge_base_mapping.input[UPLOAD_FILES_KEY][key.replace('dataset.', '')] = value;
            }
        });

        const params = {
            run_name: value.run_name,
            inputs: input,
            run_type: 0,
            node_confirm_users: {},
            knowledge_base_mapping,
        };

        runWorkFlow(app_id, params)
            .then(res => {
                console.log(res);
                setSubmitLoading(false);
                onRunResult?.(res);
            })
            .catch(err => {
                setSubmitLoading(false);
                console.log(err);
            });
    };
    return (
        <>
            <ProForm
                loading={submitLoading}
                submitter={{
                    resetButtonProps: false,
                    submitButtonProps: {
                        className: 'w-full',
                    },
                    searchConfig: {
                        submitText: intl.formatMessage({
                            id: 'workflow.run',
                            defaultMessage: '',
                        }),
                    },
                }}
                onFinish={run}
            >
                <TextareaRunName name={'run_name'}></TextareaRunName>
                {nodes[0]?.id &&
                    getOutputVariables(nodes[0].id).sort((a,b)=>a.createVar.sort_order - b.createVar.sort_order).map((item, index) => {
                        if (item?.createVar?.type == 'number') {
                            return (
                                <ProFormDigit
                                    key={index}
                                    label={item.createVar.display_name || item.createVar.name}
                                    name={`var.${item.createVar.name}`}
                                    required={item.createVar.required}
                                    rules={[
                                        {
                                            required: item.createVar.required,
                                            message: intl.formatMessage({
                                                id: 'workflow.isRequire',
                                            }),
                                        },
                                    ]}
                                ></ProFormDigit>
                            );
                        }
                        return (
                            <ProFormTextArea
                                key={index}
                                label={item.createVar.display_name || item.createVar.name}
                                name={`var.${item.createVar.name}`}
                                required={item.createVar.required}
                                rules={[
                                    {
                                        required: item.createVar.required,
                                        message: intl.formatMessage({ id: 'workflow.isRequire' }),
                                    },
                                ]}
                            ></ProFormTextArea>
                        );
                    })}
                {nodes[0]?.data?.requires_upload && (
                    <div>
                        <Typography.Title level={5}>
                            {intl.formatMessage({ id: 'workflow.uploadFile' })}
                        </Typography.Title>
                        <UploadDragger 
                            name="file"
                            multiple={true}
                          
                        />

                        <ProFormDependency name={['file']}>
                            {({ file }) => {
                                return (
                                    (nodes[0]?.data?.import_to_knowledge_base &&
                                        file?.length > 0 && (
                                            <div>
                                                <Typography.Title level={5}>
                                                    {intl.formatMessage({
                                                        id: 'workflow.import_to_knowledge_base',
                                                    })}
                                                </Typography.Title>
                                                {file?.map(x => {
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
                                                })}
                                            </div>
                                        )) ||
                                    null
                                );
                            }}
                        </ProFormDependency>
                    </div>
                )}
            </ProForm>
        </>
    );
});



const DetailContent = memo(({ endRun }) => {
    const intl = useIntl();
    const [messageType, setMessageType] = useState<'success' | 'fail'>('fail');
    const form = useRef(null);
    const [code, setCode] = useState('');
    const messConfig = {
        statusClass: {
            success: 'green-700',
            fail: 'red-700',
        },
        message: {
            success: 'Success',
            fail: 'Fail',
        },
        messageType: {
            success: 'success',
            fail: 'error',
        },
    } as const;
    type MessConfigKeys = keyof typeof messConfig;
    const getMessage = useCallback(
        (configName: MessConfigKeys) => {
            return messConfig[configName][messageType];
        },
        [messageType],
    );

    useEffect(() => {
        if (endRun) {
            form?.current.setFieldsValue({
                status: 'success',
                elapsed_time: endRun?.data?.elapsed_time?.toFixed(4) || 0,
                completion_tokens: endRun?.data?.completion_tokens || '',
                created_time: endRun?.data?.created_time || '',
                total_tokens: endRun?.data?.total_tokens || '',
                actual_completed_steps: endRun?.data?.actual_completed_steps || '',
            });
            setMessageType('success');
        }
    }, [endRun]);

    const Message = () => {
        return (
            <div>
                <div className="grid grid-cols-3">
                    <div>
                        <div className="text-gray-500 text-sm">
                            {intl.formatMessage({
                                id: 'workflow.label.status',
                                defaultMessage: '',
                            })}
                        </div>
                        <div
                            className={`text-${getMessage(
                                'statusClass',
                            )} font-bold text-base flex gap-2 items-center`}
                        >
                            <div className={`size-2  bg-${getMessage('statusClass')}`}></div>
                            {getMessage('message')}
                        </div>
                    </div>
                    <div>
                        <div className="text-gray-500 text-sm">
                            {intl.formatMessage({
                                id: 'workflow.label.elapsedTime',
                                defaultMessage: '',
                            })}
                        </div>
                        <div className="font-bold text-base">
                            {endRun?.data?.elapsed_time?.toFixed(4) || 0}s
                        </div>
                    </div>
                    <div>
                        <div className="text-gray-500 text-sm">
                            {intl.formatMessage({
                                id: 'workflow.label.totalTokens',
                                defaultMessage: 'token',
                            })}
                        </div>
                        <div className=" font-bold text-base">
                            {endRun?.data?.total_tokens || 0} Tokens
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const alertType = getMessage('messageType') as 'success' | 'error';
    return (
        <>
            <Alert message={<Message></Message>} type={alertType}></Alert>
            <div className="h-80 mt-4 w-[350px]">
                <CodeEditor
                    language="python3"
                    value={endRun?.data?.node_exec_data?.outputs}
                    mdValue={endRun?.data?.node_exec_data?.outputs_md}
                    readOnly
                    isJSONStringifyBeauty
                    title={intl.formatMessage({
                        id: 'workflow.label.output',
                        defaultMessage: '',
                    })}
                ></CodeEditor>
            </div>

            <Divider orientationMargin="0" orientation="left">
                {intl.formatMessage({ id: 'workflow.label.metadata', defaultMessage: '' })}
            </Divider>

            <ProForm
                layout="horizontal"
                formRef={form}
                initialValues={{
                    status: 'fail',
                }}
                submitter={false}
                labelAlign="left"
                labelCol={{ span: 8 }}
                wrapperCol={{ span: 16 }}
            >
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({
                        id: 'workflow.label.status',
                        defaultMessage: '',
                    })}
                    name="status"
                ></ProFormText>
                <ProFormDateTimePicker
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({
                        id: 'workflow.label.startTime',
                        defaultMessage: '',
                    })}
                    name="created_time"
                ></ProFormDateTimePicker>
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({
                        id: 'workflow.label.elapsedTime',
                        defaultMessage: '',
                    })}
                    name="elapsed_time"
                ></ProFormText>
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({
                        id: 'workflow.label.totalTokens',
                        defaultMessage: 'token',
                    })}
                    name="total_tokens"
                ></ProFormText>
                <ProFormText
                    formItemProps={{
                        className: '!mb-0',
                    }}
                    readonly
                    label={intl.formatMessage({
                        id: 'workflow.label.completedSteps',
                        defaultMessage: '',
                    })}
                    name="actual_completed_steps"
                ></ProFormText>
            </ProForm>

            {endRun?.data?.node_exec_data?.file_list?.length > 0 && (
                <FileDownloadList 
                    files={endRun.data.node_exec_data.file_list} 
                    title={intl.formatMessage({ id: 'skill.downloadFiles' })}
                />
            )}
        </>
    );
});
