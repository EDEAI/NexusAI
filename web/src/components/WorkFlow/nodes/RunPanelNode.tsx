/*
 * @LastEditors: biz
 */
import { runNode } from '@/api/workflow';
import FileDownloadList from '@/components/common/FileDownloadList';
import { ObjectVariable, Variable } from '@/py2js/variables.js';
import { CloseOutlined } from '@ant-design/icons';
import {
    ProCard,
    ProForm,
    ProFormDigit,
    ProFormText,
    ProFormTextArea,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount } from 'ahooks';
import { Alert, Button, Divider, Typography } from 'antd';
import _ from 'lodash';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import CodeEditor from '../components/Editor/CodeEditor';
import { UploadDragger } from '../components/Form/Upload';
import useNodeIdUpdate from '../hooks/useNodeIdUpdate';
import useSaveWorkFlow from '../saveWorkFlow';
import useStore from '../store';

export default memo(() => {
    const intl = useIntl();
    const runPanelShow = useStore(state => state.runPanelNodeShow);
    const setRunPanelShow = useStore(state => state.setRunPanelNodeShow);
    const runPanelAllsShow = useStore(state => state.runPanelShow);
    const [hasResult, setHasResult] = useState(false);
    const [result, setResult] = useState(null);
    useNodeIdUpdate(() => {
        setHasResult(false);
        setResult(null);
    });
    const runResult = e => {
        console.log(e);
        setHasResult(true);
        setResult(e.data);
    };
    const onClose = () => {
        setRunPanelShow(false);
        setResult(null);
        setHasResult(false);
    };
    const DetailContent = memo(() => {
        const [messageType, setMessageType] = useState<'success' | 'fail'>('fail');
        const form = useRef(null);
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
            setMessageType(result.status == 'success' ? 'success' : 'fail');
            form.current.setFieldsValue({
                status: result.status == 'success' ? 'success' : 'fail',
                elapsed_time: result?.data?.elapsed_time?.toFixed(4) || 0,
                completion_tokens: result?.data?.completion_tokens || '',
                finished_time: result?.data?.finished_time || '',
            });
        }, [result]);

        const handleCodeChange = e => {};
        const Message = () => {
            return (
                <div className="">
                    <div className="grid grid-cols-3">
                        <div>
                            <div className="text-gray-500 text-sm">
                                {intl.formatMessage({ id: 'workflow.status' })}
                            </div>
                            <div
                                className={`text-${getMessage(
                                    'statusClass',
                                )} font-bold text-base flex gap-2 items-center`}
                            >
                                <div className="size-0 bg-green-700 bg-red-700"></div>
                                <div className={`size-2  bg-${getMessage('statusClass')}`}></div>
                                {getMessage('message')}
                            </div>
                        </div>
                        <div>
                            <div className="text-gray-500 text-sm">
                                {intl.formatMessage({ id: 'workflow.elapsed_time' })}
                            </div>
                            <div className="font-bold text-base">
                                {result?.data?.elapsed_time?.toFixed(4) || 0}s
                            </div>
                        </div>
                        <div>
                            <div className="text-gray-500 text-sm">
                                {intl.formatMessage({ id: 'workflow.completion_tokens' })}
                            </div>
                            <div className=" font-bold text-base">
                                {result?.data?.completion_tokens || 0} Tokens
                            </div>
                        </div>
                    </div>
                </div>
            );
        };

        const alertType = getMessage('messageType') as 'success' | 'error';

        let outputs = {};

        Object.entries(result?.data?.outputs || {})?.forEach(([key, value]: [string, string]) => {
            try {
                outputs[key] = JSON.parse(value);
            } catch (error) {
                console.log('error', error);

                outputs[key] = value;
            }
        });

        return (
            <div className="mt-4 ">
                {/* <Badge.Ribbon text='Fail' color='red'> */}
                <Alert message={<Message></Message>} type={alertType}></Alert>

                {messageType == 'fail' && (
                    <Alert
                        message={result?.message}
                        className="text-red-500 mt-4"
                        type={alertType}
                    ></Alert>
                )}
                {result?.data?.outputs && (
                    <div className="h-80 mt-4">
                        <CodeEditor
                            language="python3"
                            value={outputs}
                            mdValue={result?.data?.outputs_md}
                            isJSONStringifyBeauty
                            onChange={handleCodeChange}
                            title={intl.formatMessage({ id: 'workflow.outputs' })}
                        ></CodeEditor>
                    </div>
                )}

                {result?.data?.file_list?.length > 0 && (
                    <FileDownloadList
                        files={result.data.file_list}
                        title={intl.formatMessage({ id: 'skill.downloadFiles' })}
                        className="mt-4"
                    />
                )}

                <Divider orientationMargin="0" orientation="left">
                    {intl.formatMessage({ id: 'workflow.orcompute' })}
                </Divider>

                <ProForm
                    layout="horizontal"
                    formRef={form}
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
                        label={intl.formatMessage({ id: 'workflow.status' })}
                        name="status"
                    ></ProFormText>
                    <ProFormText
                        formItemProps={{
                            className: '!mb-0',
                        }}
                        readonly
                        label={intl.formatMessage({ id: 'workflow.finished_time' })}
                        name="finished_time"
                    ></ProFormText>
                    <ProFormText
                        formItemProps={{
                            className: '!mb-0',
                        }}
                        readonly
                        label={intl.formatMessage({ id: 'workflow.elapsed_time' })}
                        name="elapsed_time"
                    ></ProFormText>
                    <ProFormText
                        formItemProps={{
                            className: '!mb-0',
                        }}
                        readonly
                        label={intl.formatMessage({ id: 'workflow.completion_tokens' })}
                        name="completion_tokens"
                    ></ProFormText>
                    {/* <ProFormText
                        formItemProps={{
                            className: '!mb-0',
                        }}
                        readonly
                        label=""
                        name="status"
                    ></ProFormText> */}
                </ProForm>
                {/* </Badge.Ribbon> */}
            </div>
        );
    });
    return runPanelShow ? (
        <ProCard
            className=" border border-blue-300 fixed z-10  top-[105px] right-2 duration-300"
            style={{
                height: 'calc(100vh - 10px - 100px)',
                width: 'inherit',
                right: runPanelAllsShow ? '420px' : '',
            }}
            bodyStyle={{ overflowY: 'auto' }}
            extra={
                <Button
                    type="text"
                    className="-mr-4 -mt-8"
                    onClick={onClose}
                    icon={<CloseOutlined></CloseOutlined>}
                ></Button>
            }
            title={
                <Typography.Title level={5}>
                    {intl.formatMessage({ id: 'workflow.runNode.title' })}
                </Typography.Title>
            }
        >
            <div className="overflow-y-auto">
                <InputContent onRunResult={runResult}></InputContent>
                {hasResult ? <DetailContent></DetailContent> : null}
            </div>
        </ProCard>
    ) : null;
});
type InputContentProps = {
    onRunResult: (res: any) => void;
};
const InputContent = memo(({ onRunResult }: InputContentProps) => {
    const intl = useIntl();
    const runPanelShow = useStore(state => state.runPanelNodeShow);
    const getOutputVariables = useStore(state => state.getOutputVariables);
    const selectNode = runPanelShow?.data?.isChild
        ? runPanelShow
        : useStore(state => state.selectedNode);
    const getInputVariables = useStore(state => state.getInputVariables);
    const app_id = useStore(state => state.app_id);
    const [submitLoading, setSubmitLoading] = useState(false);
    const [inputs, setInputs] = useState([]);
    const [contexts, setContext] = useState([]);
    const [formInfo, setFormInfo] = useState({});
    const saveWorkFlow = useSaveWorkFlow();
    useMount(() => {
        if (!selectNode?.id) return;
        const vars = getInputVariables(selectNode.id);
        const variable = getOutputVariables(selectNode.id);
        console.log(vars, variable);
        if (vars?.inputs) {
            if (vars.inputs['type'] == 'object') {
                const inputs = Object.values(vars.inputs['properties']);
                setInputs(inputs);
            } else {
                setInputs([vars.inputs]);
            }
        }
        if (vars?.context) {
            const varGroup = {};
            vars.context.forEach(x => {
                // ,`<<${x.identifier}.${x.ioType}.${x.fieldName}>>`
                const varItem = variable.find(
                    m => m.value == `<<${x.identifier}.${x.ioType}.${x.fieldName}>>`,
                );
                if (!varItem) {
                    return console.warn('', variable, x.identifier);
                }
                console.log(x, varItem);
                if (!varGroup[x.identifier]) {
                    varGroup[x.identifier] = {
                        name: varItem.title,
                        id: x.identifier,
                        list: [],
                        ...varItem,
                    };
                }
                varGroup[x.identifier].list.push({
                    ...x,
                    ...varItem,
                    name: x.fieldName,
                });
            });
            console.log(varGroup);

            setContext(Object.values(varGroup));
        }
        setFormInfo(vars);
    });

    const run = async value => {
        console.log(value);
        setSubmitLoading(true);
        await saveWorkFlow();
        const input = new ObjectVariable('inputs');

        const getArr = name => Object.entries(value).filter(([key]) => key.includes(name));
        getArr('inputs').forEach(([key, val]) => {
            const name = key.split('.')[1];
            const item = inputs.find(x => x.name == name);
            const variable = new Variable(name, item?.type, val);
            input.addProperty(name, variable);
        });

        const context = contexts.map(x => {
            console.log(x);
            const node = {
                level: 0,
                node_id: x.id,
                node_title: x.name,
                node_type: x.type,
                inputs: null,
                outputs: null,
            };
            const output = new ObjectVariable('output');
            x.list.forEach(item => {
                const name = `contexts.${x.id}.${item.name}`;
                let val = value[name];

                if (item.createVar?.type == 'file') {
                    val = val[0]?.response?.data?.file_id;
                }

                const variable = new Variable(
                    item.name,
                    item.createVar?.type || 'string',
                    val || '',
                );

                output.addProperty(item.name, variable);
            });
            node.outputs = output;
            return node;
        });

        const params = {
            node_id: selectNode?.currentId || selectNode.id,
            parent_node_id: selectNode?.currentId ? selectNode.id : null,
            inputs: null,
            context: context,
        };
        console.log(JSON.stringify(params));

        if (!_.isEmpty(input.properties)) {
            params.inputs = input;
        }
        runNode(app_id, params)
            .then(res => {
                console.log(res);
                onRunResult?.(res);
            })
            .catch(err => {
                console.log(err);
            })
            .finally(() => {
                setSubmitLoading(false);
            });
    };

    return (
        <>
            <ProForm
                loading={submitLoading}
                layout="vertical"
                submitter={{
                    resetButtonProps: false,
                    submitButtonProps: {
                        className: 'w-full',
                    },
                    searchConfig: {
                        submitText: intl.formatMessage({ id: 'workflow.run' }),
                    },
                }}
                onFinish={run}
            >
                {inputs.length > 0 && (
                    <div>
                        <div className="font-bold text-base mb-2">
                            {intl.formatMessage({
                                id: 'workflow.inputs',
                                defaultMessage: 'Inputs',
                            })}
                        </div>
                        {inputs.map((item, index) => {
                            if (item?.type == 'number') {
                                return (
                                    <ProFormDigit
                                        key={index}
                                        label={item.display_name || item.name}
                                        name={`inputs.${item.name}`}
                                        required={item.required}
                                        rules={[
                                            {
                                                required: item.required,
                                                message: intl.formatMessage({
                                                    id: 'workflow.isRequire',
                                                }),
                                            },
                                        ]}
                                    ></ProFormDigit>
                                );
                            }
                            if (item.type === 'file') {
                                return (
                                    <div key={item.name}>
                                        <Typography.Title level={5}>
                                            {item.display_name || item.name}
                                            {item.required && (
                                                <span className="text-red-500 ml-1">*</span>
                                            )}
                                        </Typography.Title>
                                        <UploadDragger
                                            name={`inputs.${item.name}`}
                                            multiple={false}
                                        />
                                    </div>
                                );
                            }
                            return (
                                <ProFormTextArea
                                    key={index}
                                    label={item.display_name || item.name}
                                    name={`inputs.${item.name}`}
                                    required={item.required}
                                    rules={[
                                        {
                                            required: item.required,
                                            message: intl.formatMessage({
                                                id: 'workflow.isRequire',
                                            }),
                                        },
                                    ]}
                                ></ProFormTextArea>
                            );
                        })}
                    </div>
                )}

                {contexts.length > 0 && (
                    <div>
                        <div className="font-bold text-base mb-2">
                            {intl.formatMessage({
                                id: 'workflow.context',
                                defaultMessage: 'Context',
                            })}
                        </div>
                        {contexts.map((x, index) => {
                            console.log(x);

                            return (
                                <div className="mb-2" key={index}>
                                    <ProCard title={x.name} ghost>
                                        {x.list.map((item, i) => {
                                            if (item?.createVar?.type == 'number') {
                                                return (
                                                    <ProFormDigit
                                                        key={i}
                                                        label={
                                                            <div>
                                                                {item?.createVar?.display_name ||
                                                                    item.name}{' '}
                                                            </div>
                                                        }
                                                        name={`contexts.${item.identifier}.${item.name}`}
                                                        required={item.required}
                                                        rules={[
                                                            {
                                                                required: item.required,
                                                                message: intl.formatMessage({
                                                                    id: 'workflow.isRequire',
                                                                }),
                                                            },
                                                        ]}
                                                    ></ProFormDigit>
                                                );
                                            }
                                            if (item?.createVar?.type === 'file') {
                                                return (
                                                    <div key={item.name}>
                                                        <UploadDragger
                                                            name={`contexts.${item.identifier}.${item.name}`}
                                                            multiple={false}
                                                            label={
                                                                item?.createVar?.display_name ||
                                                                item.name
                                                            }
                                                        />
                                                    </div>
                                                );
                                            }

                                            return (
                                                <ProFormTextArea
                                                    key={i}
                                                    label={
                                                        <div>
                                                            {item?.createVar?.display_name ||
                                                                item.name}{' '}
                                                        </div>
                                                    }
                                                    name={`contexts.${item.identifier}.${item.name}`}
                                                    required={item.required}
                                                    rules={[
                                                        {
                                                            required: item.required,
                                                            message: intl.formatMessage({
                                                                id: 'workflow.isRequire',
                                                            }),
                                                        },
                                                    ]}
                                                ></ProFormTextArea>
                                            );
                                        })}
                                    </ProCard>
                                </div>
                            );
                        })}
                    </div>
                )}
            </ProForm>
        </>
    );
});
