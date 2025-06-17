/*
 * @LastEditors: biz
 */
import { useEffect, useState } from 'react';
import { useLocation, useParams } from 'umi';

/**
 * 自定义 location hook，增强对 URL 参数变化的监听能力
 * @returns 返回当前 location 信息和从 URL 中获取的 ID
 */
const useCustomLocation = () => {
  const location = useLocation();
  const { id: urlParamId } = useParams<{ id: string }>();
  const [searchParamId, setSearchParamId] = useState<string | null>(null);
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  // 监听 URL 变化，更新搜索参数
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const newSearchParamId = searchParams.get('id');
    setSearchParamId(newSearchParamId);
    
    // 优先使用路径参数，其次使用查询参数
    const newId = urlParamId || newSearchParamId;
    if (newId !== currentId) {
      setCurrentId(newId);
    }
  }, [location, urlParamId]);

  // 监听自定义的 URL 更新事件
  useEffect(() => {
    const handleUrlUpdated = (event: CustomEvent) => {
      if (event.detail && event.detail.id) {
        setCurrentId(String(event.detail.id));
      }
    };
    
    window.addEventListener('url-updated', handleUrlUpdated as EventListener);
    
    return () => {
      window.removeEventListener('url-updated', handleUrlUpdated as EventListener);
    };
  }, []);
  
  return {
    location,
    urlParamId,
    searchParamId,
    id: currentId,
  };
};

export default useCustomLocation; 