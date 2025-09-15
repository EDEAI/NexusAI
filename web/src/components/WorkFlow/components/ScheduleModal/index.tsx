import React, { useState, useEffect, useRef } from 'react';
import { Modal, Form, Radio, DatePicker, InputNumber, Select, Button, Space, message, Typography } from 'antd';
import { useIntl } from '@umijs/max';
import { getWorkflowScheduledTask, createWorkflowScheduledTask, updateWorkflowScheduledTask } from '@/api/workflow';
import dayjs from 'dayjs';

interface ScheduleModalProps {
    visible: boolean;
    onCancel: () => void;
    onConfirm: (scheduleData: any) => void;
    onCancelSchedule?: (taskId: number) => void;
    onExistingTaskChange?: (task: any) => void;
    loading?: boolean;
    appId?: number;
    workflowId?: number;
    // Add workflow run parameters
    workflowInputs?: any | (() => Promise<any>);
    nodeConfirmUsers?: any;
    // Pass existing task data to avoid duplicate API calls
    existingTask?: any;
}

const ScheduleModal: React.FC<ScheduleModalProps> = ({
    visible,
    onCancel,
    onConfirm,
    onCancelSchedule,
    onExistingTaskChange,
    loading = false,
    appId,
    workflowId,
    workflowInputs,
    nodeConfirmUsers,
    existingTask: propExistingTask
}) => {
    const intl = useIntl();
    const [form] = Form.useForm();
    const [scheduleType, setScheduleType] = useState<'single' | 'repeat'>('single');
    const [endCondition, setEndCondition] = useState<'never' | 'endTime'>('never');
    const [repeatDimension, setRepeatDimension] = useState<string>('day');
    const [existingTask, setExistingTask] = useState<any>(null);
    const [fetchLoading, setFetchLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const submittingRef = useRef(false);

    // Handle existing task data when modal opens
    useEffect(() => {
        if (visible) {
            // If existingTask is passed as prop, use it immediately for faster UI feedback
            if (propExistingTask) {
                setExistingTask(propExistingTask);
                fillFormWithTaskData(propExistingTask);
            } else {
                // Set default values when no existing task
                form.setFieldsValue({
                    startTime: dayjs(),
                });
            }
        }
    }, [visible, propExistingTask]);

    // Always fetch latest task data from server when modal opens (and when ids change)
    useEffect(() => {
        if (visible && appId && workflowId) {
            fetchExistingTask();
        }
    }, [visible, appId, workflowId]);

    // Fill form with task data
    const fillFormWithTaskData = (task: any) => {
        if (!task) {
            form.setFieldsValue({
                scheduleType: 'single',
                startTime: dayjs(),
                endCondition: 'never',
            });
            return;
        }

        const taskType = task.task_type === 'one_time' ? 'single' : 'repeat';
        setScheduleType(taskType);
        
        const formValues: any = {
            scheduleType: taskType,
            startTime: dayjs(task.start_time),
        };
        
        if (taskType === 'repeat') {
            formValues.repeatDimension = task.repeat_type;
            formValues.repeatInterval = task.repeat_interval;
            setRepeatDimension(task.repeat_type || 'day');
            
            if (task.end_time) {
                setEndCondition('endTime');
                formValues.endCondition = 'endTime';
                formValues.endTime = dayjs(task.end_time);
            } else {
                setEndCondition('never');
                formValues.endCondition = 'never';
            }
        }
        
        form.setFieldsValue(formValues);
    };

    const fetchExistingTask = async () => {
        if (!appId || !workflowId) return;
        
        setFetchLoading(true);
        try {
            const response = await getWorkflowScheduledTask(appId, workflowId);
            // Backend success code is 0, and data is {} when no task
            if (response.code === 0 && response.data && Object.keys(response.data || {}).length > 0) {
                const task = response.data;
                setExistingTask(task);
                onExistingTaskChange?.(task); // Notify parent component
                fillFormWithTaskData(task);
            } else {
                // No existing task found from server, ensure local state is empty
                setExistingTask(null);
                onExistingTaskChange?.(null); // Notify parent component
                fillFormWithTaskData(null);
            }
        } catch (error) {
            console.error('Failed to fetch existing scheduled task:', error);
        } finally {
            setFetchLoading(false);
        }
    };

    const handleScheduleTypeChange = (e: any) => {
        setScheduleType(e.target.value);
        // Reset form fields when schedule type changes
        form.resetFields(['repeatDimension', 'repeatInterval', 'endCondition', 'endTime']);
        setEndCondition('never');
        setRepeatDimension('day'); // Reset to default
    };

    const handleRepeatDimensionChange = (value: string) => {
        setRepeatDimension(value);
    };

    const handleEndConditionChange = (value: string) => {
        setEndCondition(value as 'never' | 'endTime');
        if (value === 'never') {
            form.setFieldValue('endTime', undefined);
        }
    };

    const handleConfirm = async () => {
        // Synchronous guard to prevent rapid double-clicks
        if (submittingRef.current) return;
        submittingRef.current = true;
        setSubmitting(true);
        try {
             const values = await form.validateFields();
             
             // Build input data and run_name: if function, call it
             let inputData: any = {};
             let scheduleRunName: string = '';
             try {
                 if (typeof workflowInputs === 'function') {
                     const built: any = await workflowInputs();
                     if (built && typeof built === 'object' && 'input' in built) {
                         inputData = built.input;
                         scheduleRunName = built.run_name || '';
                     } else {
                         inputData = built || {};
                     }
                 } else if (workflowInputs && typeof workflowInputs === 'object') {
                     inputData = workflowInputs;
                 } else if (existingTask && typeof existingTask.input === 'object') {
                     inputData = existingTask.input;
                 } else {
                     inputData = {};
                 }
             } catch (e) {
                 console.error('Failed to build workflow inputs for schedule:', e);
                 inputData = (existingTask && typeof existingTask.input === 'object') ? existingTask.input : {};
             }
             
             // Prefer using run name from form as schedule task name if provided
             const taskName = (existingTask && existingTask.id)
             ? (existingTask.name || `Workflow ${workflowId} Schedule - ${dayjs().format('YYYY-MM-DD HH:mm:ss')}`)
             : (scheduleRunName
             ? scheduleRunName
             : `Workflow ${workflowId} Schedule - ${dayjs().format('YYYY-MM-DD HH:mm:ss')}`);
             
             // Build schedule data with all required fields for backend API
             const scheduleData = {
                 // Required fields for backend API
                 name: taskName,
                 task_type: scheduleType === 'single' ? 'one_time' : 'recurring',
                 app_id: appId,
                 workflow_id: workflowId,
                 input: (existingTask && existingTask.id) ? (existingTask.input || {}) : inputData, // Keep original input when editing
                 start_time: values.startTime.format('YYYY-MM-DD HH:mm:ss'),
                 task_data: {
                     schedule_type: scheduleType,
                     created_from: 'workflow_ui'
                 },
                 // Move node_confirm_users as independent field
                 node_confirm_users: (existingTask && existingTask.id) ? (existingTask.node_confirm_users || {}) : (nodeConfirmUsers || {}),
                 
                 // Optional fields based on schedule type
                 ...(scheduleType === 'repeat' && {
                     repeat_type: values.repeatDimension || 'day',
                     repeat_interval: values.repeatInterval || 1,
                     ...(endCondition === 'endTime' && {
                         end_time: values.endTime.format('YYYY-MM-DD HH:mm:ss')
                     })
                 })
             } as any;
             
             let response;
             if (existingTask && existingTask.id) {
                 // Update existing task - only send changed fields
                 const updateData = {
                   // Keep original name and input and node_confirm_users when editing
                   name: existingTask.name,
                   task_type: scheduleData.task_type,
                   input: existingTask.input,
                   start_time: scheduleData.start_time,
                   task_data: {
                       schedule_type: scheduleType,
                       created_from: 'workflow_ui'
                   },
                   node_confirm_users: existingTask.node_confirm_users || {},
                   ...(scheduleType === 'repeat' && {
                       repeat_type: scheduleData.repeat_type,
                       repeat_interval: scheduleData.repeat_interval,
                       // Always include end_time field for repeat tasks to handle clearing
                       end_time: endCondition === 'endTime' ? scheduleData.end_time : null
                   }),
                   // For single tasks, explicitly clear end_time if it existed before
                   ...(scheduleType === 'single' && existingTask.end_time && {
                       end_time: null
                   })
               };
                 response = await updateWorkflowScheduledTask(existingTask.id, updateData);
             } else {
                 // Create new task
                 response = await createWorkflowScheduledTask(scheduleData);
             }
             
             if (response.code === 0) {
                 message.success(response.data.message);
                 
                 // Build task object and propagate to parent so it can update UI state
                 let taskObj = (existingTask && existingTask.id)
                   ? {
                       ...existingTask,
                       // Preserve original fields per requirement
                       name: existingTask.name,
                       input: existingTask.input,
                       node_confirm_users: existingTask.node_confirm_users,
                       // Update only scheduling-related fields
                       task_type: scheduleData.task_type,
                       start_time: scheduleData.start_time,
                       ...(scheduleType === 'repeat' && {
                         repeat_type: scheduleData.repeat_type,
                         repeat_interval: scheduleData.repeat_interval,
                         ...(endCondition === 'endTime' && { end_time: scheduleData.end_time })
                       }),
                       task_data: { ...(existingTask.task_data || {}), schedule_type: scheduleType, created_from: 'workflow_ui' }
                     }
                   : null;
                 // If creating new task, save the returned task_id to local state and compose task object
                 if ((!existingTask || !existingTask.id) && response.data && response.data.task_id) {
                     taskObj = {
                         id: response.data.task_id,
                         ...scheduleData
                     } as any;
                     setExistingTask(taskObj);
                 } else if (existingTask && existingTask.id) {
                     setExistingTask(taskObj);
                 }
                 
                 // Notify parent about the current existing task so it can toggle hasScheduledTask
                 if (taskObj) {
                     onExistingTaskChange?.(taskObj);
                 }
                 
                 // Keep existing behavior: notify confirm callback with the latest task object if available
                 onConfirm(taskObj || scheduleData);
             } else {
                 message.error(response?.detail || response?.response?.data?.detail || 'Operation failed');
             }
        } catch (error) {
             console.error('Schedule operation failed:', error);
        } finally {
             submittingRef.current = false;
             setSubmitting(false);
        }
    };

    const handleCancel = () => {
        form.resetFields();
        setScheduleType('single');
        setEndCondition('never');
        // Don't clear existingTask here - we want to keep the task info for future operations
        onCancel();
    };

    const handleCancelSchedule = async () => {
        if (!existingTask) return;
        
        Modal.confirm({
            title: intl.formatMessage({ id: 'workflow.confirmCancelSchedule', defaultMessage: 'Confirm Cancel Schedule' }),
            content: intl.formatMessage({ id: 'workflow.confirmCancelScheduleContent', defaultMessage: 'Are you sure you want to cancel the current schedule? This action cannot be undone.' }),
            centered: true,
            onOk: async () => {
                if (onCancelSchedule) {
                    await onCancelSchedule(existingTask.id);
                    handleCancel();
                } else {
                    message.warning(intl.formatMessage({ id: 'workflow.cancelHandlerMissing', defaultMessage: 'Cancel handler not provided' }));
                }
            },
            onCancel: () => {
                // User cancelled the confirmation, do nothing
            }
        });
    };

    const repeatDimensionOptions = [
        { label: intl.formatMessage({ id: 'workflow.minute' }), value: 'minute' },
        { label: intl.formatMessage({ id: 'workflow.hour' }), value: 'hour' },
        { label: intl.formatMessage({ id: 'workflow.day' }), value: 'day' },
        { label: intl.formatMessage({ id: 'workflow.week' }), value: 'week' },
        { label: intl.formatMessage({ id: 'workflow.month' }), value: 'month' },
        { label: intl.formatMessage({ id: 'workflow.year' }), value: 'year' },
    ];

    const endConditionOptions = [
        { label: intl.formatMessage({ id: 'workflow.noEnd' }), value: 'never' },
        { label: intl.formatMessage({ id: 'workflow.setEndTime' }), value: 'endTime' },
    ];

    // Disable past dates and times
    const disabledDate = (current: any) => {
        return current && current < dayjs().startOf('day');
    };

    const disabledTime = (current: any) => {
        if (!current) return {};
        
        const now = dayjs();
        if (current.isSame(now, 'day')) {
            return {
                disabledHours: () => {
                    const hours = [];
                    for (let i = 0; i < now.hour(); i++) {
                        hours.push(i);
                    }
                    return hours;
                },
                disabledMinutes: (selectedHour: number) => {
                    if (selectedHour === now.hour()) {
                        const minutes = [];
                        for (let i = 0; i <= now.minute(); i++) {
                            minutes.push(i);
                        }
                        return minutes;
                    }
                    return [];
                },
            };
        }
        return {};
    };

    return (
        <Modal
            title={intl.formatMessage({ id: 'workflow.scheduleExecutionTitle' })}
            open={visible}
            onCancel={handleCancel}
            footer={null}
            width={600}
            destroyOnClose
            confirmLoading={fetchLoading}
        >
            <Form
                form={form}
                layout="vertical"
                initialValues={{
                    scheduleType: 'single',
                    repeatInterval: 1,
                    repeatDimension: 'day',
                    endCondition: 'never'
                }}
            >
                {existingTask && (
                    <>
                        <Form.Item
                            label={intl.formatMessage({ id: 'workflow.scheduleName', defaultMessage: 'Plan Name' })}
                        >
                            <div style={{ padding: '4px 0', color: '#595959' }}>
                                {existingTask?.name || '-'}
                            </div>
                        </Form.Item>
                        
                        <Form.Item
                            label={intl.formatMessage({ id: 'workflow.title.inputParameters', defaultMessage: 'Input Parameters' })}
                        >
                            <div style={{ padding: '4px 0', color: '#595959' }}>
                                {(() => {
                                    // Render read-only input parameters
                                    const renderReadOnlyInputs = (input: any) => {
                                        // Show empty state when no input
                                        if (!input) {
                                            return intl.formatMessage({ id: 'workflow.emptyInput', defaultMessage: 'No input' });
                                        }
                                        const props = input?.properties || input;
                                        const items = Object.values(props || {});
                                        if (!items.length) {
                                            return intl.formatMessage({ id: 'workflow.emptyInput', defaultMessage: 'No input' });
                                        }
                                        return (
                                            <div>
                                                {items.map((item: any) => {
                                                    const label = item.display_name || item.name;
                                                    const key = item.name || label;
                                                    const type = item.type;
                                                    const value = item.value;

                                                    if (type === 'json') {
                                                        let str = '';
                                                        try {
                                                            str = typeof value === 'string' ? value : JSON.stringify(value ?? {}, null, 2);
                                                        } catch (e) {
                                                            str = String(value ?? '');
                                                        }
                                                        return (
                                                            <div key={key} style={{ marginBottom: 10 }}>
                                                                <div style={{ marginBottom: 8, fontWeight: 400 }}>{label}</div>
                                                                <pre style={{ 
                                                                    padding: '4px 11px', 
                                                                    fontSize: '13px', 
                                                                    lineHeight: 1.5, 
                                                                    backgroundColor: '#f5f5f5', 
                                                                    borderRadius: 4, 
                                                                    overflow: 'auto', 
                                                                    maxHeight: 240, 
                                                                    whiteSpace: 'pre-wrap', 
                                                                    wordBreak: 'break-word',
                                                                    margin: 0
                                                                }}>{str || '-'}</pre>
                                                            </div>
                                                        );
                                                    }

                                                    return (
                                                        <div key={key} style={{ marginBottom: 10 }}>
                                                            <div style={{ marginBottom: 8, fontWeight: 400 }}>{label}</div>
                                                            <div style={{ padding: '4px 11px', fontSize: '14px', lineHeight: 1.5 }}>{value ?? '-'}</div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        );
                                    };

                                    return renderReadOnlyInputs(existingTask?.input);
                                })()} 
                            </div>
                        </Form.Item>
                    </>
                )}

                {/* Schedule Type */}
                <Form.Item
                    label={intl.formatMessage({ id: 'workflow.scheduleType' })}
                    name="scheduleType"
                    rules={[{ required: true }]}
                >
                    <Radio.Group onChange={handleScheduleTypeChange} value={scheduleType}>
                        <Radio value="single">
                            {intl.formatMessage({ id: 'workflow.singleRun' })}
                        </Radio>
                        <Radio value="repeat">
                            {intl.formatMessage({ id: 'workflow.repeatRun' })}
                        </Radio>
                    </Radio.Group>
                </Form.Item>

                {/* Start Time */}
                <Form.Item
                    label={intl.formatMessage({ id: 'workflow.startTime' })}
                    name="startTime"
                    rules={[
                        { required: true, message: intl.formatMessage({ id: 'workflow.pleaseSelectStartTime' }) }
                    ]}
                >
                    <DatePicker
                        showTime={{ format: 'HH:mm' }}
                        format="YYYY-MM-DD HH:mm"
                        placeholder={intl.formatMessage({ id: 'workflow.pleaseSelectStartTime' })}
                        disabledDate={disabledDate}
                        disabledTime={disabledTime}
                        style={{ width: '100%' }}
                    />
                </Form.Item>

                {/* Repeat Settings - Only show when repeat is selected */}
                {scheduleType === 'repeat' && (
                    <>
                        {/* Repeat Dimension */}
                        <Form.Item
                            label={intl.formatMessage({ id: 'workflow.repeatDimension' })}
                            name="repeatDimension"
                            rules={[{ required: true }]}
                        >
                            <Select
                                placeholder={intl.formatMessage({ id: 'workflow.repeatDimension' })}
                                options={repeatDimensionOptions}
                                onChange={handleRepeatDimensionChange}
                            />
                        </Form.Item>

                        {/* Repeat Interval */}
                        <Form.Item
                            label={intl.formatMessage({ id: 'workflow.repeatInterval' })}
                            name="repeatInterval"
                            rules={[
                                { required: true, message: intl.formatMessage({ id: 'workflow.pleaseInputInterval' }) },
                                { type: 'number', min: 1, message: intl.formatMessage({ id: 'workflow.intervalMustBePositive' }) }
                            ]}
                        >
                            <InputNumber
                                min={1}
                                placeholder={intl.formatMessage({ id: 'workflow.pleaseInputInterval' })}
                                style={{ width: '100%' }}
                                addonAfter={
                                    <span>
                                        {repeatDimension && 
                                            intl.formatMessage({ id: `workflow.${repeatDimension}` })
                                        }
                                    </span>
                                }
                            />
                        </Form.Item>

                        {/* End Condition */}
                        <Form.Item
                            label={intl.formatMessage({ id: 'workflow.endCondition' })}
                            name="endCondition"
                            rules={[{ required: true }]}
                        >
                            <Select
                                value={endCondition}
                                onChange={handleEndConditionChange}
                                options={endConditionOptions}
                            />
                        </Form.Item>

                        {/* End Time - Only show when endTime is selected */}
                        {endCondition === 'endTime' && (
                            <Form.Item
                                label={intl.formatMessage({ id: 'workflow.endTime' })}
                                name="endTime"
                                rules={[
                                    { required: true, message: intl.formatMessage({ id: 'workflow.pleaseSelectEndTime' }) },
                                    ({ getFieldValue }) => ({
                                        validator(_, value) {
                                            const startTime = getFieldValue('startTime');
                                            if (!value || !startTime) {
                                                return Promise.resolve();
                                            }
                                            if (value.isAfter(startTime)) {
                                                return Promise.resolve();
                                            }
                                            return Promise.reject(new Error('End time must be after start time'));
                                        },
                                    }),
                                ]}
                            >
                                <DatePicker
                                    showTime={{ format: 'HH:mm' }}
                                    format="YYYY-MM-DD HH:mm"
                                    placeholder={intl.formatMessage({ id: 'workflow.pleaseSelectEndTime' })}
                                    disabledDate={disabledDate}
                                    disabledTime={disabledTime}
                                    style={{ width: '100%' }}
                                />
                            </Form.Item>
                        )}
                    </>
                )}

                {/* Footer Buttons */}
                <Form.Item className="mb-0 mt-6">
                    <Space className="w-full justify-end">
                        {existingTask && (
                            <Button 
                                danger
                                onClick={handleCancelSchedule}
                                loading={loading}
                            >
                                {intl.formatMessage({ id: 'workflow.cancelSchedule', defaultMessage: 'Cancel Schedule' })}
                            </Button>
                        )}
                        <Button 
                            type="primary" 
                            onClick={handleConfirm}
                            loading={loading || submitting}
                        >
                            {intl.formatMessage({ id: 'workflow.savePlan', defaultMessage: 'Save Plan' })}
                        </Button>
                    </Space>
                </Form.Item>
            </Form>
        </Modal>
    );
};

export default ScheduleModal;