/*
 * @LastEditors: biz
 */
import {
    clearAgentMessageMemory,
    getAgentMessageHistory,
    postAgentChatMessage,
    PutagentPublish,
} from '@/api/agents';
import InfiniteScroll from '@/components/common/InfiniteScroll';
import { createPromptFromObject } from '@/py2js/prompt.js';
import useSocketStore from '@/store/websocket';
import { DeleteOutlined, ExclamationCircleFilled, SendOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useUpdateEffect } from 'ahooks';
import { Button, message, Modal, Spin } from 'antd';
import { memo, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';

interface ApiResponse<T> {
    code: number;
    data: T;
    message?: string;
}

interface SocketMessageData {
    message_id: number;
    message: string;
    agent_run_id: number;
    ability_id?: number;
    error?: string;
    created_time?: string;
    total_tokens?: number;
}

interface SocketMessage {
    data: SocketMessageData;
}

interface WebSocketStore {
    getTypedMessages: (type: string) => SocketMessageData[];
    getTypedLastMessage: (type: string) => SocketMessage | null;
}

interface SocketMessageResponse {
    data: SocketMessageData;
}

type SocketMessages = SocketMessageResponse[];

interface Message {
    id: number;
    message: string;
    agent_run_id: number;
    ability_id?: number;
    error?: string;
    created_time?: string;
    total_tokens?: number;
    content?: string;
    isUser?: boolean;
    agent_id?: number;
    completion_tokens?: number;
    prompt_tokens?: number;
}

interface MessageProps {
    message: Message;
    detailList?: {
        agent: {
            agent_id: number;
            input_variables: any;
        };
        app?: {
            name: string;
        };
    };
    abilitiesList?: Array<{
        value: number;
        label: string;
    }>;
}

interface Props {
    data: {
        detailList: {
            agent: {
                agent_id: number;
                input_variables: any;
            };
            app?: {
                name: string;
            };
        };
        abilitiesList: Array<{
            value: number;
            label: string;
        }>;
    };
    operationbentate?: string;
    saveInfo?: {
        firstjudgingcondition: () => boolean;
        secondjudgingcondition: () => boolean;
        agentupdata: () => void;
    };
}

interface HistoryResponse {
    list: Message[];
    total_pages: number;
}

const UserMessageComponent = memo(({ message }: MessageProps) => (
    <div className="flex justify-end">
        <div className="max-w-[70%] rounded-lg p-3 bg-blue-100 text-blue-900">
            {message.message}
        </div>
    </div>
));

const LLMMessageComponent = memo(({ message, detailList, abilitiesList }: MessageProps) => {
    const intl = useIntl();
    const ability = abilitiesList.find(item => item.value === message.ability_id);
    return (
        <div className="flex justify-start pb-4">
            <div>
                <div className="text-sm font-bold mb-2">
                    {detailList?.app?.name}{' '}
                    {ability?.label && (
                        <span className="text-gray-500 font-normal text-xs">
                            ({ability?.label})
                        </span>
                    )}
                </div>
                <div className="max-w-[90%] rounded-lg  relative bg-white text-gray-900 border border-gray-200">
                    {message.message && (
                        <div className="p-3">
                            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                {message.message}
                            </ReactMarkdown>
                        </div>
                    )}
                    {message.error && (
                        <div className="p-3 text-red-500">
                            <div>{intl.formatMessage({ id: 'agent.chat.error.message' })}</div>
                            {message.error}
                        </div>
                    )}
                    <div className="absolute w-full mt-1">
                        <div className="text-xs text-gray-500 flex justify-between">
                            <div>{message.created_time}</div>
                            <div>
                                {/* {intl.formatMessage({ id: 'agent.chat.tokens' })}:{' '}
                                <span className="text-blue-500">{message.total_tokens || 0}</span> */}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
});

const LoadingMessage = memo(({ detailList }: { detailList: MessageProps['detailList'] }) => {
    const intl = useIntl();
    return (
        <div className="flex justify-start pb-4 max-w-[90%] min-w-[70%]">
            <div>
                <div className="text-sm font-bold mb-2">{detailList?.app?.name}</div>
                <div className="max-w-[90%] min-w-[70%] rounded-lg relative bg-white text-gray-900 border border-gray-200 p-4">
                    <div className="flex items-center gap-2 pr-4">
                        <Spin size="small" />
                        <span className="text-gray-500">{intl.formatMessage({ id: 'agent.chat.waiting' })}</span>
                    </div>
                </div>
            </div>
        </div>
    );
});

export default memo((props: Props) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [hasMoreHistory, setHasMoreHistory] = useState(true);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [clearingMemory, setClearingMemory] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
    const formRef = useRef<ProFormInstance>();
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const intl = useIntl();

    const listenMessage = useSocketStore(state =>
        (state as unknown as WebSocketStore).getTypedMessages('chat_message_llm_return'),
    );

    const lastMessage = useSocketStore(state =>
        (state as unknown as WebSocketStore).getTypedLastMessage('chat_message_llm_return'),
    );
    console.log(props.data);
    

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    const handleSaveInfo = () => {
        if (props?.saveInfo?.firstjudgingcondition()) {
        } else if (props?.saveInfo?.secondjudgingcondition()) {
        } else {
            props?.saveInfo?.agentupdata();
        }
    };
    useUpdateEffect(() => {
        const messageData = lastMessage?.data;
        if (!messageData) return;

        const newMessage: Message = {
            ...messageData,
            id: messageData.message_id,
        };

        if (listenMessage && listenMessage.length > 0) {
            setIsWaitingForResponse(false);
            setMessages(prev => [...prev, newMessage]);
            setTimeout(scrollToBottom, 100);
        }
    }, [listenMessage]);

    const handleSubmit = async (values: { content: string }) => {
        console.log(values);
        const val = formRef.current?.getFieldsValue();
        if (!val || !values.content?.trim()) return;

        const agent_id = props.data.detailList.agent.agent_id;
        const input_dict = props.data.detailList.agent.input_variables;
        const ability_id = val.ability_id;
        const prompt = new createPromptFromObject({
            user: {
                value: val.content,
            },
        });

        const newMessage: Message = {
            id: Date.now(),
            content: values.content,
            isUser: true,
            ability_id,
            agent_id,
            agent_run_id: 0,
            completion_tokens: 0,
            created_time: new Date().toISOString(),
            message: val.content,
            prompt_tokens: 0,
            total_tokens: 0,
        };

        setIsWaitingForResponse(true);
        setMessages(prev => [...prev, newMessage]);
        formRef.current?.resetFields(['content']);

        try {
            await postAgentChatMessage({
                agent_id,
                input_dict,
                ability_id,
                prompt,
            });
        } catch (error) {
            setIsWaitingForResponse(false);
            message.error('发送消息失败，请重试');
        }

        setTimeout(scrollToBottom, 100);
    };

    const getMessageHistory = async () => {
        if (!props.data?.detailList?.agent?.agent_id) return;

        try {
            setInitialLoading(true);
            const res = await getAgentMessageHistory(
                String(props.data.detailList.agent.agent_id),
                1,
            );
            if (res.data?.list) {
                setMessages(res.data.list);
                setHasMoreHistory(res.data.total_pages > 1);
                setPage(1);
            }
        } catch (error) {
            console.error('Failed to fetch initial messages:', error);
        } finally {
            setInitialLoading(false);
        }
    };

    const fetchHistoryMessages = async () => {
        if (loading || !props.data?.detailList?.agent?.agent_id) return;

        try {
            setLoading(true);
            const nextPage = page + 1;
            const res = (await getAgentMessageHistory(
                String(props.data.detailList.agent.agent_id),
                nextPage,
            )) as ApiResponse<HistoryResponse>;

            if (res.data?.list?.length > 0) {
                setMessages(prev => [...res.data.list, ...prev]);
                setPage(nextPage);
                setHasMoreHistory(nextPage < res.data.total_pages);
            } else {
                setHasMoreHistory(false);
            }
        } catch (error) {
            console.error('Failed to load more messages:', error);
            setHasMoreHistory(false);
        } finally {
            setLoading(false);
        }
    };

    const handleClearMemory = async () => {
        if (!props.data?.detailList?.agent?.agent_id || clearingMemory || !messages.length) return;

        Modal.confirm({
            title: intl.formatMessage({ id: 'agent.chat.clear.memory.confirm.title' }),
            icon: <ExclamationCircleFilled />,
            content: intl.formatMessage({ id: 'agent.chat.clear.memory.confirm.content' }),
            okText: intl.formatMessage({ id: 'agent.chat.clear.memory.confirm.ok' }),
            cancelText: intl.formatMessage({ id: 'agent.chat.clear.memory.confirm.cancel' }),
            onOk: async () => {
                try {
                    setClearingMemory(true);
                    const lastMessageId = messages[messages.length - 1].id;
                    await clearAgentMessageMemory(
                        String(props.data.detailList.agent.agent_id),
                        lastMessageId,
                    );
                    message.success(intl.formatMessage({ id: 'agent.chat.clear.memory.success' }));
                } catch (error) {
                    console.error('Failed to clear context memory:', error);
                } finally {
                    setClearingMemory(false);
                }
            },
        });
    };

    useEffect(() => {
        if (props.data?.detailList?.agent?.agent_id) {
            getMessageHistory();
        }
    }, [props.data?.detailList?.agent?.agent_id]);

    useEffect(() => {
        if (!initialLoading && messages.length > 0) {
            scrollToBottom();
        }
    }, [initialLoading]);

    const LoadingIndicator = () => (
        <div className="flex items-center justify-center py-2 bg-white/80">
            <Spin size="small" />
            <span className="ml-2 text-sm text-gray-500">
                {intl.formatMessage({ id: 'agent.chat.loading.more' })}
            </span>
        </div>
    );

    if (initialLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <Spin />
            </div>
        );
    }
    const agentPublish = async () => {
        const res = await PutagentPublish(props.data?.detailList?.agent?.agent_id);

        if (res.code == 0) {
            message.success(intl.formatMessage({ id: 'agent.message.success.publish' }));
        } else {
            message.error(intl.formatMessage({ id: 'agent.message.fail.publish' }));
        }
    };
    return (
        <div className="!h-[calc(100vh-65px)] p-4 !pb-0 box-border">
            <ProForm
                formRef={formRef}
                submitter={false}
                onFinish={handleSubmit}
                layout="horizontal"
                initialValues={{
                    ability_id: 0,
                }}
                style={{
                    height: 'calc(100vh - 57px - 16px)',
                }}
                className="m-0 flex flex-col overflow-y-auto "
            >
                <div
                    className="pb-4 flex gap-[10px] "
                    style={{
                        paddingBottom: '16px',
                    }}
                >
                  
                    {/* <ProFormSelect
                        label={intl.formatMessage({ id: 'agent.selectivepower' })}
                        name="ability_id"
                        options={props.data?.abilitiesList}
                        fieldProps={{
                            placeholder: intl.formatMessage({ id: 'agent.pleaseselect' }),
                        }}
                        formItemProps={{
                            className: 'mb-0 flex-1',
                        }}
                    /> */}
                    <div className='flex-1 flex items-center font-bold text-base'>
                        {props.data?.detailList?.app?.name}
                    </div>
                    <Button
                        type="primary"
                        disabled={props.operationbentate == 'false' ? false : true}
                        onClick={handleSaveInfo}
                        className="min-w-24"
                    >
                        {intl.formatMessage({ id: 'agent.btn.savedebug' })}
                    </Button>
                    <Button
                        type="primary"
                        disabled={props.operationbentate == 'false' ? false : true}
                        onClick={agentPublish}
                        className="min-w-24"
                    >
                        {intl.formatMessage({ id: 'agent.publish' })}
                    </Button>
                </div>
                <div className="bg-gray-50 rounded-md border border-[#ccc] flex-1 overflow-y-auto flex flex-col">
                    <div className="flex-1 overflow-y-auto " ref={chatContainerRef}>
                        <InfiniteScroll
                            className="h-full"
                            onLoadPrevious={fetchHistoryMessages}
                            hasPrevious={hasMoreHistory}
                            hasMore={false}
                            threshold={50}
                            loadingComponent={<LoadingIndicator />}
                        >
                            <div className="px-4 py-2 space-y-4">
                                {messages.map(message =>
                                    message.agent_run_id === 0 ? (
                                        <UserMessageComponent key={message.id} message={message} />
                                    ) : (
                                        <LLMMessageComponent
                                            key={message.id}
                                            detailList={props?.data?.detailList}
                                            abilitiesList={props?.data?.abilitiesList}
                                            message={message}
                                        />
                                    ),
                                )}
                                {isWaitingForResponse && (
                                    <LoadingMessage detailList={props?.data?.detailList} />
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        </InfiniteScroll>
                    </div>

                    <div className="border-t border-gray-200 bg-white  px-4 py-2 relative">
                        
                        <div className="flex items-center p-[8px] gap-[10px] box-border border bg-white rounded-[8px]">
                            <div className="flex-1">
                                <ProFormTextArea
                                    name="content"
                                    placeholder={intl.formatMessage({
                                        id: 'agent.chat.input.placeholder',
                                    })}
                                    fieldProps={{
                                        autoSize: { minRows: 1, maxRows: 4 },
                                        variant: 'borderless',
                                        onPressEnter: e => {
                                            if (!e.shiftKey) {
                                                e.preventDefault();
                                                formRef.current?.submit();
                                            }
                                        },
                                        size: 'small',
                                        className: '',
                                        title: intl.formatMessage({ id: 'agent.chat.input.shift.enter' }),
                                    }}
                                    formItemProps={{
                                        className: 'mb-0',
                                    }}
                                    className="mb-0"
                                />
                            </div>
                            <Button
                                onClick={() => formRef.current?.submit()}
                                type="primary"
                                className="min-w-[30px] h-[30px] flex items-center justify-center cursor-pointer rounded-[6px]"
                                icon={<SendOutlined />}
                                title={intl.formatMessage({ id: 'agent.chat.send' })}
                            />
                        </div>
                        <div className="flex items-center mt-1 gap-2">
                            <ProFormSelect
                                // label={intl.formatMessage({ id: 'agent.selectivepower' })}
                                name="ability_id"
                                options={props.data?.abilitiesList}
                                fieldProps={{
                                    placeholder: intl.formatMessage({ id: 'agent.pleaseselect' }),
                                    size: 'small',
                                }}
                                formItemProps={{
                                    className: 'mb-0',
                                }}
                            />
                            <Button
                                icon={<DeleteOutlined />}
                                loading={clearingMemory}
                                onClick={handleClearMemory}
                                size="small"
                            >
                                {intl.formatMessage({ id: 'agent.chat.clear.memory' })}
                            </Button>
                        </div>
                    </div>
                </div>
            </ProForm>
        </div>
    );
});
