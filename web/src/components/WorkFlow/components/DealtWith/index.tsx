/*
 * @LastEditors: biz
 */
import useSocketStore from '@/store/websocket';
import { memo } from 'react';
import DealtWith from './components';

interface DealtWithNewProps {
  onSubmit?: (execId: string) => void;
  onClose?: () => void;
}

/**
 * 优化版的DealtWith组件
 * 使用更清晰的组件结构和逻辑分离
 */
export default memo(({ onSubmit, onClose }: DealtWithNewProps) => {
  return <DealtWith onSubmit={onSubmit} onClose={onClose} />;
}); 
