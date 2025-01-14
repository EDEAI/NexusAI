import React, { FC, memo, useEffect, useRef, useState ,ReactNode,createContext } from 'react';
import useWebSocketManager from '@//hooks/useSocket';
import { getRoomMessage, roomDetails } from '@/api/plaza';
import { headportrait, userinfodata } from '@/utils/useUser';
import { ArrowDownOutlined, PauseCircleOutlined,FileDoneOutlined,FundProjectionScreenOutlined} from '@ant-design/icons';
import useChatroomStore from '@/store/chatroomstate';
import { useIntl } from '@umijs/max';
import { Input,Spin,message} from 'antd';
import copy from 'copy-to-clipboard';
import 'highlight.js/styles/atom-one-dark.css';
import { throttle } from 'lodash';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { useParams } from 'umi';
const { TextArea } = Input;

// User enters text here
interface inputFieldParameters {
    setInstruction?: any;
    messageApi?: any;
    isStop?: any;
    scrollDomRef?: any;
    upButtonDom?: any;
}
const InputField: FC<inputFieldParameters> = memo(porpos => {
    let {
        setInstruction,
        messageApi,
        isStop,
        scrollDomRef,
        upButtonDom,
    } = porpos;
    // useIntl
    let intl = useIntl();

    const disableInput = useChatroomStore(state=>state.disableInput)

    const setDisableInput = useChatroomStore(state=>state.setDisableInput)

    // Value entered by the user
    const [userSendvalue, setUserSendvalue] = useState('');
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
            setInstruction(['INPUT', e.target.value]);
            e.preventDefault();
        }
    };
    // Pause chat
    const stopChatRoom = throttle(() => {
        setInstruction(['STOP', null]);
    }, 300);
    return (
        <>
            <div className="max-w-[920px] w-full min-h-[60px] mt-[20px] mb-[20px] mx-auto relative">
                <div
                    ref={upButtonDom}
                    className="w-[40px] h-[40px] rounded-[6px]  bg-[#fff] border border-[#ddd] cursor-pointer absolute top-[-67px] left-2/4 flex items-center justify-center hidden"
                    onClick={(e: any) => {
                        scrollDomRef.current.scrollTo({
                            top: scrollDomRef.current.scrollHeight,
                            behavior: 'smooth',
                        });
                    }}
                >
                    <ArrowDownOutlined className="text-[16px]" />
                </div>
                <div className="flex items-center p-[12px] gap-[10px] box-border border border-[#ccc] bg-[#fff] rounded-[8px]">
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
                        placeholder={`${intl.formatMessage({ id: 'app.chatroom.content.input' })}…`}
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
                                setInstruction(['INPUT', userSendvalue]);
                                setUserSendvalue('');
                            }, 300)}
                        >
                            <img src="/icons/send_icon_w.svg" alt="" className="w-[18px] h-[18px]" />
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
        </>
    );
});

const extractTextFromElement = (element:ReactNode): string => {
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
const renderers= (index: any, intl: any) => {
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
const SummaryButton:FC<{}> = porpos =>{
    let intl = useIntl();
    const setSummaryParams = useChatroomStore(state=>state.setSummaryParams);
    return (
        <div className="flex gap-x-[4px] text-[#666] hover:text-[#1B64F3]">
            <div className=" p-[2px] cursor-pointer rounded-md flex gap-x-[5px] items-center pt-[10px]" onClick={()=>{
                setSummaryParams(true)
            }}>
                <FileDoneOutlined className='text-[16px]'/>
                <span className='text-[12px]'>
                    {intl.formatMessage({ id: 'app.chatroom.content.summary' })}
                </span>
            </div>
        </div>
    );
}
const MeetingSummaryBtn:FC<{roomid:any}> = porpos =>{
    let {roomid} = porpos
    let intl = useIntl();
    const setSummaryParams = useChatroomStore(state=>state.setSummaryParams);
    return (
        <div className=" bg-[#fff]  items-center justify-center rounded-[8px] cursor-pointer" style={{boxShadow:'0px 0px 4px 0px rgba(0,0,0,0.1)'}}>
            <div className='text-[#999999] hover:text-[#1B64F3] gap-x-[4px] flex items-center justify-center h-[40px] px-[20px]' onClick={()=>{
                setSummaryParams({
                    id:roomid
                })
            }}> 
                <FundProjectionScreenOutlined className='text-[16px]'/>
                <span className='text-[14px]'>
                    {intl.formatMessage({ id: 'app.chatroom.content.meetingSummary' })}
                </span>
            </div>
        </div>
    );
}
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
    } = porpos;
    let intl = useIntl();
    // page id
    const { id } = useParams<{ id: string }>();

    const setDisableInput = useChatroomStore(state=>state.setDisableInput)

    // Current conversation
    const [currentMessage, setCurrentMessage]: any = useState({});
    // Whether the chat returns data
    const chatReturn = useRef(false);
    // Current chat text
    const agentText = useRef('');
    
    const setTruncatable = useChatroomStore(state=>state.setTruncatable)
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
                        scrollDomRef.current.scrollTop = scrollDomRef.current.scrollHeight;
                        upButtonDom.current.style.display = 'none';
                    });
                    break;
                case 'STOPPABLE':
                    setIsStop(array[1]);
                    break;
                case 'TRUNCATABLE':
                    setTruncatable(array[1]);
                    if (!array[1]) {
                        messageApi.open({
                            type: 'success',
                            content: `${intl.formatMessage({ id: 'app.chatroom.sidebar.cleartips' })}`,
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
        if (data.indexOf('--NEXUSAI-INSTRUCTION-') === -1 && chatReturn.current) {
            scrollDomRef.current.scrollTop = scrollDomRef.current.scrollHeight;
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
            if(readyState == 1){
                sendMessage(sendValue);
            }else{

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
                    {/* <div className='h-[30px]'><Avatar size={30} className='bg-[#ddd]' icon={currentMessage.icon?currentMessage.icon:<UserOutlined />}/></div> */}
                    <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] flex items-center justify-center shrink-0">
                        {currentMessage.is_agent == 1 ? (
                            <img
                                src={headportrait('single', currentMessage.icon)}
                                alt=""
                                className="w-[18px]  h-[18px]"
                            />
                        ) : (
                            <img src="/icons/user_header.svg" className="w-[18px]  h-[18px]" />
                        )}
                    </div>
                    <div className="flex1 max-w-[560px] text-right" id={`addcontent`}>
                        <div className={`${currentMessage.is_agent == 1 ?'text-left':'text-right'} font-[500] text-[14px] text-[#213044] pb-[8px]`}>
                            {currentMessage.name
                                ? currentMessage.name
                                : userinfodata('GET').nickname}
                        </div>
                        <div
                            className={`text-left inline-block markdown-container text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
                            style={
                                currentMessage.is_agent == 1
                                    ? { borderRadius: ' 0px 8px 8px 8px' }
                                    : {
                                          borderRadius: '8px 0px 8px 8px',
                                          background: 'rgba(27,100,243,0.1)',
                                          whiteSpace:'pre-wrap'
                                      }
                            }
                            id={`addchilContent`}
                        >
                            <ReactMarkdown
                                rehypePlugins={[rehypeHighlight]}
                                components={renderers('add', intl)}
                            >
                                {currentMessage.content}
                            </ReactMarkdown>
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
    } = porpos;
    let intl = useIntl();
    const [currentMessageContent, setCurrentMessageContent]: any = useState([]);
    const [isEnd, setisEnd] = useState(false);
    useEffect(() => {
        if (isEnd) {
            setUserMessage((pre: any) => {
                return [...pre, ...currentMessageContent];
            });
            setCurrentMessageContent([]);
            setTimeout(() => {
                setisEnd(false);
                scrollDomRef.current.scrollTop = scrollDomRef.current.scrollHeight;
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
                        {/* <div className='h-[30px]'><Avatar size={30} className='bg-[#ddd]' icon={item.icon?item.icon:<UserOutlined />}/></div> */}
                        <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] flex items-center justify-center shrink-0">
                            {item.is_agent == 1 ? (
                                <img
                                    src={headportrait('single', item.icon)}
                                    alt=""
                                    className="w-[18px]  h-[18px]"
                                />
                            ) : (
                                <img src="/icons/user_header.svg" className="w-[18px]  h-[18px]" />
                            )}
                        </div>
                        <div className="flex1 max-w-[560px] text-right" id={`currentContent${index}`}>
                            <div
                                className={`${item.is_agent == 1 ?'text-left':'text-right'} font-[500] text-[14px] text-[#213044] pb-[8px]`}
                            >
                                {item.name ? item.name : userinfodata('GET').nickname}
                            </div>
                            <div
                                className={`text-left inline-block markdown-container text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
                                style={
                                    item.is_agent == 1
                                        ? { borderRadius: ' 0px 8px 8px 8px' }
                                        : {
                                              borderRadius: '8px 0px 8px 8px',
                                              background: 'rgba(27,100,243,0.1)',
                                              whiteSpace:'pre-wrap'
                                              
                                          }
                                }
                                id={`currentChilContent${index}`}
                            >
                                <ReactMarkdown
                                    rehypePlugins={[rehypeHighlight]}
                                    components={renderers(index, intl)}
                                >
                                    {item.content}
                                </ReactMarkdown>
                            </div>
                            {item.is_agent == 1 ? (
                                <div className='flex gap-x-[20px]'>
                                    <Chatcopy
                                        messageApi={messageApi}
                                        index={index}
                                        idName="currentContent"
                                        cidName="currentChilContent"
                                    />
                                    <SummaryButton/>
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
    } = porpos;

    let intl = useIntl();

    const { id } = useParams<{ id: string }>();
    // const setDisableInput = useChatroomStore(state=>state.setDisableInput)
    // chat history
    const [userMessage, setUserMessage] = useState([]);
    // Whether to show the down arrow button
    const isupButtonShow = useRef(false);
    // WebSocket trigger command
    const [sendValue, setSendValue] = useState('');

    const scrollchildDomRef = useRef(null);
    // Loading
    const scrollDomload = useRef(null);
    // Whether to load on upward scroll
    const isUpload = useRef(true);

    const roomMessageContentpage = useRef(2);

    const roomMessagepage = useRef(1);
    
    const newAddLength = useRef(0)

    // Retrieve chat history
    const getChathistory = async (init: boolean, toTOP: any = () => {}) => {
        if (id) {
            let res = await getRoomMessage(id, {
                page: roomMessagepage.current,
                page_size: 20,
            });
            if (res.code == 0) {
                roomMessageContentpage.current = res.data.total_pages;
                setUserMessage(pre => {
                    return init ? [...res.data.list] : [...res.data.list, ...pre];
                });
                if (init) {
                    setTimeout(() => {
                        scrollDomRef.current.scrollTop = scrollDomRef.current.scrollHeight;
                        upButtonDom.current.style.display = 'none';
                    });
                } else {
                    newAddLength.current = res.data.list.length
                    // toTOP({ length: res.data.list.length });
                }
            }
        }
    };
    // Scroll movement
    const slideScroll = (e: any) => {
        let scrollPosition = e.target.scrollHeight - e.target.scrollTop - e.target.clientHeight;
        if (isupButtonShow.current !== Math.ceil(scrollPosition) > 50) {
            isupButtonShow.current = Math.ceil(scrollPosition) > 50;
            upButtonDom.current.style.display = isupButtonShow.current ? 'flex' : 'none';
        }
        if (e.target.scrollTop == 0 && isUpload.current) {
            isUpload.current = false;
            const firstChild = scrollchildDomRef.current.firstChild;
            roomMessagepage.current = roomMessagepage.current + 1;
            scrollDomload.current.style.display = 'flex';
            roomMessageContentpage.current;
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

    const disableInput = useChatroomStore(state=>state.disableInput)

    const clearMemory = useChatroomStore(state=>state.clearMemory)

    useEffect(()=>{
        clearMemory && clearMemory.length && setsendMessageinit(clearMemory[0],clearMemory[1])
    },[clearMemory])



    useEffect(() => {
        if (instruction && instruction.length) {
            setsendMessageinit(instruction[0], instruction[1] ? instruction[1] : '');
            setInstruction([]);
        }
    }, [instruction]);

    useEffect(() => {
        if(newAddLength.current && scrollchildDomRef.current.children[newAddLength.current]){
            scrollDomRef.current.scrollTop = scrollchildDomRef.current.children[newAddLength.current].offsetTop;
            isUpload.current = true;
        }
    }, [userMessage]);

    useEffect(() => {
        roomMessagepage.current = 1;
        getChathistory(true);
    }, []);

    return (
        <div
            className={`flex-1 box-border relative overflow-y-auto chatroom overflow-x-hidden`}
            ref={scrollDomRef}
            onScroll={slideScroll}
        >
            <div
                className="text-center justify-center items-center flex"
                style={{ display: 'none' }}
                ref={scrollDomload}
            >
                {/* <div className='loader_box'></div> */}
                <Spin />
            </div>
            <div className="max-w-[920px] mx-auto" ref={scrollchildDomRef}>
                {userMessage.map((item, index) => (
                    <div
                        key={index}
                        id={`c${item.id}`}
                        className={`w-full flex gap-[15px] pt-[15px] pb-[15px] ${
                            item.is_agent != 1 ? 'flex-row-reverse' : ''
                        }`}
                    >
                        <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] flex items-center justify-center shrink-0">
                            {item.is_agent == 1 ? (
                                <img
                                    src={headportrait('single', item.icon)}
                                    alt=""
                                    className="w-[18px]  h-[18px]"
                                />
                            ) : (
                                <img src="/icons/user_header.svg" className="w-[18px]  h-[18px]" />
                            )}
                        </div>
                        <div className="flex1 max-w-[560px] text-right" id={`content${index}`}>
                            <div
                                className={`${item.is_agent == 1 ?'text-left':'text-right'} font-[500] text-[14px] text-[#213044] pb-[8px]`}
                            >
                                {item.name ? item.name : userinfodata('GET').nickname}
                            </div>
                            <div
                                className={`text-left markdown-container inline-block text-[14px] font-[400] text-[#213044] bg-[#F7F7F7] p-[15px] pb-[1px] leading-[22px]`}
                                style={
                                    item.is_agent == 1
                                        ? { borderRadius: ' 0px 8px 8px 8px' }
                                        : {
                                              borderRadius: '8px 0px 8px 8px',
                                              background: 'rgba(27,100,243,0.1)',
                                              whiteSpace:'pre-wrap'
                                          }
                                }
                                id={`chilContent${index}`}
                            >
                                <ReactMarkdown
                                    rehypePlugins={[rehypeHighlight]}
                                    components={renderers(index, intl)}
                                >
                                    {item.content}
                                </ReactMarkdown>
                            </div>
                            {item.is_agent == 1 ? (
                                <div className='flex gap-x-[20px]'>
                                    <Chatcopy
                                        messageApi={messageApi}
                                        idName="content"
                                        cidName="chilContent"
                                        index={index}
                                    />
                                    <SummaryButton/>
                                </div>
                            ) : (
                                <></>
                            )}
                        </div>
                    </div>
                ))}
                <ChatwindowCont
                    messageApi={messageApi}
                    setUserMessage={setUserMessage}
                    sendValue={sendValue}
                    agentList={agentList}
                    scrollDomRef={scrollDomRef}
                    upButtonDom={upButtonDom}
                    setIsStop={setIsStop}
                    setSendValue={setSendValue}
                ></ChatwindowCont>
            </div>
            <div className='w-full flex justify-center pb-[10px]'>{!disableInput?<MeetingSummaryBtn roomid={id}/>:<></>}</div>
        </div>
    );
});


interface parameters{
    agentList?:any
}
export const ChatRoomContent :FC<parameters> = memo((porpos)=>{
    let {agentList} = porpos
    // Get current scroll
    const scrollDomRef = useRef(null);
    // Get DOM
    const upButtonDom = useRef(null);
    // Whether to show pause
    const [isStop, setIsStop] = useState(false);
    // Parameters to be sent
    const [instruction, setInstruction] = useState([]);
    
    const [messageApi, contextHolder] = message.useMessage();

    return (
        <>
        {contextHolder}
        <div
            className="mx-[44px] flex justify-center relative box-border pt-[12px]   overflow-auto"
            style={{ height: 'calc(100% )' }}
        >
            <div className="flex flex-col w-full">
                <ChatRoomContentbox
                    instruction={instruction}
                    setInstruction={setInstruction}
                    messageApi={messageApi}
                    scrollDomRef={scrollDomRef}
                    setIsStop={setIsStop}
                    upButtonDom={upButtonDom}
                    agentList={agentList}
                ></ChatRoomContentbox>
                <InputField
                    setInstruction={setInstruction}
                    messageApi={messageApi}
                    isStop={isStop}
                    upButtonDom={upButtonDom}
                    scrollDomRef={scrollDomRef}
                ></InputField>
            </div>
        </div>
        </>
    )
})