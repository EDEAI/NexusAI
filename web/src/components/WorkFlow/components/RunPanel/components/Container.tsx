/*
 * @LastEditors: biz
 */
import { CloseOutlined } from '@ant-design/icons';
import { ProCard } from '@ant-design/pro-components';
import { Button, Typography } from 'antd';
import { memo } from 'react';
import { ContainerProps } from './types';

const Container = memo(({
  runPanelShow,
  setRunPanelShow,
  title,
  tabItems,
  activeKey,
  onTabChange,
  children,
}: ContainerProps) => {
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
        <Button
          type="text"
          onClick={() => setRunPanelShow(false)}
          icon={<CloseOutlined />}
        />
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