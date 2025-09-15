/*
 * @LastEditors: biz
 */
import { getNodeConfirmUserList, getWorkFlowStartCondition, runWorkFlow, getWorkflowScheduledTask, createWorkflowScheduledTask, updateWorkflowScheduledTask, deleteWorkflowScheduledTask } from '@/api/workflow';
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
import RunForm from './components/RunForm';
import { UploadDragger } from './components/Form/Upload';
const { error } = message;
export default memo(() => {
    const intl = useIntl();
    const appId = useUserStore(state => state.appId);
    const setRunId = useUserStore(state => state.setRunId);
    const [messageApi, contextHolder] = message.useMessage();
    const [visible, setVisible] = useState(false);
    const [existingTask, setExistingTask] = useState<any>(null);
    const parent = useRef(null);
    useEffect(() => {
        parent.current && autoAnimate(parent.current);
    }, [parent]);
    const { data, loading, run } = useRequest(getWorkFlowStartCondition, {
        manual: true,
    });
    const [submitLoading, setSubmitLoading] = useState(false);

    // Extract workflowId from data
    const workflowId = data?.data?.workflow_id;

    useUpdateEffect(() => {
        appId && run(appId);
    }, [appId]);
    
    const onClose = () => {
        setVisible(false);
        setRunId(null);
    };

    const confirm = async (formData: any) => {
        console.log(formData);
        const { description, ...input } = formData;
        const inputs = data?.data?.start_node?.data?.input;
        const node_confirm_users = {};

        Object.entries(input)
            .filter(([key, value]) => {
                if (inputs?.properties?.[key]) {
                    if(inputs.properties[key].type === 'file'){
                        inputs.properties[key].value = value[0]?.response?.data?.file_id||''
                    }else{
                        inputs.properties[key].value = value;
                    }
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
        try {
            const res = await runWorkFlow(appId, submitData);
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
        } catch (err) {
            console.log(err);
            setSubmitLoading(false);
            // messageApi.error(
            //     intl.formatMessage({
            //         id: 'workflow.message.runFailure',
            //         defaultMessage: '',
            //     }),
            // );
        }
    };

    const handleScheduleExecute = async (scheduleData: any, formData: any) => {
        console.log('Schedule execution:', scheduleData, formData);
        
        // Process form data similar to confirm function
        const { description, ...input } = formData;
        const inputs = data?.data?.start_node?.data?.input;
        const node_confirm_users = {};

        Object.entries(input)
            .filter(([key, value]) => {
                if (inputs?.properties?.[key]) {
                    if(inputs.properties[key].type === 'file'){
                        inputs.properties[key].value = value[0]?.response?.data?.file_id||''
                    }else{
                        inputs.properties[key].value = value;
                    }
                    return false;
                }
                return true;
            })
            .forEach(([key, value]) => {
                node_confirm_users[key] = value;
            });

        const submitData = {
            name: scheduleData.name || `Workflow ${workflowId} Schedule`,
            task_type: scheduleData.task_type || 'one_time',
            app_id: appId,
            workflow_id: workflowId,
            input: inputs,
            start_time: scheduleData.start_time,
            node_confirm_users,
            task_data: {
                schedule_type: scheduleData.schedule_type || 'single',
                created_from: 'workflow_ui'
            },
            ...(scheduleData.task_type === 'recurring' && {
                repeat_type: scheduleData.repeat_type,
                repeat_interval: scheduleData.repeat_interval,
                ...(scheduleData.end_time && {
                    end_time: scheduleData.end_time
                })
            })
        };

        try {
            let response;
            if (existingTask && existingTask.id) {
                // Update existing task
                response = await updateWorkflowScheduledTask(existingTask.id, submitData);
            } else {
                // Create new task
                response = await createWorkflowScheduledTask(submitData);
            }
            
            if (response.code === 0) {
                messageApi.success(response.data.message);
                
                // Update existing task state
                if (response.data && response.data.task_id) {
                    setExistingTask({
                        id: response.data.task_id,
                        ...submitData
                    });
                }
                
                setTimeout(() => {
                    onClose();
                }, 1000);
            } else {
                throw new Error(response?.detail || 'Schedule operation failed');
            }
        } catch (error) {
            console.error('Schedule execution failed:', error);
            messageApi.error(
                intl.formatMessage({
                    id: 'workflow.message.scheduleFailure', 
                    defaultMessage: 'Failed to create schedule',
                }),
            );
        }
    };

    const handleCancelSchedule = async (taskId: number) => {
        try {
            const response = await deleteWorkflowScheduledTask(taskId);
            if (response.code === 0) {
                messageApi.success(response.data.message);
                setExistingTask(null);
            } else {
                throw new Error(response?.detail || 'Cancel operation failed');
            }
        } catch (error) {
            console.error('Cancel schedule failed:', error);
            messageApi.error(
                intl.formatMessage({
                    id: 'workflow.message.cancelScheduleFailure',
                    defaultMessage: 'Failed to cancel schedule',
                }),
            );
        }
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
                    <RunForm 
                        loading={submitLoading}
                        onFinish={confirm}
                        onScheduleExecute={handleScheduleExecute}
                        onCancelSchedule={handleCancelSchedule}
                        data={data}
                        appId={appId}
                        workflowId={workflowId ? Number(workflowId) : undefined}
                    />
                </ProCard>
            ) : null}
        </div>
    );
});
