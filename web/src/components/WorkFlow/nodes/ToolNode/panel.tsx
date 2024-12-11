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
    ProFormTextArea,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import Link from 'antd/lib/typography/Link';
import { memo, useRef, useState } from 'react';
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

const transformSelectOptions = options => {
    return options.map(group => {
        return {
            label: <span>{group.label}</span>,
            title: group.value,
            options:
                group.options?.map(item => ({
                    label: <span>{item.label}</span>,
                    value: item.value,
                })) || [],
        };
    });
};

export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const updateNodeData = useStore(state => state.updateNodeData);
    const [params, setParams] = useState<any>([]);
    const [authorizationStatus, setAuthorizationStatus] = useState<any>(1);
    const [credentialsProvider, setCredentialsProvider] = useState<any>(null);

    useMount(() => {
        setParams(node.data?.baseData?.parameters || []);
        setAuthorizationStatus(node.data?.baseData?.authorization_status || 1);
        setCredentialsProvider(node.data?.baseData?.credentials_for_provider || null);
        setTimeout(() => {
            const fieldNames = Object.keys(formRef?.current?.getFieldsValue() || {});
            // console.log(1111, node, fieldNames);
            if (!fieldNames?.length) return;
            fieldNames
                .filter(x => node.data['form']?.[x])
                .forEach(e => {
                    formRef.current.setFieldsValue({ [e]: node.data['form']?.[e] });
                });
        }, 200);
    });

    useUpdateEffect(() => {}, [node.id]);

    const setNodeChange = (addItem: { [key: string]: any }, allValue) => {
        console.log(allValue);
        updateNodeData(node.id, {
            form: allValue,
        });
    };

    //
    const getToolAuthorization = async e => {
        const res = await getToolAuthorizationStatus(node.data?.baseData?.groupName, e);
        if (res?.code == 0) {
            setAuthorizationStatus(1);
            updateNodeData(node.id, {
                baseData: {
                    ...node.data?.baseData,
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
                            Object.values(credentialsProvider).map(e => {
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
                                    return <ProFormTextArea {...baseProps} />;
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
