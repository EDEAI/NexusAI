import React, { useEffect, useRef, useState } from 'react';
import { Spin } from 'antd';
import { useIntl } from '@umijs/max';

/**
 * Props interface for InfiniteScroll component
 * @interface InfiniteScrollProps
 */
interface InfiniteScrollProps {
    /** Content to be rendered inside the scroll container */
    children: React.ReactNode;
    /** Callback function to load more items when scrolling down */
    onLoadMore?: () => Promise<void>;
    /** Callback function to load previous items when scrolling up */
    onLoadPrevious?: () => Promise<void>;
    /** Flag indicating if there are more items to load when scrolling down */
    hasMore: boolean;
    /** Flag indicating if there are previous items to load when scrolling up */
    hasPrevious?: boolean;
    /** Distance in pixels from the edge to trigger loading (default: 100) */
    threshold?: number;
    /** Additional CSS classes for the container */
    className?: string;
    /** Custom loading indicator component */
    loadingComponent?: React.ReactNode;
    /** Custom error component */
    errorComponent?: React.ReactNode;
    /** Initial scroll position ('top' or 'bottom', default: 'bottom') */
    initialScrollPosition?: 'top' | 'bottom';
    /** Whether to preserve scroll position when loading new content (default: true) */
    preserveScrollPosition?: boolean;
    /** Scroll behavior for automatic scrolling (default: 'smooth') */
    scrollBehavior?: ScrollBehavior;
}

/**
 * InfiniteScroll component for handling infinite scrolling in both directions
 * 
 * @component
 * @example
 * ```tsx
 * <InfiniteScroll
 *   onLoadPrevious={loadPreviousItems}
 *   onLoadMore={loadMoreItems}
 *   hasPrevious={true}
 *   hasMore={true}
 *   threshold={50}
 * >
 *   {items.map(item => <Item key={item.id} {...item} />)}
 * </InfiniteScroll>
 * ```
 */
const InfiniteScroll = ({
    children,
    onLoadMore,
    onLoadPrevious,
    hasMore,
    hasPrevious = false,
    threshold = 100,
    className = '',
    loadingComponent = <Spin size="small" />,
    errorComponent,
    initialScrollPosition = 'bottom',
    preserveScrollPosition = true,
    scrollBehavior = 'smooth',
}: InfiniteScrollProps) => {
    const intl = useIntl();
    const containerRef = useRef<HTMLDivElement>(null);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [isLoadingPrevious, setIsLoadingPrevious] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const loadingRef = useRef(false);
    const isInitialMount = useRef(true);

    const scrollToBottom = () => {
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    };

    useEffect(() => {
        if (isInitialMount.current && containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
            isInitialMount.current = false;
        }
    }, []);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const handleScroll = async () => {
            if (loadingRef.current) return;
            
            const { scrollTop, scrollHeight, clientHeight } = container;
            
            if (hasPrevious && !isLoadingPrevious && scrollTop < threshold) {
                try {
                    loadingRef.current = true;
                    setIsLoadingPrevious(true);
                    
                    const beforeScrollHeight = container.scrollHeight;
                    const beforeScrollTop = container.scrollTop;
                    
                    await onLoadPrevious?.();
                    
                    requestAnimationFrame(() => {
                        const afterScrollHeight = container.scrollHeight;
                        const heightDiff = afterScrollHeight - beforeScrollHeight;
                        container.scrollTop = beforeScrollTop + heightDiff;
                    });
                } finally {
                    loadingRef.current = false;
                    setIsLoadingPrevious(false);
                }
            }

            if (hasMore && !isLoadingMore && scrollHeight - scrollTop - clientHeight < threshold) {
                try {
                    loadingRef.current = true;
                    setIsLoadingMore(true);
                    await onLoadMore?.();
                    container.scrollTop = container.scrollHeight;
                } finally {
                    loadingRef.current = false;
                    setIsLoadingMore(false);
                }
            }
        };

        const debouncedHandleScroll = debounce(handleScroll, 150);
        container.addEventListener('scroll', debouncedHandleScroll);
        return () => container.removeEventListener('scroll', debouncedHandleScroll);
    }, [hasMore, hasPrevious, onLoadMore, onLoadPrevious, threshold, isLoadingMore, isLoadingPrevious]);

    function debounce(fn: Function, delay: number) {
        let timeoutId: NodeJS.Timeout;
        return function (...args: any[]) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    return (
        <div 
            ref={containerRef} 
            className={`relative overflow-y-auto ${className}`}
        >
            <div className="flex flex-col-reverse min-h-full">
                {isLoadingPrevious && (
                    <div className="sticky top-0 left-0 right-0 flex justify-center py-2 bg-white/80 z-10">
                        {loadingComponent}
                    </div>
                )}
                {children}
                {isLoadingMore && (
                    <div className="sticky bottom-0 left-0 right-0 flex justify-center py-2 bg-white/80 z-10">
                        {loadingComponent}
                    </div>
                )}
            </div>
            {error && (
                <div className="sticky top-0 w-full text-center py-2 text-red-500">
                    {errorComponent || error.message}
                </div>
            )}
        </div>
    );
};

export default InfiniteScroll; 