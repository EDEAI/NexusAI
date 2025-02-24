/*
 * @LastEditors: biz
 */
import { getAgentMessageHistory, postAgentChatMessage } from '@/api/agents';
import { createPromptFromObject } from '@/py2js/prompt.js';
import useSocketStore from '@/store/websocket';
import { SendOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useUpdateEffect } from 'ahooks';
import { Button } from 'antd';
import { memo, useEffect, useRef, useState } from 'react';

interface MessageProps {
    message: {
        id: number;
        message: string;
        agent_run_id: number;
    };
    detailList?: any;
    abilitiesList?: any;
}

const UserMessageComponent = memo(({ message }: MessageProps) => (
    <div className="flex justify-end">
        <div className="max-w-[70%] rounded-lg p-3 bg-blue-100 text-blue-900">
            {message.message}
        </div>
    </div>
));

const LLMMessageComponent = memo(({ message, detailList, abilitiesList }: MessageProps) => {
    const ability = abilitiesList.find(item => item.value === message.ability_id);
    return (
        <div className="flex justify-start pb-4">
            <div>
                <div className="text-sm font-bold mb-2">
                    {detailList?.app?.name}
                    {
                        ability?.label&&
                        <span className='text-gray-500 font-normal text-xs'>({ability?.label})</span>
                    }
                </div>
                <div className="max-w-[70%] rounded-lg  relative bg-white text-gray-900 border border-gray-200">
                    {message.message && <div className="p-3">{message.message}</div>}
                    {message.error && (
                        <div className="p-3 text-red-500">
                            <div>运行错误</div>
                            {message.error}
                        </div>
                    )}
                    <div className="absolute w-full mt-1">
                        <div className="text-xs text-gray-500 flex justify-between">
                            <div>{message.created_time}</div>
                            <div>
                                tokens:{' '}
                                <span className="text-blue-500">{message.total_tokens || 0}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
});

interface Message {
    id: number;
    content: string;
    isUser: boolean;
}

export default memo(props => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [gettedMessage, setGettedMessage] = useState(false);
    const formRef = useRef<ProFormInstance>();
    const messageContainerRef = useRef<HTMLDivElement>(null);
    const intl = useIntl();
    const listenMessage = useSocketStore(state =>
        state.getTypedMessages('chat_message_llm_return'),
    );
    const lastMessage = useSocketStore(state =>
        state.getTypedLastMessage('chat_message_llm_return'),
    );
    useUpdateEffect(() => {
        if (!lastMessage) return;
        const newMessage = {
            ...lastMessage.data,
            id: lastMessage.data.message_id,
        };

        if (listenMessage.length > 0) {
            setMessages([...messages, newMessage]);
            setTimeout(() => {
                messageContainerRef.current?.scrollTo({
                    top: messageContainerRef.current.scrollHeight,
                    behavior: 'smooth',
                });
            }, 100);
        }
    }, [listenMessage]);

    useUpdateEffect(() => {
        messageContainerRef.current?.scrollTo({
            top: messageContainerRef.current.scrollHeight,
            behavior: 'smooth',
        });
    }, [messages?.length]);

    const handleSubmit = async (values: { content: string }) => {
        console.log(values);
        const val = formRef.current.getFieldsValue();
        const agent_id = props.data.detailList.agent.agent_id;
        const input_dict = props.data.detailList.agent.input_variables;
        const ability_id = val.ability_id;
        const prompt = new createPromptFromObject({
            user: {
                value: val.content,
            },
        });
        if (!values.content?.trim()) return;

        const newMessage = {
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
        const res = await postAgentChatMessage({
            agent_id,
            input_dict,
            ability_id,
            prompt,
        });
        setMessages([...messages, newMessage]);

        formRef.current?.resetFields(['content']);
    };

    const getMessageHistory = async () => {
        const res = await getAgentMessageHistory(props.data.detailList.agent.agent_id);
        console.log(props.data);

        setGettedMessage(true);
        setMessages(res.data.list);
    };
    useEffect(() => {
        if (props.data?.detailList?.agent?.agent_id && !gettedMessage) {
            getMessageHistory();
        }
    }, [props.data.detailList]);

    return (
        <div className="flex flex-col h-full bg-gray-50">
            {/* Messages Container */}
            <ProForm
                formRef={formRef}
                submitter={false}
                onFinish={handleSubmit}
                layout="horizontal"
                initialValues={{
                    ability_id: 0,
                }}
                className="m-0 h-full flex flex-col"
            >
                <div className="p-5">
                    <ProFormSelect
                        label={intl.formatMessage({ id: 'agent.selectivepower' })}
                        name="ability_id"
                        options={props.data.abilitiesList}
                        fieldProps={{
                            placeholder: intl.formatMessage({ id: 'agent.pleaseselect' }),
                        }}
                        formItemProps={{
                            className: 'mb-0',
                        }}
                    />
                </div>
                <div
                    ref={messageContainerRef}
                    className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[calc(100vh-218px)]"
                >
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
                </div>

                {/* Input Area */}
                <div className="border-t border-gray-200 bg-white p-4">
                    <div className="flex items-center p-[12px] gap-[10px] box-border border border-[#ccc] bg-[#fff] rounded-[8px]">
                        <div className="flex-1">
                            <ProFormTextArea
                                name="content"
                                placeholder="请输入消息..."
                                fieldProps={{
                                    autoSize: { minRows: 1, maxRows: 4 },
                                    variant: 'borderless',
                                    onPressEnter: e => {
                                        if (!e.shiftKey) {
                                            e.preventDefault();
                                            formRef.current?.submit();
                                        }
                                    },
                                    className: '',
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
                            className="min-w-[30px] h-[30px]  flex items-center justify-center cursor-pointer rounded-[6px]"
                            icon={<SendOutlined />}
                        ></Button>
                    </div>
                </div>
            </ProForm>
        </div>
    );
});
