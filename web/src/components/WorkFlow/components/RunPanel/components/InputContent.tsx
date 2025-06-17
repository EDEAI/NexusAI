/*
 * @LastEditors: biz
 */
import { ProForm, ProFormDigit, ProFormDependency, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Typography } from 'antd';
import { memo, useState } from 'react';
import { useMount, useUpdateEffect } from 'ahooks';
import { BlockEnum } from '../../../types';
import useStore from '../../../store';
import useSaveWorkFlow from '../../../saveWorkFlow';
import { TextareaRunName } from '../../Form/Input';
import { UploadDragger } from '../../Form/Upload';
import { InputContentProps } from './types';
import { runWorkFlow } from '@/api/workflow';
import { ArrayVariable, ObjectVariable, Variable } from '@/py2js/variables';
import { UPLOAD_FILES_KEY } from '../../../config';
import _ from 'lodash';

// Define AppNodeData interface to resolve type errors
interface AppNodeData {
  label: string;
  requires_upload?: boolean;
  import_to_knowledge_base?: boolean;
  knowledge_base_mapping?: { [key: string]: any };
  [key: string]: any;
}

const InputContent = memo(({ onRunResult, loading }: InputContentProps) => {
  const intl = useIntl();
  const nodes = useStore(state => state.nodes);
  const app_id = useStore(state => state.app_id);
  const getOutputVariables = useStore(state => state.getOutputVariables);
  const datasetData = useStore(state => state.datasetData);
  const [submitLoading, setSubmitLoading] = useState(false);

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

  useMount(() => {
    if (nodes[0]?.id) {
      console.log(getOutputVariables(nodes[0].id));
    }
  });

  useUpdateEffect(() => {
    if (loading === false) {
      setSubmitLoading(false);
    }
  }, [loading]);

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

      // Process files
      // const freeFile = new ArrayVariable(UPLOAD_FILES_KEY, 'array[number]');
      // if (value.file && Array.isArray(value.file)) {
      //   value.file.forEach((x: any) => {
      //     const fileId = x?.response?.data?.file_id || 0;
      //     if (fileId) {
      //       const fileVariable = new Variable(x.uid, 'number', fileId);
      //       freeFile.addValue(fileVariable);
      //     }
      //   });
      // }
      // input.addProperty(UPLOAD_FILES_KEY, freeFile);

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

  // Safely get node data, ensuring type safety
  const getNodeData = (node: any): AppNodeData => {
    return node?.data || { label: '' };
  };

  const firstNodeData = nodes[0] ? getNodeData(nodes[0]) : { label: '' };

  return (
    <ProForm
      loading={submitLoading}
      submitter={{
        resetButtonProps: false,
        submitButtonProps: {
          className: 'w-full',
        },
        searchConfig: {
          submitText: intl.formatMessage({
            id: 'workflow.run',
            defaultMessage: '',
          }),
        },
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
  );
});

export default InputContent;
