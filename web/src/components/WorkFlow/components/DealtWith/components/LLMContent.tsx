import { BlockEnum } from '@/components/WorkFlow/types';
import {
  ProForm,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { List, Typography, message, Spin } from 'antd';
import { useCallback, useState } from 'react';
import CodeEditor from '../../Editor/CodeEditor';
import { ContentProps } from './types';
import React from 'react';
import { Prompt } from '@/py2js/prompt';

const LLMContent = ({ dealtWithInfo, dealtWithData, execId, buttonLoading, onSubmit }: ContentProps) => {
  const intl = useIntl();
  const [messageApi, contextHolder] = message.useMessage();
  const [submitting, setSubmitting] = useState(false);
  const [updating, setUpdating] = useState(false);
  const nodeType = dealtWithData?.data?.node_exec_data?.node_type;

  // Save previous execId and dealtWithInfo for change detection
  const prevExecIdRef = React.useRef(execId);
  const prevInfoRef = React.useRef(dealtWithInfo);
  
  React.useEffect(() => {
    // If execId changes, it means we're loading new results
    if (execId !== prevExecIdRef.current) {
      setUpdating(true);
      prevExecIdRef.current = execId;
    } 
    // If dealtWithInfo changes and status is updating, show update success message
    else if (
      dealtWithInfo && 
      updating && 
      JSON.stringify(dealtWithInfo) !== JSON.stringify(prevInfoRef.current)
    ) {
      setUpdating(false);
      messageApi.success(
        intl.formatMessage({
          id: 'workflow.resultUpdatedMsg',
          defaultMessage: '修正结果已更新',
        })
      );
    }
    
    // Update references
    prevInfoRef.current = dealtWithInfo;
  }, [execId, dealtWithInfo, updating, messageApi, intl]);

  const handleSubmit = useCallback((values: any) => {
    setSubmitting(true);
    
    // Construct data structure same as DealtWithNew
    const submitData = {
      correct_prompt: new Prompt('', values.prompt, ''),
      operation: 1,
      outputs: dealtWithInfo?.outputs || null,
    };
    
    // Call the onSubmit method passed from parent component
    onSubmit(submitData);
    
    // Set success message and status
    setTimeout(() => {
      setSubmitting(false);
      messageApi.success(
        intl.formatMessage({
          id: 'workflow.promptSubmitSuccessMsg',
          defaultMessage: 'Prompt已提交，请点击确认完成待办',
        })
      );
      // Set updating status after submission success, waiting for new results
      setUpdating(true);
    }, 500);
  }, [onSubmit, messageApi, intl, dealtWithInfo]);

  return (
    <>
      {contextHolder}
      <div className="flex flex-col gap-2 mt-4">
        {nodeType !== BlockEnum.LLM && (
          <div className="h-80">
            <CodeEditor
              language="python3"
              value={dealtWithInfo?.inputs}
              readOnly
              isJSONStringifyBeauty
              onChange={() => {}}
              title={`input`}
            ></CodeEditor>
          </div>
        )}

        {dealtWithInfo?.correct_llm_history?.length > 0 && (
          <List
            header={
              <Typography.Title level={5}>
                {intl.formatMessage({
                  id: 'workflow.historyPrompt',
                  defaultMessage: 'prompt',
                })}
              </Typography.Title>
            }
            dataSource={dealtWithInfo?.correct_llm_history}
            renderItem={item => (
              <List.Item>{item?.correct_prompt?.user?.value}</List.Item>
            )}
          ></List>
        )}

        <div className="h-80 relative">
          {updating && (
            <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-20 z-10">
              <Spin tip={intl.formatMessage({ id: 'workflow.updatingResult', defaultMessage: '正在更新结果...' })} />
            </div>
          )}
          <CodeEditor
            language="python3"
            value={dealtWithInfo?.outputs}
            readOnly
            isJSONStringifyBeauty
            onChange={() => {}}
            title={`output`}
          ></CodeEditor>
        </div>
      </div>
      <ProForm
        submitter={{
          resetButtonProps: false,
          submitButtonProps: {
            className: 'w-full',
            loading: submitting,
          },
          searchConfig: {
            submitText: intl.formatMessage({ id: 'workflow.xz' }),
          },
        }}
        loading={buttonLoading}
        onFinish={handleSubmit}
      >
        <div className="flex">
          <div className="flex-1 pt-2 border-stone-300 border rounded-md my-2">
            <div className="px-2 flex justify-between cursor-default">
              <div>
                <div className="text-sm text-gray-500 font-bold pb-1">
                  Prompt
                </div>
              </div>
              <div></div>
            </div>
            <div className="pb-6 user-input-error">
              <ProFormTextArea
                formItemProps={{
                  className: 'mb-0',
                }}
                name="prompt"
                required
                rules={[
                  {
                    required: true,
                    message: intl.formatMessage({
                      id: 'workflow.requireInputPrompt',
                    }),
                  },
                ]}
                fieldProps={{
                  variant: 'borderless',
                  placeholder: intl.formatMessage({
                    id: 'workflow.requireInputPrompt',
                  }),
                  autoSize: { minRows: 2, maxRows: 40 },
                  count: {
                    show: ({ count }) => (
                      <div className="pr-2 text-blue-400">{count}</div>
                    ),
                  },
                }}
              />
            </div>
          </div>
        </div>
      </ProForm>
    </>
  );
};

export default LLMContent; 