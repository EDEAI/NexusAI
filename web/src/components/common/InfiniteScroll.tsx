/*
 * @LastEditors: biz
 */
import React, { useEffect, useRef, useState } from 'react';
import { Spin } from 'antd';
import { useIntl } from '@umijs/max';

interface InfiniteScrollProps {
    loading?: boolean;
    hasMore: boolean;
    onLoadMore: () => void;
    children: React.ReactNode;
    className?: string;
    threshold?: number;
}

const InfiniteScroll: React.FC<InfiniteScrollProps> = ({
    loading = false,
    hasMore,
    onLoadMore,
    children,
    className = '',
    threshold = 0.8,
}) => {
    const intl = useIntl();
    const [isIntersecting, setIsIntersecting] = useState(false);
    const targetRef = useRef<HTMLDivElement>(null);
    const observerRef = useRef<IntersectionObserver | null>(null);

    useEffect(() => {
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: threshold,
        };

        observerRef.current = new IntersectionObserver(([entry]) => {
            setIsIntersecting(entry.isIntersecting);
        }, options);

        if (targetRef.current) {
            observerRef.current.observe(targetRef.current);
        }

        return () => {
            if (observerRef.current) {
                observerRef.current.disconnect();
            }
        };
    }, [threshold]);

    useEffect(() => {
        if (isIntersecting && !loading && hasMore) {
            onLoadMore();
        }
    }, [isIntersecting, loading, hasMore]);

    return (
        <div className={`relative ${className}`}>
            {children}
            <div ref={targetRef} className="h-4 w-full" />
            {loading && (
                <div className="flex justify-center py-4">
                    <Spin />
                </div>
            )}
            {!hasMore && !loading && (
                <div className="text-center text-gray-500 py-4">
                    {intl.formatMessage({ id: 'common.no.more.data' })}
                </div>
            )}
        </div>
    );
};

export default InfiniteScroll; 