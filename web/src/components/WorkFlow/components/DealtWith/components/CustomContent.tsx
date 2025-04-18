import { NOT_SHOW_INPUT_RESULT_NODE } from '@/components/WorkFlow/config';
import { Button, Typography, message } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import CodeEditor from '../../Editor/CodeEditor';
import { ContentProps } from './types';
import { flattenObjectProperties } from './utils';
import { useIntl } from '@umijs/max';

const CustomContent = ({ dealtWithInfo, onUpdate, execId }: ContentProps) => {
  const intl = useIntl();
  const [outputsValue, setOutputsValue] = useState('');
  const [messageApi, contextHolder] = message.useMessage();

  useEffect(() => {
    if (dealtWithInfo?.outputs) {
      const flattenedOutputs = flattenObjectProperties(dealtWithInfo.outputs);
      setOutputsValue(JSON.stringify(flattenedOutputs));
    }
  }, [dealtWithInfo]);

  const handleSubmit = useCallback(() => {
    try {
      const outputs = JSON.parse(outputsValue);
      onUpdate(execId, {
        outputs: Array.isArray(outputs) ? outputs[0] : outputs,
      }).then(res => {
        if (res.code === 0) {
          messageApi.success(
            intl.formatMessage({
              id: 'workflow.checkSc',
              defaultMessage: '',
            })
          );
        }
      }).catch(() => {
        messageApi.error(
          intl.formatMessage({
            id: 'workflow.checkOutputMessageError',
            defaultMessage: ',',
          })
        );
      });
    } catch (error) {
      messageApi.error(
        intl.formatMessage({
          id: 'workflow.checkOutputMessageError',
          defaultMessage: ',',
        })
      );
    }
  }, [outputsValue, onUpdate, execId, messageApi, intl]);

  return (
    <div>
      {contextHolder}
      <div className="flex flex-col gap-2 pt-4">
        {!NOT_SHOW_INPUT_RESULT_NODE.includes(dealtWithInfo?.node_type as string) && (
          <div>
            <Typography.Title level={5}>Inputs</Typography.Title>
            <div className="h-80">
              <CodeEditor
                language="python3"
                value={dealtWithInfo?.inputs}
                readOnly
                isJSONStringifyBeauty
                onChange={() => {}}
              ></CodeEditor>
            </div>
          </div>
        )}
        <Typography.Title level={5}>
          Outputs({intl.formatMessage({ id: 'workflow.toEdit', defaultMessage: '' })})
        </Typography.Title>
        <div className="h-80">
          <CodeEditor
            language="python3"
            value={dealtWithInfo?.outputs}
            isJSONStringifyBeauty
            onChange={value => {
              setOutputsValue(value);
            }}
          ></CodeEditor>
        </div>
        <Button type="primary" onClick={handleSubmit} className="w-full mt-4">
          {intl.formatMessage({ id: 'workflow.checked', defaultMessage: '' })}
        </Button>
      </div>
    </div>
  );
};

export default CustomContent; 