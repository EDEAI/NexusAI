import React, { useState, useEffect } from 'react';
import { List, Avatar, Spin } from 'antd';
import InfiniteScroll from './InfiniteScroll';

interface Message {
    id: number;
    content: string;
    timestamp: string;
    avatar: string;
}

const InfiniteScrollDemo: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [hasMoreHistory, setHasMoreHistory] = useState(true);
    const [initialLoading, setInitialLoading] = useState(true);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const PAGE_SIZE = 20;
    const MAX_MESSAGES = 100;

    const generateMessages = (startId: number, count: number) => {
        return Array.from({ length: count }, (_, index) => {
            const id = startId + index;
            const timeOffset = (MAX_MESSAGES - id) * 60000;
            return {
                id,
                content: `Message content ${id}, sent at ${new Date(Date.now() - timeOffset).toLocaleTimeString()}`,
                timestamp: new Date(Date.now() - timeOffset).toISOString(),
                avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${id}`
            };
        });
    };

    const fetchInitialMessages = async () => {
        try {
            setInitialLoading(true);
            await new Promise(resolve => setTimeout(resolve, 1000));
      
            const initialMessages = generateMessages(81, PAGE_SIZE);
            setMessages(initialMessages);
        } catch (error) {
            console.error('Failed to fetch initial messages:', error);
        } finally {
            setInitialLoading(false);
        }
    };
    

    const fetchHistoryMessages = async () => {
        if (isLoadingMore) return;

        try {
            setIsLoadingMore(true);
            const earliestId = messages[0]?.id || 0;
            
            if (earliestId <= 1) {
                setHasMoreHistory(false);
                return;
            }

            await new Promise(resolve => setTimeout(resolve, 200));
            
            const nextStartId = Math.max(1, earliestId - PAGE_SIZE);
            const count = earliestId - nextStartId;
            
            const historyMessages = generateMessages(nextStartId, count);
            setMessages(prev => [...historyMessages, ...prev]);
            
            if (nextStartId <= 1) {
                setHasMoreHistory(false);
            }
        } finally {
            setIsLoadingMore(false);
        }
    };


    useEffect(() => {
        fetchInitialMessages();
    }, []);

    if (initialLoading) {
        return (
            <div className="w-full max-w-2xl mx-auto p-4">
                <div className="border rounded-lg h-[400px] flex items-center justify-center">
                    <Spin />
                </div>
            </div>
        );
    }

    const LoadingIndicator = () => (
        <div className="flex items-center justify-center py-2 bg-white/80">
            <Spin size="small" />
            <span className="ml-2 text-sm text-gray-500">Loading more messages...</span>
        </div>
    );

    return (
        <div className="w-full max-w-2xl mx-auto p-4">
            <h2 className="text-xl font-bold mb-4">Chat History</h2>
            <div className="border rounded-lg h-[400px] bg-gray-50">
                <InfiniteScroll
                    className="h-full"
                    onLoadPrevious={fetchHistoryMessages}
                    hasPrevious={hasMoreHistory}
                    hasMore={false}
                    threshold={50}
                    loadingComponent={<LoadingIndicator />}
                >
                    <div className="px-4 py-2 space-y-3">
                        {messages.map((message) => (
                            <div 
                                key={message.id} 
                                className="flex items-start space-x-3"
                            >
                                <Avatar src={message.avatar} />
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-baseline justify-between">
                                        <span className="text-sm font-medium text-gray-900">
                                            User #{message.id}
                                        </span>
                                        <span className="text-xs text-gray-500">
                                            {new Date(message.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <div className="mt-1 text-sm text-gray-700 bg-white rounded-lg p-2 shadow-sm">
                                        {message.content}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </InfiniteScroll>
            </div>
            <div className="mt-4 text-sm text-gray-500">
                Tip: Scroll up to load more history
            </div>
        </div>
    );
};

export default InfiniteScrollDemo; 