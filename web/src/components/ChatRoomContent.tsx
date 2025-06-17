import useWebSocketManager from '@//hooks/useSocket';
import { getRoomMessage } from '@/api/plaza';
import Avatar from '@/components/ChatAvatar';
import FileListDisplay from '@/components/FileListDisplay';
import useFileUpload from '@/hooks/useFileUpload';
import useChatroomStore from '@/store/chatroomstate';
import { userinfodata } from '@/utils/useUser';
import {
    ArrowDownOutlined,
    ClearOutlined,
    DownloadOutlined,
    ExclamationCircleFilled,
    FileDoneOutlined,
    FileOutlined,
    FundProjectionScreenOutlined,
    PauseCircleOutlined,
    UploadOutlined,
} from '@ant-design/icons';
import { ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Button, Image, Input, Modal, Spin, Tag, Tooltip, message } from 'antd';
import copy from 'copy-to-clipboard';
import 'highlight.js/styles/atom-one-dark.css';
import { throttle } from 'lodash';
import React, { FC, ReactNode, memo, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { useLocation, useParams } from 'umi';
const { TextArea } = Input;

const downloadFile = (url: string, filename: string) => {
    try {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {}
};

// User enters text here
interface inputFieldParameters {
    setInstruction?: any;
    messageApi?: any;
    isStop?: any;
    scrollDomRef?: any;
    upButtonDom?: any;
    abilitiesList?: any;
    agentChatRoomId?: any;
}
const InputField: FC<inputFieldParameters> = memo(porpos => {
    let {
        setInstruction,
        messageApi,
        isStop,
        scrollDomRef,
        upButtonDom,
        abilitiesList,
        agentChatRoomId,
    } = porpos;
    // useIntl
    let intl = useIntl();

    const disableInput = useChatroomStore(state => state.disableInput);
    const setDisableInput = useChatroomStore(state => state.setDisableInput);
    const [abilityId, setAbilityId] = useState(null);
    const setClearMemory = useChatroomStore(state => state.setClearMemory);
    const {
        uploadedFiles,
        handleUpload,
        removeFile: handleRemoveFile,
        clearFiles,
        isUploading,
    } = useFileUpload({
        maxSizeMB: 15,
        acceptedFileTypes: '.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.jpeg',
        multiple: true,
    });

    // Value entered by the user
    const [userSendvalue, setUserSendvalue] = useState('');
    const clearContext = () => {
        const { confirm } = Modal;
        confirm({
            title: intl.formatMessage({ id: 'app.chatroom.clear.title' }),
            icon: <ExclamationCircleFilled />,
            content: intl.formatMessage({ id: 'app.chatroom.clear.tips' }),
            okText: intl.formatMessage({ id: 'app.chatroom.clear.confirm' }),
            okType: 'danger',
            cancelText: intl.formatMessage({ id: 'app.chatroom.clear.cancel' }),
            onOk() {
                setClearMemory(['TRUNCATE', '0']);
            },
        });
    };
    // Send instructions in sequence with appropriate timing
    const sendInstructionQueue = (instructions, finalCallback) => {
        if (instructions.length === 0) {
            if (finalCallback) finalCallback();
            return;
        }

        const [currentInstruction, ...remainingInstructions] = instructions;
        setInstruction(currentInstruction);

        // Use shorter delay for better responsiveness while ensuring order
        setTimeout(() => {
            sendInstructionQueue(remainingInstructions, finalCallback);
        }, 100);
    };

    const sendMessageUseFile = message => {
        const instructions = [];

        // Build instruction queue based on current state
        if (uploadedFiles?.length > 0) {
            instructions.push(['FILELIST', uploadedFiles.map(file => file.file_id)]);
        }

        if (abilityId) {
            instructions.push(['SETABILITY', abilityId]);
        }

        instructions.push(['INPUT', message]);

        // Send instructions in sequence and clean up files after completion
        sendInstructionQueue(instructions, () => {
            if (uploadedFiles?.length > 0) {
                clearFiles();
            }
        });
    };
    // Send message
    const userSendmessage = (e: any) => {
        if (!e.shiftKey && e.target.value == '') {
            messageApi.open({
                type: 'warning',
                content: intl.formatMessage({ id: 'app.chatroom.content.input' }),
                duration: 10,
            });
            setUserSendvalue('');
            e.preventDefault();
        }
        if (!e.shiftKey && e.keyCode == 13 && e.target.value != '') {
            setDisableInput(true);
            setUserSendvalue('');
            sendMessageUseFile(e.target.value);

            e.preventDefault();
        }
    };
    // Pause chat
    const stopChatRoom = throttle(() => {
        setInstruction(['STOP', null]);
    }, 300);

    const handleFileUpload = () => {
        if (disableInput) return;
        handleUpload();
    };

    return (
        <>
            <div className="max-w-[920px] w-full min-h-[60px] mt-[20px] mb-[20px] mx-auto relative">
                <div
                    ref={upButtonDom}
                    className="w-[40px] h-[40px] rounded-[6px]  bg-[#fff] border border-[#ddd] cursor-pointer absolute top-[-67px] left-2/4 flex items-center justify-center hidden"
                    onClick={(e: any) => {
                        scrollDomRef.current.scrollTo({
                            top: 0,
                            behavior: 'smooth',
                        });
                    }}
                >
                    <ArrowDownOutlined className="text-[16px]" />
                </div>

                <Image.PreviewGroup>
                    {uploadedFiles.length > 0 && (
                        <div className="p-2 border-b border-gray-200">
                            <div className="flex flex-wrap gap-2">
                                {uploadedFiles.map(file => (
                                    <Tag
                                        key={file.uid}
                                        closable
                                        onClose={() => handleRemoveFile(file.uid)}
                                        className={`flex items-center ${
                                            file.isImage
                                                ? 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                                                : 'bg-blue-50 text-blue-600'
                                        }`}
                                    >
                                        <Tooltip title={file.name}>
                                            <div className="flex items-center">
                                                {file.isImage ? (
                                                    <div className="mr-1 flex items-center">
                                                        <Image
                                                            src={file.path_show || file.url}
                                                            alt={file.name}
                                                            className="w-6 h-6 max-w-6 max-h-6 object-cover mr-1 rounded-sm cursor-pointer"
                                                            preview={{
                                                                src: file.path_show || file.url,
                                                                mask: false,
                                                            }}
                                                        />
                                                        <span className="truncate mr-1">
                                                            {file.name}
                                                        </span>
                                                        <DownloadOutlined
                                                            className="text-gray-500 hover:text-blue-600 cursor-pointer ml-1"
                                                            onClick={e => {
                                                                e.stopPropagation();
                                                                downloadFile(
                                                                    file.path_show || file.url,
                                                                    file.name,
                                                                );
                                                            }}
                                                        />
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center">
                                                        <FileOutlined className="mr-1" />
                                                        <span className="truncate mr-1">
                                                            {file.name}
                                                        </span>
                                                        <DownloadOutlined
                                                            className="text-gray-500 hover:text-blue-600 cursor-pointer ml-1"
                                                            onClick={e => {
                                                                e.stopPropagation();
                                                                downloadFile(
                                                                    file.path_show || file.url,
                                                                    file.name,
                                                                );
                                                            }}
                                                        />
                                                    </div>
                                                )}
                                            </div>
                                        </Tooltip>
                                    </Tag>
                                ))}
                            </div>
                        </div>
                    )}
                </Image.PreviewGroup>
                <div
                    className={`border  px-[12px] py-2 border-[#ccc] bg-[#fff]  ${
                        uploadedFiles.length > 0 ? 'rounded-b-[8px]' : 'rounded-[8px]'
                    }`}
                >
                    {agentChatRoomId && (
                        <div className="flex flex-wrap gap-2 items-center mb-2">
                            {abilitiesList?.length > 0 && (
                                <ProFormSelect
                                    label={intl.formatMessage({ id: 'agent.selectivepower' })}
                                    name="ability_id"
                                    options={abilitiesList}
                                    initialValue={abilityId}
                                    fieldProps={{
                                        placeholder: intl.formatMessage({
                                            id: 'agent.pleaseselect',
                                        }),
                                        size: 'small',
                                        onChange: (value: any) => {
                                            setAbilityId(value);
                                        },
                                    }}
                                    formItemProps={{
                                        className: 'm-0',
                                    }}
                                />
                            )}

                            <Button
                                size="small"
                                color="danger"
                                variant="outlined"
                                onClick={clearContext}
                                icon={<ClearOutlined></ClearOutlined>}
                            >
                                {intl.formatMessage({ id: 'app.chatroom.sidebar.agent_button' })}
                            </Button>
                        </div>
                    )}
                    <div className={`flex items-center gap-[10px] box-border `}>
                        <Button
                            type="text"
                            icon={<UploadOutlined />}
                            onClick={handleFileUpload}
                            disabled={disableInput || isUploading}
                            loading={isUploading}
                        />

                        <TextArea
                            id="userValue"
                            className="placeholder-text-[#aaa] placeholder-text-[14px]"
                            autoSize={{ minRows: 1, maxRows: 6 }}
                            value={userSendvalue}
                            disabled={disableInput}
                            onChange={(e: any) => {
                                setUserSendvalue(e.target.value);
                            }}
                            onPressEnter={userSendmessage}
                            style={{
                                height: '34px',
                                border: 'none',
                                resize: 'none',
                                backgroundColor: 'transparent',
                            }}
                            placeholder={`${intl.formatMessage({
                                id: 'app.chatroom.content.input',
                            })}…`}
                        ></TextArea>
                        {!isStop ? (
                            <div
                                className={`${
                                    disableInput || !userSendvalue ? 'bg-[#ddd]' : 'bg-[#1B64F3]'
                                } min-w-[30px] h-[30px]  flex items-center justify-center cursor-pointer rounded-[6px]`}
                                onClick={throttle(() => {
                                    if (disableInput || !userSendvalue) return false;
                                    if (!userSendvalue) {
                                        messageApi.open({
                                            type: 'warning',
                                            content: intl.formatMessage({
                                                id: 'app.chatroom.content.input',
                                            }),
                                            duration: 10,
                                        });
                                    }
                                    setDisableInput(true);

                                    sendMessageUseFile(userSendvalue);
                                    setUserSendvalue('');
                                }, 300)}
                            >
                                <img
                                    src="/icons/send_icon_w.svg"
                                    alt=""
                                    className="w-[18px] h-[18px]"
                                />
                                {/* <EnterOutlined style={{color:'#fff',fontSize:'20px'}}/> */}
                            </div>
                        ) : (
                            <div
                                className="min-w-[34px] h-[34px] bg-[#000] flex items-center justify-center cursor-pointer rounded-[4px]"
                                onClick={stopChatRoom}
                            >
                                <PauseCircleOutlined style={{ color: '#fff', fontSize: '20px' }} />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
});

const extractTextFromElement = (element: ReactNode): string => {
    if (typeof element === 'string') {
        return element;
    }
    if (Array.isArray(element)) {
        return element.map(extractTextFromElement).join('');
    }
    if (React.isValidElement(element)) {
        return extractTextFromElement(element.props.children);
    }
    return '';
};
const extractTextFromArray = (arr: any) => {
    return extractTextFromElement(arr);
};
// Code block copy functionality
const renderers = (index: any, intl: any) => {
    // const textRef = useRef(null)
    return {
        code: ({ node, className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            if (match?.length) {
                const id = Math.random().toString(36).substr(2, 9);
                return (
                    <div className=" rounded-md border overflow-hidden">
                        <div className="flex h-12 items-center justify-between bg-zinc-100 px-4 bg-zinc-900">
                            <div className="flex items-center gap-2">
                                <p className="text-sm  text-[#fff] mb-[0]">{match[1]}</p>
                            </div>
                            <div
                                className="text-[12px] text-[#fff] mb-[0] cursor-pointer flex gap-x-[5px]"
                                onClick={async (e: any) => {
                                    try {
                                        let ct = e.currentTarget;
                                        await copy(extractTextFromArray(children));
                                        if (ct)
                                            ct.children[1].innerText = intl.formatMessage({
                                                id: 'app.chatroom.content.copySucceed',
                                            });
                                        setTimeout(() => {
                                            if (ct)
                                                ct.children[1].innerText = intl.formatMessage({
                                                    id: 'app.chatroom.content.copycode',
                                                });
                                        }, 200);
                                    } catch (err) {
                                        console.error('Failed to copy text: ', err);
                                    }
                                }}
                            >
                                <img src="/icons/chat_copy_w.svg"></img>
                                <span>
                                    {intl.formatMessage({ id: 'app.chatroom.content.copycode' })}
                                </span>
                            </div>
                        </div>
                        <div className="overflow-x-auto bg-[#282c34] text-[#abb2bf]">
                            <div id={`${id}${index}`} className="p-4">
                                {children}
                            </div>
                        </div>
                    </div>
                );
            } else {
                return <code {...props}>{children}</code>;
            }
        },
        img: ({ node, ...props }) => (
            <div className="relative group">
                <Image
                    src={props.src}
                    alt={props.alt}
                    className="max-w-full max-h-40 h-auto rounded-md"
                />
                <div className="absolute top-0 right-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                        type="primary"
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={e => {
                            e.stopPropagation();
                            downloadFile(props.src || '', props.alt || 'image.png');
                        }}
                    />
                </div>
            </div>
        ),
    };
};
// Copy entire chat
interface Chatcopyprops {
    messageApi?: any;
    index?: number;
    idName: string;
    cidName: string;
}
const Chatcopy: FC<Chatcopyprops> = memo(props => {
    let { messageApi, index, idName, cidName } = props;
    let intl = useIntl();
    const [iconHover, setIconHover] = useState(false);
    return (
        <div className="flex gap-x-[4px]">
            <div
                onMouseEnter={() => {
                    setIconHover(true);
                }}
                onMouseLeave={() => {
                    setIconHover(false);
                }}
                className=" p-[2px] cursor-pointer rounded-md flex gap-x-[5px] items-center pt-[10px]"
                onClick={async (e: any) => {
                    const dom = e.target.closest(`#${idName}${index}`);
                    const childElement = dom.querySelector(`#${cidName}${index}`);
                    try {
                        // await navigator.clipboard.writeText(childElement.innerText);
                        await copy(childElement.innerText);
                        messageApi.open({
                            type: 'success',
                            content: intl.formatMessage({ id: 'app.chatroom.content.copySucceed' }),
                            duration: 2,
                        });
                    } catch (err) {
                        console.error('Failed to copy text: ', err);
                    }
                }}
            >
                <img
                    src={`${!iconHover ? '/icons/chat_copy.svg' : '/icons/chat_copy_check.svg'}`}
                    className="w-[16px] h-[16px]"
                ></img>
                <span className={`text-[12px] ${!iconHover ? 'text-[#666]' : ' text-[#1B64F3]'}`}>
                    {intl.formatMessage({ id: 'app.chatroom.content.copy' })}
                </span>
            </div>
        </div>
    );
});
const SummaryButton: FC<{ id: any; index?: number; idName: string; cidName: string }> = porpos => {
    let { id, index, idName, cidName } = porpos;
    let intl = useIntl();
    const setSummaryClick = useChatroomStore(state => state.setSummaryClick);
    const [disabled, setDisabled] = useState(true);
    const summaryClick = useChatroomStore(state => state.summaryClick);
    useEffect(() => {
        setDisabled(summaryClick);
    }, [summaryClick]);
    const setSummaryParams = useChatroomStore(state => state.setSummaryParams);
    return (
        <div
            className={`flex gap-x-[4px] text-[#666] ${
                disabled ? 'cursor-pointer hover:text-[#1B64F3]' : 'cursor-no-drop'
            }`}
        >
            <div
                className=" p-[2px]  rounded-md flex gap-x-[5px] items-center pt-[10px]"
                onClick={(e: any) => {
                    if (disabled) {
                        const dom = e.target.closest(`#${idName}${index}`);
                        const childElement = dom.querySelector(`#${cidName}${index}`);
                        setSummaryParams({ id: id, message: childElement.innerText });
                        // setDisabled(false)
                        setSummaryClick(false);
                    }
                }}
            >
                <FileDoneOutlined className="text-[16px]" />
                <span className="text-[12px]">
                    {intl.formatMessage({ id: 'app.chatroom.content.summary' })}
                </span>
            </div>
        </div>
    );
};
const MeetingSummaryBtn: FC<{ roomid: any }> = porpos => {
    let { roomid } = porpos;
    let intl = useIntl();
    const setSummaryClick = useChatroomStore(state => state.setSummaryClick);
    const [disabled, setDisabled] = useState(true);
    const summaryClick = useChatroomStore(state => state.summaryClick);
    useEffect(() => {
        setDisabled(summaryClick);
    }, [summaryClick]);
    const setSummaryParams = useChatroomStore(state => state.setSummaryParams);
    return (
        <div
            className={`bg-[#fff] text-[#999999]   items-center justify-center rounded-[8px] ${
                disabled ? 'cursor-pointer hover:text-[#1B64F3]' : 'cursor-no-drop'
            }`}
            style={{ boxShadow: '0px 0px 4px 0px rgba(0,0,0,0.1)' }}
        >
            <div
                className=" gap-x-[4px] flex items-center justify-center h-[40px] px-[20px]"
                onClick={() => {
                    if (disabled) {
                        setSummaryParams({
                            id: roomid,
                        });
                        // setDisabled(false)
                        setSummaryClick(false);
                    }
                }}
            >
                <FundProjectionScreenOutlined className="text-[16px]" />
                <span className="text-[14px]">
                    {intl.formatMessage({ id: 'app.chatroom.content.meetingSummary' })}
                </span>
            </div>
        </div>
    );
};
// Current agent speaking
interface chatwindowParameters {
    setisEnd?: any;
    messageApi?: any;
    setCurrentMessageContent?: any;
    sendValue?: any;
    agentList?: any;
    scrollDomRef?: any;
    upButtonDom?: any;
    setIsStop?: any;
    setSendValue?: any;
    agentChatRoomId?: any;
}
const Chatwindow: FC<chatwindowParameters> = memo(porpos => {
    let {
        messageApi,
        setCurrentMessageContent,
        sendValue,
        agentList,
        scrollDomRef,
        upButtonDom,
        setIsStop,
        setisEnd,
        setSendValue,
        agentChatRoomId,
    } = porpos;
    let intl = useIntl();
    // page id
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');
    // Use URL param id if available, otherwise use search param id
    const id = agentChatRoomId || urlParamId || searchParamId;

    const setDisableInput = useChatroomStore(state => state.setDisableInput);

    // Current conversation
    const [currentMessage, setCurrentMessage]: any = useState({});
    // Whether the chat returns data
    const chatReturn = useRef(false);
    // Current chat text
    const agentText = useRef('');

    const setTruncatable = useChatroomStore(state => state.setTruncatable);
    // Get the value returned by WebSocket
    const getSocketMessage = (message: any) => {
        let data = message.data;
        if (data.indexOf('--NEXUSAI-INSTRUCTION-') !== -1) {
            let array = JSON.parse(data.slice(22, -2));
            switch (array[0]) {
                case 'ERROR':
                    setDisableInput(false);
                    setIsStop(false);
                    setSendValue('');
                    messageApi.open({
                        type: 'error',
                        content: `webSocket-${array[1]}`,
                        duration: 10,
                    });
                    break;
                case 'CHAT':
                    let userObj = {
                        content: `${array[1]}`,
                        is_agent: 0,
                    };
                    setCurrentMessageContent((pre: any) => {
                        return [...pre, userObj];
                    });
                    setTimeout(() => {
                        scrollDomRef.current.scrollTop = 0;
                        upButtonDom.current.style.display = 'none';
                    });
                    break;
                case 'WITHFILELIST':
                    setCurrentMessageContent((pre: any) => {
                        const newPre = [...pre];
                        if (newPre.length) {
                            newPre[newPre.length - 1].file_list = array[1];
                        }

                        return newPre;
                    });
                    setTimeout(() => {
                        scrollDomRef.current.scrollTop = 0;
                        upButtonDom.current.style.display = 'none';
                    });
                    break;
                // case 'ABILITY':
                //     setCurrentMessageContent((pre: any) => {
                //         const newPre = [...pre];
                //         if (newPre.length) {
                //             newPre[newPre.length - 1].ability_id = array[1];
                //         }
                //         debugger
                //         return newPre;
                //     });
                //     break;
                case 'STOPPABLE':
                    setIsStop(array[1]);
                    break;
                case 'TRUNCATABLE':
                    setTruncatable(array[1]);
                    if (!array[1]) {
                        messageApi.open({
                            type: 'success',
                            content: `${intl.formatMessage({
                                id: 'app.chatroom.sidebar.cleartips',
                            })}`,
                            duration: 3,
                        });
                    }
                    break;
                case 'TRUNCATEOK':
                    messageApi.open({
                        type: 'success',
                        content: `${intl.formatMessage({ id: 'app.chatroom.sidebar.cleartips' })}`,
                        duration: 3,
                    });
                    break;
            }
        }
        if (data.indexOf('REPLY') !== -1) {
            if (data.indexOf('--NEXUSAI-INSTRUCTION-') !== -1) {
                let agentId = JSON.parse(data.slice(22, -2))[1];
                agentText.current = '';
                chatReturn.current = true;

                let currentAgent = agentList.current.filter(
                    (item: any) => item.agent_id == agentId,
                )[0];
                if (Object.keys(currentMessage).length) {
                    setCurrentMessageContent((pre: any) => {
                        return [...pre, currentMessage];
                    });
                }
                setCurrentMessage((pre: any) => {
                    return {
                        ...pre,
                        is_agent: 1,
                        icon: currentAgent?.icon,
                        name: currentAgent?.name,
                    };
                });
                setIsStop(true);
                setTruncatable(false);
            }
        }

        if (data.indexOf('ABILITY') !== -1) {
            if (data.indexOf('--NEXUSAI-INSTRUCTION-') !== -1) {
                let ability_id = JSON.parse(data.slice(22, -2))[1];

                setCurrentMessage((pre: any) => {
                    return {
                        ...pre,
                        is_agent: 1,
                        ability_id: ability_id,
                    };
                });
            }
        }
        if (data.indexOf('--NEXUSAI-INSTRUCTION-') === -1 && chatReturn.current) {
            scrollDomRef.current.scrollTop = 0;
            upButtonDom.current.style.display = 'none';
            agentText.current += data;
            setCurrentMessage((pre: any) => {
                return {
                    ...pre,
                    content: agentText.current,
                };
            });
        }
        if (data.indexOf('ENDCHAT') !== -1) {
            chatReturn.current = false;
            agentText.current = '';
            setDisableInput(false);
            setIsStop(false);
            setTruncatable(true);
            if (Object.keys(currentMessage).length) {
                setCurrentMessageContent((pre: any) => {
                    return [...pre, currentMessage];
                });
            }
            setCurrentMessage({});
            setisEnd(true);
            setSendValue('');
        }
    };
    // webSockt
    const { runSocket, sendMessage, readyState } = useWebSocketManager('chat', getSocketMessage);
    useEffect(() => {
        if (readyState == 1) {
            if (id) {
                sendMessage(JSON.stringify(['ENTER', parseInt(id)]));
            }
        }
    }, [readyState]);

    useEffect(() => {
        if (sendValue) {
            if (readyState == 1) {
                sendMessage(sendValue);
            } else {
            }
        }
    }, [sendValue]);

    useEffect(() => {
        runSocket();
    }, []);

    return (
        <>
            {currentMessage.name ? (
                <div
                    className={`w-full flex gap-[15px] pt-[15px] pb-[15px] ${
                        currentMessage.is_agent != 1 ? 'flex-row-reverse' : ''
                    }`}
                >
                    {currentMessage.is_agent == 1 ? (
                        <Avatar data={currentMessage} />
                    ) : (
                        <Avatar data={{ avatar: '/icons/user_header.svg' }} />
                    )}
                    <div
                        className={`flex1 ${agentChatRoomId ? '' : 'max-w-[560px]'} text-right`}
                        id={`addcontent`}
                    >
                        <div
                            className={`${
                                currentMessage.is_agent == 1 ? 'text-left' : 'text-right'
                            } font-[500] text-[14px] text-[#213044] pb-[8px]`}
                        >
                            {currentMessage.name
                                ? currentMessage.name
                                : userinfodata('GET').nickname}
                        </div>
                        <div
                            className={`flex ${
                                currentMessage.is_agent == 1 ? 'flex-row' : 'flex-row-reverse'
                            }`}
                        >
                            <div
                                className={`text-left inline-block markdown-container text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
                                style={
                                    currentMessage.is_agent == 1
                                        ? { borderRadius: ' 0px 8px 8px 8px' }
                                        : {
                                              borderRadius: '8px 0px 8px 8px',
                                              background: 'rgba(27,100,243,0.1)',
                                              whiteSpace: 'pre-wrap',
                                          }
                                }
                                id={`addchilContent`}
                            >
                                {currentMessage.file_list &&
                                    currentMessage.file_list.length > 0 && (
                                        <div className="mb-3">
                                            <FileListDisplay
                                                fileList={currentMessage.file_list}
                                                onDownload={downloadFile}
                                            />
                                        </div>
                                    )}
                                <ReactMarkdown
                                    rehypePlugins={[rehypeHighlight]}
                                    components={renderers('add', intl)}
                                >
                                    {currentMessage.content}
                                </ReactMarkdown>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <></>
            )}
        </>
    );
});

interface chatwindowContParameters {
    messageApi?: any;
    setUserMessage?: any;
    sendValue?: any;
    agentList?: any;
    scrollDomRef?: any;
    upButtonDom?: any;
    setIsStop?: any;
    setSendValue?: any;
    agentChatRoomId?: any;
    abilitiesList?: any;
}
// Current round of speaking until the end of this round is merged into the main array
const ChatwindowCont: React.FC<chatwindowContParameters> = memo(porpos => {
    let {
        messageApi,
        setUserMessage,
        sendValue,
        agentList,
        scrollDomRef,
        upButtonDom,
        setIsStop,
        setSendValue,
        agentChatRoomId,
        abilitiesList,
    } = porpos;
    let intl = useIntl();
    const [currentMessageContent, setCurrentMessageContent]: any = useState([]);
    const [isEnd, setisEnd] = useState(false);
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');
    // Use URL param id if available, otherwise use search param id
    const id = urlParamId || searchParamId;
    useEffect(() => {
        if (isEnd) {
            setUserMessage((pre: any) => {
                return [...currentMessageContent.reverse(), ...pre];
            });
            setCurrentMessageContent([]);
            setTimeout(() => {
                setisEnd(false);
                scrollDomRef.current.scrollTop = 0;
            }, 200);
        }
    }, [isEnd]);
    return (
        <>
            {currentMessageContent.length ? (
                currentMessageContent.map((item: any, index: any) => (
                    <div
                        key={index}
                        className={`w-full flex gap-[15px] pt-[15px] pb-[15px] ${
                            item.is_agent != 1 ? 'flex-row-reverse' : ''
                        }`}
                    >
                        {item.is_agent == 1 ? (
                            <Avatar data={item} />
                        ) : (
                            <Avatar data={{ avatar: '/icons/user_header.svg' }} />
                        )}
                        <div
                            className={`flex1 ${agentChatRoomId ? '' : 'max-w-[560px]'} text-right`}
                            id={`currentContent${index}`}
                        >
                            <div
                                className={`${
                                    item.is_agent == 1 ? 'text-left' : 'text-right'
                                } font-[500] text-[14px] text-[#213044] pb-[8px]`}
                            >
                                {item.name ? item.name : userinfodata('GET').nickname}
                                {item.name && item.ability_id > 0 && (
                                    <>
                                        {' '}
                                        (
                                        {abilitiesList.find(x => item.ability_id == x.value)
                                            ?.label || '未找到该能力'}
                                        )
                                    </>
                                )}
                            </div>
                            <div
                                className={`flex ${
                                    item.is_agent == 1 ? 'flex-row' : 'flex-row-reverse'
                                }`}
                            >
                                <div
                                    className={`text-left inline-block markdown-container text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
                                    style={
                                        item.is_agent == 1
                                            ? { borderRadius: ' 0px 8px 8px 8px' }
                                            : {
                                                  borderRadius: '8px 0px 8px 8px',
                                                  background: 'rgba(27,100,243,0.1)',
                                                  whiteSpace: 'pre-wrap',
                                              }
                                    }
                                    id={`currentChilContent${index}`}
                                >
                                    {item.file_list && item.file_list.length > 0 && (
                                        <div className="mb-3">
                                            <FileListDisplay
                                                fileList={item.file_list}
                                                onDownload={downloadFile}
                                            />
                                        </div>
                                    )}
                                    <ReactMarkdown
                                        rehypePlugins={[rehypeHighlight]}
                                        components={renderers(index, intl)}
                                    >
                                        {item.content}
                                    </ReactMarkdown>
                                </div>
                            </div>
                            {item.is_agent == 1 ? (
                                <div className="flex gap-x-[20px]">
                                    <Chatcopy
                                        messageApi={messageApi}
                                        index={index}
                                        idName="currentContent"
                                        cidName="currentChilContent"
                                    />
                                    {!agentChatRoomId && (
                                        <SummaryButton
                                            id={id}
                                            index={index}
                                            idName="currentContent"
                                            cidName="currentChilContent"
                                        />
                                    )}
                                </div>
                            ) : (
                                <></>
                            )}
                        </div>
                    </div>
                ))
            ) : (
                <></>
            )}
            <Chatwindow
                messageApi={messageApi}
                setCurrentMessageContent={setCurrentMessageContent}
                sendValue={sendValue}
                agentList={agentList}
                scrollDomRef={scrollDomRef}
                upButtonDom={upButtonDom}
                setIsStop={setIsStop}
                setisEnd={setisEnd}
                setSendValue={setSendValue}
                agentChatRoomId={agentChatRoomId}
            ></Chatwindow>
        </>
    );
});

interface contentParameters {
    instruction?: any;
    setInstruction?: any;
    messageApi?: any;
    scrollDomRef?: any;
    setIsStop?: any;
    upButtonDom?: any;
    agentList?: any;
    agentChatRoomId?: any;
    abilitiesList?: any;
}
// Main section
const ChatRoomContentbox: FC<contentParameters> = memo(porpos => {
    let {
        messageApi,
        scrollDomRef,
        instruction,
        setIsStop,
        upButtonDom,
        setInstruction,
        agentList,
        agentChatRoomId,
        abilitiesList,
    } = porpos;

    let intl = useIntl();

    const [bminWidth, setbminWidth] = useState(860);

    // Get both URL params and search params
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');

    // Use URL param id if available, otherwise use search param id
    const id = agentChatRoomId || urlParamId || searchParamId;

    // const setDisableInput = useChatroomStore(state=>state.setDisableInput)
    // chat history
    const [userMessage, setUserMessage] = useState([]);
    // Whether to show the down arrow button
    const isupButtonShow = useRef(false);
    // WebSocket trigger command
    const [sendValue, setSendValue] = useState('');
    // Loading
    const scrollDomload = useRef(null);
    // Whether to load on upward scroll
    const isUpload = useRef(true);

    const roomMessageContentpage = useRef(2);

    const roomMessagepage = useRef(1);

    const newAddLength = useRef(0);

    // Retrieve chat history
    const getChathistory = async (init: boolean, toTOP: any = () => {}) => {
        if (id) {
            let res = await getRoomMessage(id, {
                page: roomMessagepage.current,
                page_size: 10,
            });
            if (res.code == 0) {
                roomMessageContentpage.current = res.data.total_pages;
                if (!init) {
                    scrollDomload.current.style.display = 'none';
                }
                setUserMessage(pre => {
                    return init
                        ? [...res.data.list.reverse()]
                        : [...pre, ...res.data.list.reverse()];
                });
                if (init) {
                    if (scrollDomRef && scrollDomRef.current) {
                        setTimeout(() => {
                            scrollDomRef.current.scrollTop = 0;
                            upButtonDom.current.style.display = 'none';
                        });
                    }
                } else {
                    newAddLength.current = res.data.list.length;
                    // toTOP({ length: res.data.list.length });
                }
                isUpload.current = true;
            }
        }
    };
    // Scroll movement
    const slideScroll = (e: any) => {
        let scrollPosition = e.target.scrollHeight + (e.target.scrollTop - e.target.clientHeight);
        if (isupButtonShow.current !== Math.ceil(e.target.scrollTop) < -50) {
            isupButtonShow.current = Math.ceil(e.target.scrollTop) < -50;
            upButtonDom.current.style.display = isupButtonShow.current ? 'flex' : 'none';
        }
        if (scrollPosition < 10 && isUpload.current) {
            isUpload.current = false;
            roomMessagepage.current = roomMessagepage.current + 1;
            scrollDomload.current.style.display = 'flex';
            if (roomMessageContentpage.current >= roomMessagepage.current) {
                getChathistory(false);
            } else {
                scrollDomload.current.style.display = 'none';
            }
        }
    };
    // WebSocket send command
    const setsendMessageinit = (type: string, value: any) => {
        if (value === '0') value = Number(value);
        let initChatRoomstok = [`${type}`, value === 0 || value ? value : null];
        setSendValue(JSON.stringify(initChatRoomstok));
    };

    const disableInput = useChatroomStore(state => state.disableInput);

    const clearMemory = useChatroomStore(state => state.clearMemory);

    useEffect(() => {
        clearMemory && clearMemory.length && setsendMessageinit(clearMemory[0], clearMemory[1]);
    }, [clearMemory]);

    useEffect(() => {
        if (instruction && instruction.length) {
            setsendMessageinit(instruction[0], instruction[1] ? instruction[1] : '');
            setInstruction([]);
        }
    }, [instruction]);

    useEffect(() => {
        roomMessagepage.current = 1;
        getChathistory(true);
    }, []);
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 1280) {
            } else {
                setbminWidth(window.innerWidth - 320 - (window.innerWidth - 320) / 2 - 88);
            }
        };

        handleResize();

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);
    return (
        <div className="flex-1 min-h-0">
            <div
                className={`h-full min-h-full overflow-y-auto flex flex-col-reverse  items-center  scroll-smooth chatroom`}
                ref={scrollDomRef}
                onScroll={slideScroll}
            >
                <div style={{ minWidth: agentChatRoomId ? '' : `${bminWidth}px` }}>
                    <div className="w-full">
                        <div className="flex flex-col-reverse">
                            <>
                                {userMessage && userMessage.length ? (
                                    userMessage.map((item, index) => (
                                        <div
                                            key={index}
                                            id={`c${item.id}`}
                                            className={`w-full flex gap-[15px] pt-[15px] pb-[15px] ${
                                                item.is_agent != 1 ? 'flex-row-reverse' : ''
                                            }`}
                                        >
                                            {item.is_agent == 1 ? (
                                                <Avatar data={item} />
                                            ) : (
                                                <Avatar
                                                    data={{ avatar: '/icons/user_header.svg' }}
                                                />
                                            )}
                                            <div
                                                className={`flex1 ${
                                                    agentChatRoomId ? '' : 'max-w-[560px]'
                                                } text-right`}
                                                id={`content${index}`}
                                            >
                                                <div
                                                    className={`${
                                                        item.is_agent == 1
                                                            ? 'text-left'
                                                            : 'text-right'
                                                    } font-[500] text-[14px] text-[#213044] pb-[8px]`}
                                                >
                                                    {item.name
                                                        ? item.name
                                                        : userinfodata('GET').nickname}
                                                    {item.ability_id > 0 && (
                                                        <>
                                                            {' '}
                                                            (
                                                            {abilitiesList.find(
                                                                x => item.ability_id == x.value,
                                                            )?.label ||
                                                                intl.formatMessage({
                                                                    id: 'app.chatroom.content.abilityNotFound',
                                                                })}
                                                            )
                                                        </>
                                                    )}
                                                </div>
                                                <div
                                                    className={`flex ${
                                                        item.is_agent == 1
                                                            ? 'flex-row'
                                                            : 'flex-row-reverse'
                                                    }`}
                                                >
                                                    <div
                                                        className={`text-left inline-block markdown-container text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
                                                        style={
                                                            item.is_agent == 1
                                                                ? {
                                                                      borderRadius:
                                                                          ' 0px 8px 8px 8px',
                                                                  }
                                                                : {
                                                                      borderRadius:
                                                                          '8px 0px 8px 8px',
                                                                      background:
                                                                          'rgba(27,100,243,0.1)',
                                                                      whiteSpace: 'pre-wrap',
                                                                  }
                                                        }
                                                        id={`chilContent${index}`}
                                                    >
                                                        {item.file_list &&
                                                            item.file_list.length > 0 && (
                                                                <div className="mb-3">
                                                                    <FileListDisplay
                                                                        fileList={item.file_list}
                                                                        onDownload={downloadFile}
                                                                    />
                                                                </div>
                                                            )}
                                                        <ReactMarkdown
                                                            rehypePlugins={[rehypeHighlight]}
                                                            components={renderers(index, intl)}
                                                        >
                                                            {item.content}
                                                        </ReactMarkdown>
                                                    </div>
                                                </div>
                                                {item.is_agent == 1 ? (
                                                    <div className="flex gap-x-[20px]">
                                                        <Chatcopy
                                                            messageApi={messageApi}
                                                            idName="content"
                                                            cidName="chilContent"
                                                            index={index}
                                                        />
                                                        {!agentChatRoomId && (
                                                            <SummaryButton
                                                                id={id}
                                                                index={index}
                                                                idName="content"
                                                                cidName="chilContent"
                                                            />
                                                        )}
                                                    </div>
                                                ) : (
                                                    <></>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <></>
                                )}
                            </>
                        </div>
                        <ChatwindowCont
                            messageApi={messageApi}
                            setUserMessage={setUserMessage}
                            sendValue={sendValue}
                            agentList={agentList}
                            scrollDomRef={scrollDomRef}
                            upButtonDom={upButtonDom}
                            setIsStop={setIsStop}
                            setSendValue={setSendValue}
                            agentChatRoomId={agentChatRoomId}
                            abilitiesList={abilitiesList}
                        ></ChatwindowCont>
                    </div>
                    <div className="w-full flex justify-center pb-[10px]">
                        {!agentChatRoomId && !disableInput && userMessage.length ? (
                            <MeetingSummaryBtn roomid={id} />
                        ) : (
                            <></>
                        )}
                    </div>
                </div>
                <div
                    className="text-center justify-center items-center flex"
                    style={{ display: 'none' }}
                    ref={scrollDomload}
                >
                    <Spin />
                </div>
            </div>
        </div>
    );
});

interface parameters {
    agentList?: any;
    agentChatRoomId?: any;
    abilitiesList?: any;
}
export const ChatRoomContent: FC<parameters> = memo(porpos => {
    let { agentList, agentChatRoomId, abilitiesList } = porpos;
    // Get current scroll
    const scrollDomRef = useRef(null);
    // Get DOM
    const upButtonDom = useRef(null);
    // Whether to show pause
    const [isStop, setIsStop] = useState(false);
    // Parameters to be sent
    const [instruction, setInstruction] = useState([]);
    // Get both URL params and search params
    const { id: urlParamId } = useParams<{ id: string }>();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchParamId = searchParams.get('id');
    // Use URL param id if available, otherwise use search param id
    const id = urlParamId || searchParamId;

    const [messageApi, contextHolder] = message.useMessage();

    return (
        <>
            {contextHolder}
            <div
                className={`mx-[44px] flex justify-center relative box-border pt-[12px] h-full ${
                    agentChatRoomId ? 'w-full' : ''
                }`}
            >
                <div className="flex flex-col w-full h-full">
                    <ChatRoomContentbox
                        instruction={instruction}
                        setInstruction={setInstruction}
                        messageApi={messageApi}
                        scrollDomRef={scrollDomRef}
                        setIsStop={setIsStop}
                        upButtonDom={upButtonDom}
                        agentList={agentList}
                        agentChatRoomId={agentChatRoomId}
                        abilitiesList={abilitiesList}
                    ></ChatRoomContentbox>
                    <InputField
                        setInstruction={setInstruction}
                        messageApi={messageApi}
                        isStop={isStop}
                        upButtonDom={upButtonDom}
                        scrollDomRef={scrollDomRef}
                        agentChatRoomId={agentChatRoomId}
                        abilitiesList={abilitiesList}
                    ></InputField>
                </div>
            </div>
        </>
    );
});
