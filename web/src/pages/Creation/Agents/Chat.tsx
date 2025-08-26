/*
 * @LastEditors: biz
 */
/*
 * @LastEditors: biz
 */
import { getAgentMessageHistory, postAgentChatMessage, PutagentPublish } from '@/api/agents';
import { ChatRoomContent } from '@/components/ChatRoomContent';
import { ModelImageSupportProvider } from '@/contexts/ModelImageSupportContext';
import useFileUpload from '@/hooks/useFileUpload';
import { createPromptFromObject } from '@/py2js/prompt.js';
import useSocketStore from '@/store/websocket';
import { getAgentFullscreenState, setAgentFullscreenState } from '@/utils/fullscreenStorage';
import { useModelSelect } from '@/store/modelList';
import { findOption } from '@/components/WorkFlow/components/Form/Select';
import { FullscreenExitOutlined, FullscreenOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useUpdateEffect } from 'ahooks';
import { Button, Empty, message, Spin, Tag } from 'antd';
import { memo, useEffect, useRef, useState } from 'react';

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
    agent_id?: number;
    file_list?: Array<{
        name: string;
        url: string;
    }>;
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
    file_list?: Array<{
        name: string;
        url: string;
    }>;
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
                m_config_id?: number;
            };
            app?: {
                name: string;
            };
            agent_chatroom_id?: number;
            chat_status?: number;
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

export default memo((props: Props) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [hasMoreHistory, setHasMoreHistory] = useState(true);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);

    const [initialLoading, setInitialLoading] = useState(false);
    const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
    const [savingInfo, setSavingInfo] = useState(false);
    const [publishing, setPublishing] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const formRef = useRef<ProFormInstance>();
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const chatWrapperRef = useRef<HTMLDivElement>(null);
    const intl = useIntl();
    const listenMessage = useSocketStore(state =>
        (state as unknown as WebSocketStore).getTypedMessages('chat_message_llm_return'),
    );
    const [agentChatRoomId, setAgentChatRoomId] = useState(null);
    const lastMessage = useSocketStore(state =>
        (state as unknown as WebSocketStore).getTypedLastMessage('chat_message_llm_return'),
    );
    const [agentInfo, setAgentInfo] = useState(null);
    const { options } = useModelSelect();

    // Function to get model name by config ID
    const getModelName = (modelConfigId: number | string): string => {
        if (!modelConfigId || !options) return '未知模型';
        
        const modelOption = findOption(modelConfigId, { options });
        return modelOption?.label || '未知模型';
    };

    // Function to check if model supports image understanding
    const checkImageSupport = (modelConfigId: number | string): boolean => {
        if (!modelConfigId || !options) return false;
        
        const modelOption = findOption(modelConfigId, { options });
        return modelOption?.support_image === 1;
    };

    const toggleFullscreen = () => {
        const agentId = props.data?.detailList?.agent?.agent_id;
        if (agentId) {
            const newFullscreenState = !isFullscreen;
            setIsFullscreen(newFullscreenState);
            setAgentFullscreenState(agentId, newFullscreenState);
        } else {
            console.warn('Cannot save fullscreen state: agentId is not available');
            setIsFullscreen(prev => !prev);
        }
    };

    useEffect(() => {
        if (props.data?.detailList?.app?.name != undefined) {
        
            const id = props.data.detailList.agent_chatroom_id;
            const agentId = props.data.detailList.agent.agent_id;

            if (id) {
                const currentSearch = window.location.search;
                const searchParams = new URLSearchParams(currentSearch);
                setAgentChatRoomId(id);
                searchParams.set('id', String(id));

                const newUrl = `${window.location.pathname}?${searchParams.toString()}${
                    window.location.hash
                }`;
                window.history.replaceState({}, '', newUrl);
            }

            const newAgentInfo = {
                ...props.data.detailList.app,
                agent: props.data.detailList.agent,
                agent_id: agentId,
            };

         

            setAgentInfo(newAgentInfo);

            // 恢复该Agent的全屏状态
            if (agentId) {
                const savedFullscreenState = getAgentFullscreenState(agentId);
                console.log(
                    `Restoring fullscreen state for agent ${agentId}: ${savedFullscreenState}`,
                );
                setIsFullscreen(savedFullscreenState);
            }

            setTimeout(() => {
                setLoading(false);
            }, 500);
        }
    }, [props.data?.detailList?.app?.name, props.data?.detailList?.agent?.m_config_id]);

    const {
        uploadedFiles,
        setUploadedFiles,
        handleUpload: triggerUpload,
        removeFile: handleRemoveFile,
        clearFiles,
        isUploading,
    } = useFileUpload();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    const handleSaveInfo = async () => {
        try {
            setSavingInfo(true);
            if (props?.saveInfo?.firstjudgingcondition()) {
                return true;
            } else if (props?.saveInfo?.secondjudgingcondition()) {
                return true;
            } else {
                return await props?.saveInfo?.agentupdata();
            }
        } catch (error) {
            console.error('Failed to save info:', error);
            return false;
        } finally {
            setSavingInfo(false);
        }
    };
    useUpdateEffect(() => {
        const messageData = lastMessage?.data;

        if (!messageData) return;
        if (messageData?.agent_id !== props.data?.detailList?.agent?.agent_id && !message.error) {
            return;
        }

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



    useEffect(() => {
        if (!initialLoading && messages.length > 0) {
            scrollToBottom();
        }
    }, [initialLoading]);

    const handleSubmit = async (values: { content: string; file_list: string[] }) => {
      
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

        // 处理当前的上传文件
        const currentFiles = uploadedFiles.map(file => ({
            name: file.name,
            url: file.url || file.path_show || '',
        }));

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
            file_list: currentFiles.length > 0 ? currentFiles : undefined,
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
                file_list: uploadedFiles.map(file => file.file_id),
            });

            clearFiles();
        } catch (error) {
            setIsWaitingForResponse(false);
            message.error(intl.formatMessage({ id: 'agent.chat.send.failed' }));
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

    if (initialLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <Spin />
            </div>
        );
    }
    const agentPublish = async () => {
        try {
            setPublishing(true);
            await handleSaveInfo();

            setTimeout(async () => {
                try {
                    const res = await PutagentPublish(props.data?.detailList?.agent?.agent_id);

                    if (res.code == 0) {
                        message.success(
                            intl.formatMessage({ id: 'agent.message.success.publish' }),
                        );
                    } else {
                        message.error(intl.formatMessage({ id: 'agent.message.fail.publish' }));
                    }
                } catch (error) {
                    console.error('Failed to publish agent:', error);
                    message.error(intl.formatMessage({ id: 'agent.message.fail.publish' }));
                } finally {
                    setPublishing(false);
                }
            }, 500);
        } catch (error) {
            console.error('Failed to save before publish:', error);
            setPublishing(false);
        }
    };

    if (loading) {
        return null;
    }
    // return (<div className="w-full flex bg-[#fff] overflow-hidden overflow-x-auto" style={{ height: 'calc(100vh - 56px)' }}>
    //       <ChatRoomContent agentList={{
    //         current:[agentInfo]
    //       }} agentChatRoomId={agentChatRoomId}/>

    //     </div>)
    return (
        <div
            ref={chatWrapperRef}
            className={`${
                isFullscreen
                    ? 'fixed inset-0 z-50 !h-screen  border border-gray-300 top-[55px] left-0 bg-white p-4'
                    : '!h-[calc(100vh-65px)] p-4 !pb-0'
            } box-border transition-all duration-300`}
            style={{
                height: isFullscreen ? 'calc(100vh - 265px)' : 'calc(100vh - 65px)',
                backgroundColor: '#fff',
            }}
        >
            <ProForm
                formRef={formRef}
                submitter={false}
                onFinish={handleSubmit}
                layout="horizontal"
                initialValues={{
                    ability_id: 0,
                }}
                style={{
                    height: isFullscreen
                        ? 'calc(100vh - 57px - 16px)'
                        : 'calc(100vh - 57px - 16px)',
                }}
                className="m-0 flex flex-col overflow-y-auto"
            >
                <div
                    className="pb-4 flex gap-[10px] items-center"
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
                    <div className="flex-1 flex items-center font-bold text-base">
                        {props.data?.detailList?.app?.name}
                        {isFullscreen && agentInfo?.agent?.m_config_id && (
                            <div className="ml-3 flex items-center gap-2">
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-blue-700 border shadow-sm">
                                    {getModelName(agentInfo.agent.m_config_id)}{checkImageSupport(agentInfo.agent.m_config_id) && (
                                    <Tag color="blue" className="text-xs">
                                        {intl.formatMessage({
                                            id: 'workflow.tag.imageUnderstanding',
                                            defaultMessage: 'Image Understanding',
                                        })}
                                    </Tag>
                                )}
                                </span>
                                
                            </div>
                        )}
                    </div>

                    <Button
                        type="text"
                        icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                        onClick={toggleFullscreen}
                        title={intl.formatMessage({
                            id: isFullscreen
                                ? 'agent.chat.exit.fullscreen'
                                : 'agent.chat.fullscreen',
                        })}
                    />

                    {props.operationbentate == 'false' && (
                        <>
                            <Button
                                type="primary"
                                disabled={props.operationbentate == 'false' ? false : true}
                                loading={savingInfo}
                                onClick={handleSaveInfo}
                                className="min-w-24"
                            >
                                {intl.formatMessage({ id: 'agent.btn.savedebug' })}
                            </Button>
                            <Button
                                type="primary"
                                disabled={props.operationbentate == 'false' ? false : true}
                                loading={publishing || savingInfo}
                                onClick={agentPublish}
                                className="min-w-24"
                            >
                                {intl.formatMessage({ id: 'agent.publish' })}
                            </Button>
                        </>
                    )}
                </div>
                {agentChatRoomId ? (
                    <div
                        className={`w-full flex-1 flex bg-[#fff] overflow-hidden overflow-x-auto ${
                            isFullscreen ? 'max-w-[1400px] mx-auto justify-center' : ''
                        }`}
                        style={{
                            height: isFullscreen ? 'calc(100vh - 64px)' : 'calc(100vh - 56px)',
                        }}
                    >
                        <ModelImageSupportProvider>
                            <ChatRoomContent
                                agentList={{
                                    current: [agentInfo],
                                }}
                                abilitiesList={props.data?.abilitiesList}
                                agentChatRoomId={agentChatRoomId}
                                chatStatus={props.data?.detailList?.chat_status}
                            />
                        </ModelImageSupportProvider>
                    </div>
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <Empty description={`等待创建智能体`}></Empty>
                    </div>
                )}
            </ProForm>
        </div>
    );
});
