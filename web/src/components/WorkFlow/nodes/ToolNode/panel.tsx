/*
 * @LastEditors: biz
 */
import { getToolAuthorizationStatus } from '@/api/workflow';
import {
    ProForm,
    ProFormDigit,
    ProFormSelect,
    ProFormSwitch,
    ProFormText,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
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

    useMount(() => {
        setLoading(true);
        const nodeData = node.data as any;
        setParams(nodeData?.baseData?.parameters || []);
        setAuthorizationStatus(nodeData?.baseData?.authorization_status || 1);
        setCredentialsProvider(nodeData?.baseData?.credentials_for_provider || null);

        const vars = getVariables(node.id);
        setEditorOptions(vars);

        setTimeout(() => {
            const fieldNames = Object.keys(formRef?.current?.getFieldsValue() || {});
            if (!fieldNames?.length) {
                setLoading(false);
                return;
            }
            fieldNames
                // .filter(x => nodeData['form']?.[x])
                .forEach(e => {
                    if (nodeData['form']?.[e] && nodeData['form']?.[e] != '') {
                        formRef.current.setFieldsValue({ [e]: nodeData['form']?.[e] });
                    } else {
                        const hasDefault = nodeData?.baseData?.parameters?.find(
                            x => x.name == e && x.default,
                        );
                        if (hasDefault) {
                            setEditorValue(e, hasDefault.default);
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
                                                <Link href={e?.url} underline target="_blank">
                                                    {e?.help?.zh_Hans}
                                                </Link>
                                            }
                                            required={e.required}
                                            placeholder={e.placeholder?.zh_Hans}
                                            rules={[
                                                {
                                                    required: e.required,
                                                    message: e.placeholder?.zh_Hans,
                                                },
                                            ]}
                                            name={e.name}
                                            label={e?.label?.zh_Hans}
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
                        onValuesChange={setNodeChange}
                        initialValues={(node.data as any)?.form || {}}
                    >
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
                                    return <ProFormDigit {...baseProps} />;
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
                            }
                        })}

                        <div className="h-80"></div>
                    </ProForm>
                )}
            </div>
        </>
    );
});
