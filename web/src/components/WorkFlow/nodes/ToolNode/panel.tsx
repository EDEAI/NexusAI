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
import { memo, useRef, useState, useEffect, useCallback } from 'react';
import { debounce } from 'lodash';
import useStore from '../../store';
import { AppNode } from '../../types';
import ProFormWrapperEditor from '../../components/Editor/ProFormWrapperEditor';

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

export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    const [params, setParams] = useState<any>([]);
    const [authorizationStatus, setAuthorizationStatus] = useState<any>(1);
    const [credentialsProvider, setCredentialsProvider] = useState<Record<string, CredentialsProviderItem> | null>(null);
    const [editorOptions, setEditorOptions] = useState([]);
    const [loading, setLoading] = useState(false);

    const updateNodeDataRef = useRef(updateNodeData);
    const nodeIdRef = useRef(node.id);
    const loadingRef = useRef(loading);

    // 保持引用最新
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
                .filter(x => nodeData['form']?.[x])
                .forEach(e => {
                    formRef.current.setFieldsValue({ [e]: nodeData['form']?.[e] });
                });
            setLoading(false);
        }, 200);
    });

    useUpdateEffect(() => {
        setLoading(true);
        const vars = getVariables(node.id);
        setEditorOptions(vars);
        
        // 更新表单值
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
        [], // 空依赖数组，避免重新创建debounce函数
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
                            if (!e.required) return null;

                            switch (e.type) {
                                case 'object':
                                case 'json':
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
                    </ProForm>
                )}
            </div>
        </>
    );
});
