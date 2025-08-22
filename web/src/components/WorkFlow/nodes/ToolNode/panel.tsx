/*
 * @LastEditors: biz
 */
import { delToolAuthorization, getToolAuthorizationStatus, getToolDetail } from '@/api/workflow';
import {
    ProForm,
    ProFormDigit,
    ProFormSelect,
    ProFormSwitch,
    ProFormText,
} from '@ant-design/pro-components';
import { getLocale, useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import { Button, Tag, Space, Modal } from 'antd';
import { CheckCircleOutlined, DeleteOutlined, EditOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import Link from 'antd/lib/typography/Link';
import { debounce } from 'lodash';
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import CodeEditor from '../../components/Editor/CodeEditor';
import ProFormWrapperEditor from '../../components/Editor/ProFormWrapperEditor';
import useStore from '../../store';
import { AppNode } from '../../types';

type PromptItem = {
    serializedContent: string;
    value: object;
};
interface Prompt {
    system: PromptItem;
    user: PromptItem;
    assistant: PromptItem;
}

interface CredentialsProviderItem {
    name: string;
    url?: string;
    help?: { zh_Hans: string };
    required: boolean;
    placeholder?: { zh_Hans: string };
    label?: { zh_Hans: string };
}

// Create JSONFormEditor component outside of render cycle to avoid recreation
const JSONFormEditor = ({
    value,
    onChange,
    fieldName,
}: {
    value?: string;
    onChange?: (value: string) => void;
    fieldName?: string;
}) => {
    const valueRef = useRef(value);

    // Sync external value changes to internal reference
    useEffect(() => {
        valueRef.current = value;
    }, [value]);

    // Use useMemo to create stable CodeEditor instance
    const CodeEditorMemo = useMemo(
        () => (
            <div className="h-[300px]">
                <CodeEditor
                    language="json"
                    height={200}
                    isJSONStringifyBeauty
                    value={valueRef.current}
                    onChange={newValue => {
                        valueRef.current = newValue;
                        onChange?.(newValue);
                    }}
                    showMaximize={true}
                />
            </div>
        ),
        [fieldName], // Only depend on field name to keep editor instance stable
    );

    return CodeEditorMemo;
};

export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    const nodes = useStore(state => state.nodes);
    const [params, setParams] = useState<any>([]);
    const [authorizationStatus, setAuthorizationStatus] = useState<any>(1);
    const [credentialsProvider, setCredentialsProvider] = useState<Record<
        string,
        CredentialsProviderItem
    > | null>(null);
    const [editorOptions, setEditorOptions] = useState([]);
    const [loading, setLoading] = useState(false);

    const updateNodeDataRef = useRef(updateNodeData);
    const nodeIdRef = useRef(node.id);
    const loadingRef = useRef(loading);

    useEffect(() => {
        updateNodeDataRef.current = updateNodeData;
        nodeIdRef.current = node.id;
        loadingRef.current = loading;
    });

    const getGroupDetail = async () => {
        const res = await getToolDetail(node.data?.baseData?.groupName);
        if(res?.code==0){
            // setToolDetail(res?.data);
            setAuthorizationStatus(res?.data?.authorization_status);
        }
    };
    useMount(() => {
        setLoading(true);
        const nodeData = node.data as any;
        setParams(nodeData?.baseData?.parameters || []);
        
        // setAuthorizationStatus(nodeData?.baseData?.authorization_status || 1);
        setCredentialsProvider(nodeData?.baseData?.credentials_for_provider || null);
        getGroupDetail();
        const vars = getVariables(node.id);
        setEditorOptions(vars);

        setTimeout(() => {
            const fieldNames = Object.keys(formRef?.current?.getFieldsValue() || {});
            if (!fieldNames?.length) {
                setLoading(false);
                return;
            }
            debugger
            fieldNames
                // .filter(x => nodeData['form']?.[x])
                .forEach(e => {
                    if (nodeData['form']?.[e] && nodeData['form']?.[e] != '') {
                        formRef.current.setFieldsValue({ [e]: nodeData['form']?.[e] });
                        debugger
                    } else {
                        const hasDefault = nodeData?.baseData?.parameters?.find(
                            x => x.name == e && x.default,
                        );
                        if (hasDefault) {
                            switch(hasDefault.type){
                                case "object":
                                case "json":
                                case "array":
                                case "string":
                                    setEditorValue(e, hasDefault.default);
                                    break;
                                default:
                                    formRef.current.setFieldsValue({ [e]: hasDefault.default });
                                    break;
                            }
                         
                        }
                    }
                });
            setLoading(false);
        }, 200);
    });

    useUpdateEffect(() => {
        setLoading(true);
        const vars = getVariables(node.id);
        setEditorOptions(vars);

        const nodeData = node.data as any;
        if (formRef.current && nodeData?.form) {
            formRef.current.setFieldsValue(nodeData.form);
        }

        setTimeout(() => {
            setLoading(false);
        }, 100);
    }, [node.id, node.data]);

    const setNodeChange = useCallback(
        debounce((addItem: { [key: string]: any }, allValue) => {
            if (loadingRef.current) {
                return;
            }
            updateNodeDataRef.current(nodeIdRef.current, {
                form: allValue,
            });
        }, 300),
        [],
    );

    const getToolAuthorization = async e => {
        const nodeData = node.data as any;
        const res = await getToolAuthorizationStatus(nodeData?.baseData?.groupName, e);
        if (res?.code == 0) {
            setAuthorizationStatus(1);
            updateNodeData(node.id, {
                baseData: {
                    ...nodeData?.baseData,
                    authorization_status: 1,
                },
            });
            const nodeList = nodes.filter(x=>x.data?.baseData?.groupName==nodeData?.baseData?.groupName);
            nodeList.forEach(x=>{
                updateNodeData(x.id, {
                    baseData: {
                        ...x.data?.baseData,
                        authorization_status: 1,
                    },
                });
            });
        }
    };

    const setEditorValue = useCallback((name: string, value: string) => {
        if (formRef.current) {
            const newValue = [
                {
                    type: 'paragraph',
                    children: [
                        {
                            text: value,
                        },
                    ],
                },
            ];
            formRef.current.setFieldsValue({ [name]: newValue });
        }
    }, []);

    const delAuthorization = async () => {
        Modal.confirm({
            title: intl.formatMessage({
                id: 'workflow.authorization.confirmDelete',
                defaultMessage: 'Confirm Delete Authorization?',
            }),
            content: intl.formatMessage({
                id: 'workflow.authorization.confirmDeleteContent',
                defaultMessage: 'After deleting authorization, you need to re-authorize to use this tool',
            }),
            okText: intl.formatMessage({
                id: 'workflow.authorization.delete',
                defaultMessage: 'Delete Authorization',
            }),
            cancelText: intl.formatMessage({
                id: 'workflow.cancel',
                defaultMessage: 'Cancel',
            }),
            onOk: async () => {
                const res = await delToolAuthorization(node.data?.baseData?.groupName);
                if (res?.code == 0) {
                    setAuthorizationStatus(2);
                    const nodeData = node.data as any;
                    updateNodeData(node.id, {
                        baseData: {
                            ...nodeData?.baseData,
                            authorization_status: 2,
                        },
                    });
                }
            },
        });
    };
    const lang = getLocale() === 'en-US' ? 'en_US' : 'zh_Hans';
    return (
        <>
            <div className="pt-4">
                {authorizationStatus == 2 ? (
                    <ProForm
                        onFinish={getToolAuthorization}
                        autoFocusFirstInput={false}
                        submitter={{
                            resetButtonProps: false,
                            submitButtonProps: {
                                className: 'w-full',
                            },
                            searchConfig: {
                                submitText: intl.formatMessage({
                                    id: 'workflow.button.authorize',
                                    defaultMessage: '',
                                }),
                            },
                        }}
                    >
                        
                        {credentialsProvider &&
                            Object.values(credentialsProvider).map((e: CredentialsProviderItem) => {
                                return (
                                    <div key={e.name}>
                                      
                                        <ProFormText
                                            tooltip={
                                                e?.help?.[lang]||e?.help?.['zh_CN'] ? (
                                                    <Link href={e?.url} underline target="_blank">
                                                        {e?.help?.[lang]||e?.help?.['zh_CN']}
                                                    </Link>
                                                ) : null
                                            }
                                            required={e.required}
                                            placeholder={e.placeholder?.[lang]||e.placeholder?.['zh_CN']}
                                            rules={[
                                                {
                                                    required: e.required,
                                                    message: e.placeholder?.[lang]||e.placeholder?.['zh_CN'],
                                                },
                                            ]}
                                            name={e.name}
                                            label={e?.label?.[lang]||e?.label?.['zh_CN']}
                                        ></ProFormText>
                                    </div>
                                );
                            })}
                    </ProForm>
                ) : (
                    <ProForm
                        submitter={{
                            render: () => null,
                        }}
                        formRef={formRef}
                        omitNil={false}
                        className='user-form'
                        onValuesChange={setNodeChange}
                        initialValues={(node.data as any)?.form || {}}
                    >
                        <div className="mb-4 flex items-center justify-between gap-3  rounded-lg  border-gray-200">
                            <Space align="center">
                                {authorizationStatus != 3 && (
                                    <Tag 
                                        icon={<CheckCircleOutlined />} 
                                        color="success" 
                                        className="flex items-center gap-1 px-3 py-1 text-sm font-medium"
                                        title={intl.formatMessage({
                                            id: 'workflow.authorization.tooltip.authorized',
                                            defaultMessage: 'This tool has been authorized and can be used normally',
                                        })}
                                    >
                                        {intl.formatMessage({
                                            id: 'workflow.authorization.authorized',
                                            defaultMessage: 'Authorized',
                                        })}
                                    </Tag>
                                )}
                            
                            </Space>
                            {authorizationStatus == 1 && authorizationStatus != 3 && (
                                <div className='flex items-center gap-2'>
                                    <Button 
                                    type="primary" 
                                    icon={<EditOutlined />}
                                    onClick={() => setAuthorizationStatus(2)}
                                    className="flex items-center gap-1"
                                    title={intl.formatMessage({
                                        id: 'workflow.authorization.tooltip.modify',
                                        defaultMessage: 'Modify the authorization information for the current tool',
                                    })}
                                >
                                    {intl.formatMessage({
                                        id: 'workflow.authorization.modify',
                                        defaultMessage: 'Modify Authorization',
                                    })}
                                </Button>
                               
                                </div>
                            )}
                        </div>

                        <div className="user-form row">
                            <ProFormSwitch
                                name="manual_confirmation"
                                label={intl.formatMessage({
                                    id: 'workflow.label.manualConfirmation',
                                    defaultMessage: '',
                                })}
                            ></ProFormSwitch>
                            <ProFormSwitch
                                name="wait_for_all_predecessors"
                                label={intl.formatMessage({
                                    id: 'workflow.label.waitForAllPredecessors',
                                    defaultMessage: '',
                                })}
                            ></ProFormSwitch>
                        </div>
                        {params.map((e, index) => {
                            const baseProps = {
                                name: e.name,
                                label: e?.label?.zh_Hans,
                                tooltip: e?.human_description?.zh_Hans,
                                key: e.name,
                                required: e.required,
                            };
                            // if (e.default) {
                            //     setTimeout(() => {
                            //         setEditorValue(e.name, e.default);
                            //     }, 200);
                            // }
                            // if (!e.required) return null;
                            // debugger;
                            switch (e.type) {
                                case 'object':
                                case 'json':
                                //  {
                                // Create wrapper component to properly handle Form.Item value synchronization
                                //     return (
                                //         <ProFormItem
                                //             name={e.name}
                                //             label={e?.label?.zh_Hans}
                                //             tooltip={e?.human_description?.zh_Hans}
                                //             required={e.required}
                                //             rules={[
                                //                 {
                                //                     required: e.required,
                                //                     message: intl.formatMessage({
                                //                         id: 'workflow.form.parameter.required',
                                //                     }),
                                //                 },
                                //                 {
                                //                     validator: (_, value) => {
                                //                         if (!value) return Promise.resolve();
                                //                         try {
                                //                             JSON.parse(value);
                                //                             return Promise.resolve();
                                //                         } catch (error) {
                                //                             return Promise.reject(
                                //                                 new Error(intl.formatMessage({ id: 'workflow.form.parameter.json.invalid' })),
                                //                             );
                                //                         }
                                //                     },
                                //                 },
                                //             ]}
                                //             initialValue={{}}

                                //         >
                                //             <JSONFormEditor fieldName={e.name} />
                                //         </ProFormItem>
                                //     );
                                // }
                                case 'array':
                                case 'string':
                                    return (
                                        <ProFormWrapperEditor
                                            {...baseProps}
                                            placeholder={intl.formatMessage({
                                                id: 'workflow.placeholder.fillPrompt',
                                            })}
                                            title={`Editor`}
                                            options={editorOptions}
                                            rules={[
                                                {
                                                    required: e.required,
                                                    message: intl.formatMessage({
                                                        id: 'workflow.form.parameter.required',
                                                    }),
                                                },
                                            ]}
                                        />
                                    );
                                case 'number':
                                    return <><ProFormDigit {...baseProps} /></>;
                                case 'select':
                                    return (
                                        <ProFormSelect
                                            {...baseProps}
                                            options={e.options.map(x => {
                                                return {
                                                    ...x,
                                                    label: x.label?.zh_Hans,
                                                };
                                            })}
                                        />
                                    );
                                case 'boolean':
                                    return <div className='user-form row'><ProFormSwitch {...baseProps} /></div>;
                            }
                        })}

                        <div className="h-80"></div>
                    </ProForm>
                )}
            </div>
        </>
    );
});
