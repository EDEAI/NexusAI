/*
 * @LastEditors: biz
 */
import { Alert, Divider, Typography } from 'antd';
import { useIntl } from '@umijs/max';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import { ProForm, ProFormText, ProFormDateTimePicker } from '@ant-design/pro-components';
import CodeEditor from '../../Editor/CodeEditor';
import FileDownloadList from '@/components/common/FileDownloadList';
import { DetailContentProps } from './types';

const { Text } = Typography;

const DetailContent = memo(({ endRun }: DetailContentProps) => {
  const intl = useIntl();
  const [messageType, setMessageType] = useState<'success' | 'fail'>('fail');
  const form = useRef(null);
  const [code, setCode] = useState('');
  
  const messConfig = {
    statusClass: {
      success: 'green-700',
      fail: 'red-700',
    },
    message: {
      success: 'Success',
      fail: 'Fail',
    },
    messageType: {
      success: 'success',
      fail: 'error',
    },
  } as const;
  
  type MessConfigKeys = keyof typeof messConfig;
  
  const getMessage = useCallback(
    (configName: MessConfigKeys) => {
      return messConfig[configName][messageType];
    },
    [messageType],
  );

  useEffect(() => {
    if (endRun && form.current) {
      form.current.setFieldsValue({
        status: 'success',
        elapsed_time: endRun?.data?.elapsed_time?.toFixed(4) || 0,
        completion_tokens: endRun?.data?.completion_tokens || '',
        created_time: endRun?.data?.created_time || '',
        total_tokens: endRun?.data?.total_tokens || '',
        actual_completed_steps: endRun?.data?.actual_completed_steps || '',
      });
      setMessageType('success');
    }
  }, [endRun]);

  const Message = () => {
    return (
      <div>
        <div className="grid grid-cols-3">
          <div>
            <div className="text-gray-500 text-sm">
              {intl.formatMessage({
                id: 'workflow.label.status',
                defaultMessage: '',
              })}
            </div>
            <div
              className={`text-${getMessage('statusClass')} font-bold text-base flex gap-2 items-center`}
            >
              <div className={`size-2 bg-${getMessage('statusClass')}`}></div>
              {getMessage('message')}
            </div>
          </div>
          <div>
            <div className="text-gray-500 text-sm">
              {intl.formatMessage({
                id: 'workflow.label.elapsedTime',
                defaultMessage: '',
              })}
            </div>
            <div className="font-bold text-base">
              {endRun?.data?.elapsed_time?.toFixed(4) || 0}s
            </div>
          </div>
          <div>
            <div className="text-gray-500 text-sm">
              {intl.formatMessage({
                id: 'workflow.label.totalTokens',
                defaultMessage: 'token',
              })}
            </div>
            <div className="font-bold text-base">
              {endRun?.data?.total_tokens || 0} Tokens
            </div>
          </div>
        </div>
      </div>
    );
  };

  const alertType = getMessage('messageType') as 'success' | 'error';
  
  // If there's no endRun, display a placeholder content
  if (!endRun) {
    return (
      <div className="p-4 text-gray-500">
        {intl.formatMessage({ id: 'workflow.noResultData' })}
      </div>
    );
  }
  
  return (
    <>
      <Alert message={<Message />} type={alertType} />
      <div className="h-80 mt-4 w-full overflow-hidden">
        <CodeEditor
          language="python3"
          value={endRun?.data?.node_exec_data?.outputs || ''}
          mdValue={endRun?.data?.node_exec_data?.outputs_md || ''}
          readOnly
          isJSONStringifyBeauty
          title={intl.formatMessage({
            id: 'workflow.label.output',
            defaultMessage: '',
          })}
        />
      </div>

      <Divider orientationMargin="0" orientation="left">
        {intl.formatMessage({ id: 'workflow.label.metadata', defaultMessage: '' })}
      </Divider>

      <ProForm
        layout="horizontal"
        formRef={form}
        initialValues={{
          status: 'fail',
        }}
        submitter={false}
        labelAlign="left"
        labelCol={{ span: 8 }}
        wrapperCol={{ span: 16 }}
        className="w-full overflow-hidden"
      >
        <ProFormText
          formItemProps={{
            className: '!mb-0',
          }}
          readonly
          label={intl.formatMessage({
            id: 'workflow.label.status',
            defaultMessage: '',
          })}
          name="status"
        />
        <ProFormDateTimePicker
          formItemProps={{
            className: '!mb-0',
          }}
          readonly
          label={intl.formatMessage({
            id: 'workflow.label.startTime',
            defaultMessage: '',
          })}
          name="created_time"
        />
        <ProFormText
          formItemProps={{
            className: '!mb-0',
          }}
          readonly
          label={intl.formatMessage({
            id: 'workflow.label.elapsedTime',
            defaultMessage: '',
          })}
          name="elapsed_time"
        />
        <ProFormText
          formItemProps={{
            className: '!mb-0',
          }}
          readonly
          label={intl.formatMessage({
            id: 'workflow.label.totalTokens',
            defaultMessage: 'token',
          })}
          name="total_tokens"
        />
        <ProFormText
          formItemProps={{
            className: '!mb-0',
          }}
          readonly
          label={intl.formatMessage({
            id: 'workflow.label.completedSteps',
            defaultMessage: '',
          })}
          name="actual_completed_steps"
        />
      </ProForm>

      {endRun?.data?.node_exec_data?.file_list?.length > 0 && (
        <div className="w-full overflow-hidden">
          <FileDownloadList 
            files={endRun.data.node_exec_data.file_list} 
            title={intl.formatMessage({ id: 'skill.downloadFiles' })}
            className="w-full"
          />
        </div>
      )}
    </>
  );
});

export default DetailContent; 