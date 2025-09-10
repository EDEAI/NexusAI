/*
 * @LastEditors: biz
 */
import { ProForm, ProFormDigit, ProFormDependency, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Typography, Button, Space, message } from 'antd';
import { memo, useState, useEffect } from 'react';
import { useUpdateEffect } from 'ahooks';
import { getWorkflowScheduledTask } from '@/api/workflow';
import { BlockEnum } from '../../../types';
import useStore from '../../../store';
import useSaveWorkFlow from '../../../saveWorkFlow';
import { TextareaRunName } from '../../Form/Input';
import { UploadDragger } from '../../Form/Upload';
import { InputContentProps } from './types';
import { runWorkFlow, deleteWorkflowScheduledTask } from '@/api/workflow';
import { ObjectVariable, Variable } from '@/py2js/variables';
import { UPLOAD_FILES_KEY } from '../../../config';
import _ from 'lodash';
import { ClockCircleOutlined } from '@ant-design/icons';
import ScheduleModal from '../../ScheduleModal';

// Define AppNodeData interface to resolve type errors
interface AppNodeData {
  label: string;
  requires_upload?: boolean;
  import_to_knowledge_base?: boolean;
  knowledge_base_mapping?: { [key: string]: any };
  [key: string]: any;
}

const InputContent = memo(({ onRunResult, loading, onCancelSchedule, appId, workflowId }: InputContentProps) => {
  const intl = useIntl();
  const nodes = useStore(state => state.nodes);
  const app_id = useStore(state => state.app_id);
  const getOutputVariables = useStore(state => state.getOutputVariables);
  const datasetData = useStore(state => state.datasetData);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [scheduleModalVisible, setScheduleModalVisible] = useState(false);
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [hasScheduledTask, setHasScheduledTask] = useState(false);
  const [checkingSchedule, setCheckingSchedule] = useState(false);
  const [existingTask, setExistingTask] = useState<any>(null);
  const [formRef] = ProForm.useForm();

  // Use the original saveWorkFlow hook
  const saveWorkFlow = useSaveWorkFlow();

  // 获取表单初始值
  const getInitialValues = () => {
    const initialValues: Record<string, any> = {

    };

    if (nodes[0]?.id) {
      const variables = getOutputVariables(nodes[0].id);
      variables.forEach(item => {
        // 为每个变量设置默认值
        if (item.createVar.default_value !== undefined) {
          initialValues[`var.${item.createVar.name}`] = item.createVar.default_value;
        } else if (item.createVar.type === 'number') {
          initialValues[`var.${item.createVar.name}`] = 0;
        } else if (item.createVar.type === 'string') {
          initialValues[`var.${item.createVar.name}`] = '';
        }else if(item.createVar.type === 'file'){
          initialValues[`var.${item.createVar.name}`] = [];
        }
      });
    }

    return initialValues;
  };



  useUpdateEffect(() => {
    if (loading === false) {
      setSubmitLoading(false);
    }
  }, [loading]);

  // Check for existing scheduled task on component mount
  useEffect(() => {
    const checkScheduledTask = async () => {
      if (!appId || !workflowId) {
        setCheckingSchedule(false);
        return;
      }
      try {
        setCheckingSchedule(true);
        const response = await getWorkflowScheduledTask(appId, workflowId);
        const hasTask =
          response && response.code === 0 && response.data && Object.keys(response.data || {}).length > 0;
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
    };

    // Directly check on dependency changes to avoid stale global guards preventing fetch
    checkScheduledTask();
  }, [appId, workflowId]);

  // Implement workflow running logic in the component
  const handleRun = async (value: any) => {
    setSubmitLoading(true);

    const findEnd = nodes.find(x => x.type === BlockEnum.End);
    if (!findEnd) {
      setSubmitLoading(false);
      return;
    }

    try {
      // First save the workflow
      await saveWorkFlow();

      // Build input variables object
      const input = new ObjectVariable('input_var');
      const vals = getOutputVariables(nodes[0].id);

      // Process variables
      for (const key in value) {
        if (key.startsWith('var.')) {
          const varName = key.replace('var.', '');
          const val = vals.find(x => x.createVar.name === varName);
          if (val) {
            let variableValue=value[key]
            if(_.isObject(value[key])){
               variableValue=value[key][0]?.response?.data?.file_id||''
            }
            const variable = new Variable(varName, val.createVar.type,variableValue);
            input.addProperty(varName, variable);
          }
        }
      }

      // Process knowledge base mapping
      const knowledge_base_mapping = (nodes[0]?.data && 'knowledge_base_mapping' in nodes[0].data)
        ? nodes[0].data.knowledge_base_mapping
        : { input: {}, output: {} };

      Object.entries(value).forEach(([key, val]) => {
        if (key.startsWith('dataset.')) {
          if (!knowledge_base_mapping.input[UPLOAD_FILES_KEY]) {
            knowledge_base_mapping.input[UPLOAD_FILES_KEY] = {};
          }
          knowledge_base_mapping.input[UPLOAD_FILES_KEY][key.replace('dataset.', '')] = val;
        }
      });

      // Build run parameters
      const params = {
        run_name: value.run_name || `Run-${new Date().toISOString()}`,
        inputs: input,
        run_type: 0,
        node_confirm_users: {},
        knowledge_base_mapping,
      };

      // Call run API
      const res = await runWorkFlow(app_id, params);

      if (res && res.code === 0) {
        onRunResult?.(res);
      }
    } catch (err) {
      console.error('Error running workflow:', err);
    } finally {
      setSubmitLoading(false);
    }
  };

  // Build workflow inputs from current form values
  const buildWorkflowInputs = async () => {
    try {
      // Use getFieldsValue to avoid triggering validations when scheduling
      const formValues = formRef.getFieldsValue();
      
      // Build input variables object (same as handleRun)
      const input = new ObjectVariable('input_var');
      const vals = getOutputVariables(nodes[0].id);

      // Process variables
      for (const key in formValues) {
        if (key.startsWith('var.')) {
          const varName = key.replace('var.', '');
          const val = vals.find(x => x.createVar.name === varName);
          if (val) {
            let variableValue = formValues[key];
            if (_.isObject(formValues[key])) {
              variableValue = formValues[key][0]?.response?.data?.file_id || '';
            }
            const variable = new Variable(varName, val.createVar.type, variableValue);
            input.addProperty(varName, variable);
          }
        }
      }

      // Also pick run name from form values for schedule naming
      const run_name = formValues?.run_name || '';

      return { input, run_name };
    } catch (error) {
      console.error('Failed to build workflow inputs:', error);
      return { input: new ObjectVariable('input_var'), run_name: '' };
    }
  };

  // Handle schedule click & confirm
  const handleScheduleClick = async () => {
    try {
      // If there's an existing scheduled task, open modal directly without validation
      if (hasScheduledTask) {
        setScheduleModalVisible(true);
        return;
      }
      
      // For new schedule, trigger validations just like clicking Run button
      await formRef.validateFields();
      setScheduleModalVisible(true);
    } catch (e) {
      // Validation errors will be shown by the form; we can optionally prompt
      message.warning(intl.formatMessage({ id: 'workflow.isRequire', defaultMessage: 'This field is required' }));
    }
  };

  const handleScheduleConfirm = async (scheduleData: any) => {
    try {
      setScheduleLoading(true);
      
      // The actual API call is handled in ScheduleModal component
      // This callback is triggered after successful creation/update
      console.log('Schedule operation completed:', scheduleData);
      
      setScheduleModalVisible(false);
    } catch (error) {
      console.error('Schedule operation failed:', error);
    } finally {
      setScheduleLoading(false);
    }
  };

  const handleScheduleCancel = () => setScheduleModalVisible(false);

  const handleCancelSchedule = async () => {
    if (existingTask && (existingTask as any).id) {
      try {
        setScheduleLoading(true);
        const res = await deleteWorkflowScheduledTask((existingTask as any).id);
        if (res && res.code === 0) {
          message.success(res.data.message);
        } else {
          throw new Error(res?.detail || 'Cancel operation failed');
        }
      } catch (e) {
        console.error('Failed to cancel scheduled task:', e);
      } finally {
        setScheduleLoading(false);
      }
    }
    setExistingTask(null);
    setHasScheduledTask(false);
    setScheduleModalVisible(false);
  };

  const handleExistingTaskChange = (task: any) => {
    setExistingTask(task);
    const ok = task && Object.keys(task || {}).length > 0;
    setHasScheduledTask(!!ok);
  };

  // Safely get node data, ensuring type safety
  const getNodeData = (node: any): AppNodeData => {
    return node?.data || { label: '' };
  };

  const firstNodeData = nodes[0] ? getNodeData(nodes[0]) : { label: '' };

  return (
    <>
      <ProForm
        form={formRef}
        loading={submitLoading}
        submitter={{
          resetButtonProps: false,
          render: (props, dom) => (
            <Space direction="vertical" className="w-full" size="middle">
              <Button
                type="primary"
                loading={submitLoading}
                onClick={() => props.form?.submit()}
                className="w-full"
                size="large"
              >
                {intl.formatMessage({ id: 'workflow.run', defaultMessage: 'Run' })}
              </Button>

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
                  ? intl.formatMessage({ id: 'workflow.viewSchedulePlan', defaultMessage: 'View Schedule Plan' })
                  : intl.formatMessage({ id: 'workflow.scheduleExecution', defaultMessage: 'Schedule Execution' })}
              </Button>
            </Space>
          ),
        }}
        onFinish={handleRun}
        initialValues={getInitialValues()}
      >
        <TextareaRunName name={'run_name'} />

        {nodes[0]?.id &&
          getOutputVariables(nodes[0].id)
            .sort((a, b) => a.createVar.sort_order - b.createVar.sort_order)
            .map((item, index) => {
              // Handle number type variables
              if (item?.createVar?.type === 'number') {
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
                  />
                );
              }

              // Handle file type variables
              if (item?.createVar?.type === 'file') {
                return (
                  <div key={index}>
                    <Typography.Title level={5}>
                      {item.createVar.display_name || item.createVar.name}
                      {item.createVar.required && <span className="text-red-500 ml-1">*</span>}
                    </Typography.Title>
                    <UploadDragger
                      name={`var.${item.createVar.name}`}
                      multiple={false}
                    />
                  </div>
                );
              }

              // Handle text type variables (default)
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
                />
              );
            })}

        {firstNodeData.requires_upload && (
          <div>
            <Typography.Title level={5}>
              {intl.formatMessage({ id: 'workflow.uploadFile' })}
            </Typography.Title>
            <UploadDragger
              name="file"
              multiple={true}
              accept=".txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv"
            />

            <ProFormDependency name={['file']}>
              {({ file }) => {
                return (
                  (firstNodeData.import_to_knowledge_base &&
                    file?.length > 0 && (
                      <div>
                        <Typography.Title level={5}>
                          {intl.formatMessage({
                            id: 'workflow.import_to_knowledge_base',
                          })}
                        </Typography.Title>
                        {file?.map((x: any) => {
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
                            />
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

      {/* Schedule Modal */}
      <ScheduleModal
        visible={scheduleModalVisible}
        onCancel={handleScheduleCancel}
        onConfirm={handleScheduleConfirm}
        onCancelSchedule={handleCancelSchedule}
        onExistingTaskChange={handleExistingTaskChange}
        loading={scheduleLoading}
        appId={appId}
        workflowId={workflowId}
        workflowInputs={buildWorkflowInputs}
        nodeConfirmUsers={{}}
        existingTask={existingTask}
      />
    </>
  );
});

export default InputContent;
