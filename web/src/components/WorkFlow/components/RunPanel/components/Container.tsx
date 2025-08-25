/*
 * @LastEditors: biz
 */
import { CloseOutlined, PauseOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { ProCard } from '@ant-design/pro-components';
import { Button, Typography, Tooltip } from 'antd';
import { memo } from 'react';
import { ContainerProps } from './types';
import { useIntl } from '@umijs/max';

const Container = memo(({
  runPanelShow,
  setRunPanelShow,
  title,
  tabItems,
  activeKey,
  onTabChange,
  children,
  showPauseResume,
  isPaused,
  onPauseResume,
}: ContainerProps) => {
  const intl = useIntl();
  if (!runPanelShow) return null;

  return (
    <ProCard
      className="w-[400px] border user_pro_card_overflow_y border-blue-300 fixed z-10 top-[105px] right-2"
      style={{ 
        height: 'calc(100vh - 10px - 100px)',
        maxWidth: '85vw',
        overflow: 'hidden' 
      }}
      extra={
        <div className="flex items-center gap-3">
          {showPauseResume && (
            <Tooltip 
              title={isPaused 
                ? intl.formatMessage({ id: 'workflow.resumeRun', defaultMessage: 'Resume Run' })
                : intl.formatMessage({ id: 'workflow.pauseRun', defaultMessage: 'Pause Run' })
              }
            >
              <Button
                type="primary"
                size="small"
                onClick={onPauseResume}
                icon={isPaused ? <PlayCircleOutlined /> : <PauseOutlined />}
                className="bg-blue-500 hover:bg-blue-600 border-blue-500 hover:border-blue-600"
              >
              </Button>
            </Tooltip>
          )}
          <Button
            type="text"
            onClick={() => setRunPanelShow(false)}
            icon={<CloseOutlined />}
          />
        </div>
      }
      title={
        <Typography.Title level={5} className="truncate">
          {title}
        </Typography.Title>
      }
      bodyStyle={{
        overflowY: 'auto',
        overflowX: 'hidden',
        padding: '12px',
      }}
      tabs={{
        tabPosition: 'top',
        activeKey,
        className: 'overflow-hidden w-full',
        items: tabItems.map(item => ({
          ...item,
          children: (
            <div className="w-full overflow-hidden">
              {item.children}
            </div>
          ),
        })),
        onChange: onTabChange,
      }}
    >
      {children}
    </ProCard>
  );
});

export default Container;