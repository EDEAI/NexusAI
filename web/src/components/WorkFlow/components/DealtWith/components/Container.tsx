/*
 * @LastEditors: biz
 */
import { BlockEnum } from '@/components/WorkFlow/types';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { ProCard } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Button, Typography } from 'antd';
import { ContainerProps } from './types';

const Container = ({
  dealtWithData,
  setDealtWithData,
  show,
  setShow,
  execId,
  dealtWithInfo,
  buttonLoading,
  onConfirm,
  onClose,
  children,
}: ContainerProps) => {
  const intl = useIntl();

  const handleClose = () => {
    setShow(false);
    setDealtWithData(null);
    onClose?.();
  };

  const handleConfirm = () => {
    onConfirm?.(execId);
  };

  const ConfirmButton = () => {
    const nodeType = dealtWithInfo?.node_type;
    if (
      nodeType === BlockEnum.LLM ||
      nodeType === BlockEnum.Agent ||
      nodeType === BlockEnum.TaskGeneration
    ) {
      return (
        <Button
          type="text"
          onClick={handleConfirm}
          className="text-green-500"
          disabled={buttonLoading}
          icon={<CheckOutlined></CheckOutlined>}
        >
          {intl.formatMessage({
            id: 'workflow.checkBackLogs',
            defaultMessage: '',
          })}
        </Button>
      );
    }
    return null;
  };

  return show ? (
    <ProCard
      className="w-[400px] border border-blue-300 fixed z-20 top-[105px] right-2"
      style={{ height: 'calc(100vh - 10px - 100px)' }}
      extra={
        <div className="flex gap-2">
          {<ConfirmButton />}
          <Button
            onClick={handleClose}
            type="text"
            icon={<CloseOutlined />}
          ></Button>
        </div>
      }
      title={
        <Typography.Title level={5}>
          {intl.formatMessage({ id: 'workflow.backlogs', defaultMessage: '' })}
        </Typography.Title>
      }
      bodyStyle={{
        overflowY: 'auto',
        marginTop: '20px',
        boxSizing: 'border-box',
      }}
    >
      <div>
        <div>
          <Typography.Title level={5}>
            {dealtWithInfo?.node_graph?.data?.title}
          </Typography.Title>
        </div>
        <div>
          <Typography.Text>{dealtWithInfo?.node_graph?.data?.desc}</Typography.Text>
        </div>
        {children}
      </div>
    </ProCard>
  ) : null;
};

export default Container; 