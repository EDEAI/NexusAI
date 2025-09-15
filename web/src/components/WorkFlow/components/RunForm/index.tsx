/*
 * @LastEditors: biz
 */
import { ProForm } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { memo, useState, useEffect } from 'react';
import { getWorkflowScheduledTask } from '@/api/workflow';
import { Button, Space, message } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { TextareaRunName } from '../Form/Input';
import { RenderConfirm } from './RenderConfirm';
import { RenderInput } from './RenderInput';
import ScheduleModal from '../ScheduleModal';

interface RunFormProps {
    loading?: boolean;
    onFinish: (values: any) => Promise<void>;
    data?: any;
    onScheduleExecute?: (scheduleData: any, formData: any) => void;
    onCancelSchedule?: (taskId: number) => void;
    appId?: number;
    workflowId?: number;
}

const RunForm = memo(({ loading, onFinish, data, onScheduleExecute, onCancelSchedule, appId, workflowId }: RunFormProps) => {
    const intl = useIntl();
    const [scheduleModalVisible, setScheduleModalVisible] = useState(false);
    const [scheduleLoading, setScheduleLoading] = useState(false);
    const [existingTask, setExistingTask] = useState<any>(null);
    const [hasScheduledTask, setHasScheduledTask] = useState(false);
    const [checkingSchedule, setCheckingSchedule] = useState(false);
    const [formRef] = ProForm.useForm();

    const handleScheduleClick = async () => {
        try {
            // If there's an existing scheduled task, open modal directly without validation
            if (hasScheduledTask) {
                setScheduleModalVisible(true);
                return;
            }
            
            // For new schedule, validate form first
            await formRef.validateFields();
            
            // No need to fetch existing task here, let ScheduleModal handle it
            setScheduleModalVisible(true);
        } catch (e) {
            // Show a gentle warning; the form will highlight invalid fields
            message.warning(intl.formatMessage({ id: 'workflow.isRequire', defaultMessage: 'This field is required' }));
        }
    };

    const handleScheduleConfirm = async (scheduleData: any) => {
        try {
            setScheduleLoading(true);
            // ScheduleModal already handles the API call, just close the modal
            setScheduleModalVisible(false);
            // Update local flags so the button switches to "View Schedule Plan"
            if (scheduleData && typeof scheduleData === 'object') {
                setHasScheduledTask(true);
                if ((scheduleData as any).id) {
                    setExistingTask(scheduleData);
                }
            }
        } catch (error) {
            console.error('Schedule execution failed:', error);
        } finally {
            setScheduleLoading(false);
        }
    };

    const handleCancelSchedule = () => {
        if (existingTask && existingTask.id && onCancelSchedule) {
            onCancelSchedule(existingTask.id);
            setExistingTask(null);
            setHasScheduledTask(false);
        }
        setScheduleModalVisible(false);
    };

    const handleExistingTaskChange = (task: any) => {
        setExistingTask(task);
        const ok = task && Object.keys(task || {}).length > 0;
        setHasScheduledTask(!!ok);
    };

    // Check for existing scheduled task on component mount
    useEffect(() => {
        const checkScheduledTask = async () => {
            if (appId && workflowId) {
                try {
                    setCheckingSchedule(true);
                    const response = await getWorkflowScheduledTask(appId, workflowId);
                    const hasTask = response && response.code === 0 && response.data && Object.keys(response.data || {}).length > 0;
                    if (hasTask) {
                        setHasScheduledTask(true);
                        setExistingTask(response.data);
                    } else {
                        setHasScheduledTask(false);
                        setExistingTask(null);
                    }
                } catch (error) {
                    console.error('Failed to check scheduled task:', error);
                    setHasScheduledTask(false);
                    setExistingTask(null);
                } finally {
                    setCheckingSchedule(false);
                }
            } else {
                setCheckingSchedule(false);
            }
        };

        // Always check scheduled task when appId or workflowId changes
        if (appId && workflowId) {
            checkScheduledTask();
        }
    }, [appId, workflowId]);

    // Process form data to extract inputs and node_confirm_users
    const processFormData = (formData?: any) => {
        const actualFormData = formData || formRef.getFieldsValue();
        const { description, ...input } = actualFormData;
        const inputs = data?.data?.start_node?.data?.input;
        const node_confirm_users = {};

        if (inputs?.properties) {
            Object.entries(input)
                .filter(([key, value]) => {
                    if (inputs.properties[key]) {
                        if (inputs.properties[key].type === 'file') {
                            inputs.properties[key].value = value?.[0]?.response?.data?.file_id || '';
                        } else {
                            inputs.properties[key].value = value;
                        }
                        return false;
                    }
                    return true;
                })
                .forEach(([key, value]) => {
                    node_confirm_users[key] = value;
                });
        }

        return {
            inputs,
            node_confirm_users,
        };
    };

    // Build workflow inputs for ScheduleModal
    const buildWorkflowInputs = () => {
        const formValues = formRef.getFieldsValue();
        const { inputs } = processFormData(formValues);
        return {
            input: inputs,
            run_name: formValues.description || 'Scheduled Workflow Run',
        };
    };

    const handleScheduleCancel = () => {
        setScheduleModalVisible(false);
    };

    return (
        <>
            <ProForm
                form={formRef}
                submitter={{
                    resetButtonProps: false,
                    render: (props, dom) => {
                        return (
                            <Space direction="vertical" className="w-full" size="middle">
                                {/* Normal Run Button */}
                                <Button
                                    type="primary"
                                    loading={loading}
                                    onClick={() => props.form?.submit()}
                                    className="w-full"
                                    size="large"
                                >
                                    {intl.formatMessage({ id: 'workflow.button.run' })}
                                </Button>
                                
                                {/* Schedule Execute Button */}
                                <Button
                                    type={hasScheduledTask ? "primary" : "default"}
                                    icon={<ClockCircleOutlined />}
                                    onClick={handleScheduleClick}
                                    loading={scheduleLoading || checkingSchedule}
                                    ghost={hasScheduledTask}
                                    className="w-full border border-blue-400 text-blue-600 hover:border-blue-500 hover:text-blue-700"
                                    size="large"
                                >
                                    {hasScheduledTask
                                        ? intl.formatMessage({ id: 'workflow.viewSchedulePlan' })
                                        : intl.formatMessage({ id: 'workflow.scheduleExecution' })}
                                </Button>
                            </Space>
                        );
                    },
                }}
                loading={loading}
                onFinish={onFinish}
            >
                <TextareaRunName name={'description'} />
                <RenderInput data={data?.data?.start_node?.data?.input?.properties} />
                <RenderConfirm data={data?.data?.need_confirm_nodes} />
            </ProForm>

            {/* Schedule Modal */}
            <ScheduleModal
                visible={scheduleModalVisible}
                onCancel={() => setScheduleModalVisible(false)}
                onConfirm={handleScheduleConfirm}
                onCancelSchedule={handleCancelSchedule}
                onExistingTaskChange={handleExistingTaskChange}
                loading={scheduleLoading}
                appId={appId}
                workflowId={workflowId}
                workflowInputs={buildWorkflowInputs}
                nodeConfirmUsers={(() => {
                    try {
                        const { node_confirm_users } = processFormData();
                        return node_confirm_users;
                    } catch (e) {
                        return {};
                    }
                })()}
                existingTask={existingTask}
            />
        </>
    );
});

export default RunForm;
