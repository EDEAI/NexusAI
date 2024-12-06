/*
 * @LastEditors: biz
 */
import { getNodeConfirmUserList, getWorkFlowStartCondition, runWorkFlow } from '@/api/workflow';
import useUserStore from '@/store/user';
import { CloseOutlined } from '@ant-design/icons';
import {
    ProCard,
    ProForm,
    ProFormDigit,
    ProFormSelect,
    ProFormTextArea,
} from '@ant-design/pro-components';
import autoAnimate from '@formkit/auto-animate';
import { useIntl } from '@umijs/max';
import { useRequest, useUpdateEffect } from 'ahooks';
import { Button, Typography, message } from 'antd';
import _ from 'lodash';
import { memo, useEffect, useRef, useState } from 'react';
import { TextareaRunName } from './components/Form/Input';
const { error } = message;
export default memo(() => {
    const intl = useIntl();
    const appId = useUserStore(state => state.appId);
    const setRunId = useUserStore(state => state.setRunId);
    const [messageApi, contextHolder] = message.useMessage();
    const [visible, setVisible] = useState(false);
    const parent = useRef(null);
    useEffect(() => {
        parent.current && autoAnimate(parent.current);
    }, [parent]);
    const { data, loading, run } = useRequest(getWorkFlowStartCondition, {
        manual: true,
    });
    const [submitLoading, setSubmitLoading] = useState(false);

    useUpdateEffect(() => {
        appId && run(appId);
    }, [appId]);
    const onClose = () => {
        setVisible(false);
        setRunId(null);
    };

    const RenderInput = () => {
        const inputs = data?.data?.start_node?.data?.input?.properties;
        if (!inputs || _.isEmpty(inputs)) return null;
        return (
            <div>
                <Typography.Title level={5}>
                    {intl.formatMessage({
                        id: 'workflow.title.inputParameters',
                        defaultMessage: '',
                    })}
                </Typography.Title>
                {Object.values(inputs).map((val: any) => {
                    if (val.type === 'number') {
                        return (
                            <ProFormDigit
                                key={val.name}
                                required={val.required}
                                name={val.name}
                                rules={[
                                    {
                                        required: val.required,
                                        message: intl.formatMessage({
                                            id: 'workflow.message.enterProcessDescription',
                                            defaultMessage: '',
                                        }),
                                    },
                                ]}
                                label={val.name}
                            ></ProFormDigit>
                        );
                    }
                    return (
                        <ProFormTextArea
                            key={val.name}
                            required={val.required}
                            rules={[
                                {
                                    required: val.required,
                                    message: intl.formatMessage({
                                        id: 'workflow.message.enterProcessDescription',
                                        defaultMessage: '',
                                    }),
                                },
                            ]}
                            name={val.name}
                            label={val.name}
                        ></ProFormTextArea>
                    );
                })}
            </div>
        );
    };
    const RenderConfirm = () => {
        const inputs = data?.data?.need_confirm_nodes;
        if (!inputs || !inputs.length) return null;
        return (
            <div>
                <Typography.Title level={5}>
                    {intl.formatMessage({
                        id: 'workflow.label.human',
                        defaultMessage: '',
                    })}
                </Typography.Title>
                {inputs.map((val: any) => {
                    return (
                        <ProFormSelect
                            tooltip={intl.formatMessage({
                                id: 'workflow.tooltip.selectDataConfirmer',
                                defaultMessage: '',
                            })}
                            key={val.node_id}
                            label={val.node_name}
                            name={val.node_id}
                            mode="multiple"
                            required={true}
                            rules={[
                                {
                                    required: true,
                                    message: intl.formatMessage({
                                        id: 'workflow.message.selectDataConfirmer',
                                        defaultMessage: '',
                                    }),
                                },
                            ]}
                            request={async () => {
                                const res = await getNodeConfirmUserList();
                                return res.data.team_member_list
                                    .filter((item: any) => item.user_id && item.nickname)
                                    .map((item: any) => ({
                                        label: item.nickname,
                                        value: item.user_id,
                                    }));
                            }}
                        ></ProFormSelect>
                    );
                })}
            </div>
        );
    };
    const confirm = (formData: any) => {
        console.log(formData);
        const { description, ...input } = formData;
        const inputs = data?.data?.start_node?.data?.input;
        const node_confirm_users = {};

        Object.entries(input)
            .filter(([key, value]) => {
                if (inputs?.properties?.[key]) {
                    inputs.properties[key].value = value;
                    return false;
                }
                return true;
            })
            .forEach(([key, value]) => {
                node_confirm_users[key] = value;
            });

        const submitData = {
            run_name: description,
            run_type: 1,
            inputs: inputs,
            node_confirm_users,
        };
        console.log(submitData);
        setSubmitLoading(true);
        runWorkFlow(appId, submitData)
            .then(res => {
                console.log(res);
                setSubmitLoading(false);
                messageApi.success(
                    intl.formatMessage({
                        id: 'workflow.message.runSuccess',
                        defaultMessage: '',
                    }),
                );
                setTimeout(() => {
                    onClose();
                }, 1000);
            })
            .catch(err => {
                console.log(err);
                setSubmitLoading(false);
                // messageApi.error(
                //     intl.formatMessage({
                //         id: 'workflow.message.runFailure',
                //         defaultMessage: '',
                //     }),
                // );
            });
    };
    return (
        <div ref={parent} className="fixed z-20">
            {appId ? (
                <ProCard
                    className="w-[400px] border  border-blue-300 fixed z-20  top-[65px] right-2 "
                    style={{ height: 'calc(100vh - 10px - 75px)' }}
                    title={
                        <Typography.Title level={5}>
                            {intl.formatMessage({
                                id: 'workflow.title.runWorkflow',
                                defaultMessage: '',
                            })}
                        </Typography.Title>
                    }
                    extra={
                        <Button
                            type="text"
                            onClick={onClose}
                            icon={<CloseOutlined></CloseOutlined>}
                        ></Button>
                    }
                    bodyStyle={{
                        overflowY: 'auto',
                    }}
                    loading={loading}
                >
                    {contextHolder}
                    <ProForm
                        submitter={{
                            resetButtonProps: false,
                            submitButtonProps: {
                                className: 'w-full',
                            },
                            searchConfig: {
                                submitText: intl.formatMessage({
                                    id: 'workflow.button.run',
                                    defaultMessage: '',
                                }),
                            },
                        }}
                        loading={submitLoading}
                        onFinish={confirm}
                    >
                        <TextareaRunName name={'description'}></TextareaRunName>

                        <RenderInput></RenderInput>
                        <RenderConfirm></RenderConfirm>
                    </ProForm>
                </ProCard>
            ) : null}
        </div>
    );
});
