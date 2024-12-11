// import Scroll from '@/components/InfiniteScroll';
import { roomDetails, roomRecent, upAgentStatus, updataRoom, upRoomStatus } from '@/api/plaza';
import { headportrait } from '@/utils/useUser';
import { ArrowLeftOutlined, EllipsisOutlined, QuestionCircleOutlined,ExclamationCircleFilled } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Empty, Spin, Switch, Tooltip,Modal } from 'antd';
import { throttle } from 'lodash';
import { memo, useEffect, useRef, useState } from 'react';
import { history, useParams } from 'umi';
import Agent from '../CreationChatRoom/agent';
interface siderPm {
    setsendMessage: any;
    truncatable?: any;
    messageApi?: any;
    roomDetail?: any;
    disableInput?: any;
    setAgent?:any
}

const Sider: React.FC<siderPm> = porpos => {
    const intl = useIntl();

    let { setsendMessage, truncatable, messageApi, roomDetail, disableInput,setAgent } = porpos;

    const { id } = useParams<{ id: string }>();

    const [agentList, setAgentList] = useState([]);
    // Chat room details
    const [chatRoomdetial, setchatRoomdetial] = useState({ ...roomDetail });
    // RoomRecent - recently viewed room list
    const [roomRecentList, setRoomRecentList] = useState([]);

    const agentLoading = useRef(false);

    const roomLoading = useRef(false);

    // Show or hide popup
    const [agentShow, setAgentShow] = useState(false);

    // Clear memory
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
                setsendMessage('TRUNCATE', '0');
            },
        });
    };
    // Get agent_list details
    const getRoomDetails = async () => {
        if (id) {
            let res = await roomDetails({ id });
            if (res.code == 0) {
                try {
                    setchatRoomdetial(() => {
                        return {
                            ...res.data.chat_info,
                            max_round: res.data.max_round,
                            smart_selection: res.data.smart_selection,
                        };
                    });
                    setAgentList(res.data.agent_list);
                    agentLoading.current = true;
                } catch (error) {}
            }
        }
    };
    // Get recently viewed room list
    const getRoomRecent = async () => {
        let res = await roomRecent({ id });
        if (res.code == 0) {
            setRoomRecentList(res.data.list);
            roomLoading.current = true;
        }
    };
    // Enable or disable agent auto-response
    const openRoomAgentstatus = async (item: any) => {
        if (id) {
            let active: number = item.active == 1 ? 0 : 1;
            if(active == 0){
               let  agentLength =  agentList.filter(item=>item.active == 1)
               if(agentLength.length - 1 == 0){
                    messageApi.open({
                        type: 'error',
                        content: intl.formatMessage({ id: 'app.chatroom.sidebar.agent_tips' }),
                        duration: 2,
                    });
                    return false
               }
               
            }
            let res = await upAgentStatus({ active: active }, id, item.agent_id);
            if (res.code == 0) {
                setAgentList((pre: any) => {
                    return pre.map((x: any) => {
                        return {
                            ...x,
                            active: x.agent_id == item.agent_id ? active : x.active,
                        };
                    });
                });
            }
        }
    };
    // getAgentList
    const getAgentList = (arr: any) => {
        arr.length > 6 ? (arr.length = 6) : arr.lenth;
        return arr;
    };
    // Navigate to agent
    const jumpAgentDetial = (item: any) => {
        if (item.type == 'my_agent') {
            history.push(`/Agents?app_id=${item.app_id}&type=false&from=chat_room`);
        } else {
            history.push(`/ReadOnlyAgent?app_id=${item.app_id}&type=true&from=chat_room`);
        }
    };
    // Navigate to agent
    const jumpChatRoom = (item: any) => {
        history.replace(`/chat_room/${item.chatroom_id}`);
        window.location.reload();
    };
    // add agent
    const addAgent = () => {
        setAgentShow(true);
    };
    // agent popup Close
    const popupClose = () => {
        setAgentShow(false);
    };
    // agent popup Save
    const popupSave = async (obj: any) => {
        let agentList = [...obj.checkAgent].map(({ agent_id, active = 1 }) => ({
            agent_id,
            active,
        }));
        let updataObject = {
            description: chatRoomdetial.description,
            name: chatRoomdetial.name,
            max_round: chatRoomdetial.max_round,
        };
        let res = await updataRoom({ ...updataObject, agent: agentList }, id);
        if (res.code == 0) {
            obj.checkAgent.map((item: any) => {
                item.active = item.active == undefined ? 1 : item.active;
            });
            setAgentList([...obj.checkAgent]);
            setAgent.current = [...obj.checkAgent]
            messageApi.open({
                type: 'success',
                content: intl.formatMessage({ id: 'app.chatroom.content.addAgentTips' }),
                duration: 2,
            });
        } else {
            messageApi.open({
                type: 'error',
                content: intl.formatMessage({ id: 'app.chatroom.content.addAgentTips_fail' }),
                duration: 2,
            });
        }
    };
    const openRoomstatus = async () => {
        let smart_selection = chatRoomdetial.smart_selection == 1 ? 0 : 1;
        await upRoomStatus({ smart_selection: smart_selection }, id);
        setchatRoomdetial((pre: any) => {
            return {
                ...pre,
                smart_selection: smart_selection,
            };
        });
    };
    useEffect(() => {
        getRoomDetails();
        getRoomRecent();
    }, []);

    return (
        <>
            <div
                className="h-full w-[320px] bg-[#fff] shrink-0"
                style={{ boxShadow: '0px 2px 4px 0px rgba(0,0,0,0.1)' }}
                id="sider"
            >
                <div className="flex flex-col  h-full">
                    <div className="w-full flex  justify-start px-[30px]">
                        <div className="py-[20px] text-[14px] text-[#213044] font-[500] flex gap-x-[10px] items-center w-full">
                            <div
                                className="cursor-pointer flex items-center shrink-0"
                                onClick={() => {
                                    history.go(-1);
                                }}
                            >
                                <Button type="link" danger className="p-0">
                                    <ArrowLeftOutlined className="text-[#1B64F3] w-[16px] h-[16px]" />
                                </Button>
                                <span className="ml-[5px] text-[#213044] text-sm">
                                    {intl.formatMessage({ id: 'app.chatroom.sidebar.return' })}
                                </span>
                            </div>
                            <div className="h-full flex items-center shrink-0">
                                <div className="w-[1px] h-[13px] bg-[#ebebeb]"></div>
                            </div>
                            <div className="flex-1 min-w-0 truncate">{chatRoomdetial.name}</div>
                        </div>
                    </div>
                    {/* <div className='pb-[20px] text-[14px] text-[#213044] font-[500] px-[30px]'>{chatRoomdetial.name}</div> */}
                    <div className="h-[327px]">
                        <div className="pb-[20px] border-b-[1px] px-[10px]">
                            <div className="flex items-center cursor-pointer px-[20px]">
                                <div className="flex gap-x-[5px] flex-1">
                                    <span className="text-[#666] text-[14px]">
                                        {intl.formatMessage({
                                            id: 'app.chatroom.sidebar.agent_title',
                                        })}
                                    </span>
                                    <div onClick={addAgent}>
                                        <img
                                            src="/icons/edit_icon_1.svg"
                                            className="w-[16px] h-[16px] shrink-0"
                                        ></img>{' '}
                                    </div>
                                </div>
                                <div className="shrink-0 flex items-center">
                                    <Tooltip
                                        className="pr-[2px]"
                                        overlayStyle={{ fontSize: '12px' }}
                                        title={intl.formatMessage({
                                            id: 'app.chatroom.sidebar.chatroom_switch_tips',
                                        })}
                                    >
                                        <QuestionCircleOutlined className="cursor-pointer text-[#666] text-[12px]" />
                                    </Tooltip>
                                    <span className="text-[12px] text-[#666] pr-[5px]">
                                        {intl.formatHTMLMessage({ id: 'app.chatroom_list.switch' })}
                                    </span>
                                    {/* onChange={()=>{openRoomstatus(i)}} */}
                                    <Switch
                                        size="small"
                                        defaultChecked
                                        className="w-[28px]"
                                        checked={chatRoomdetial.smart_selection == 1}
                                        onChange={openRoomstatus}
                                        disabled={disableInput}
                                    ></Switch>
                                </div>
                                {/* <span className='shrink-0'><DownOutlined size={14} color='#444444'/></span> */}
                                {/* <img src="/icons/plaza_add.svg" className="w-[16px] h-[16px] shrink-0" onClick={addAgent}></img> */}
                                {/* <div className='flex justify-center items-center rounded-[4px] text-[12px] text-[#1B64F3] px-[10px] hover:bg-[#1B64F3] hover:text-[#fff] transition' onClick={addAgent} style={{border:'1px solid #1B64F3',lineHeight:'17px'}}>
                                {intl.formatMessage({id:'app.chatroom.sidebar.add_button'})}
                                </div> */}
                            </div>
                            <div className="py-[20px] pt-[10px]">
                                <div className="h-[220px] overflow-y-auto px-[10px]">
                                    {agentLoading.current ? (
                                        <div className="flex flex-col">
                                            {agentList && agentList.length > 0 ? (
                                                agentList.map(i => (
                                                    <div
                                                        className="flex items-center gap-x-[5px] hover:bg-[#FAFAFA] transition p-[10px] slider_agent_box"
                                                        key={i.agent_id}
                                                    >
                                                        <div className="flex gap-x-[15px] flex-1 min-w-[0]">
                                                            <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] flex items-center justify-center shrink-0">
                                                                <img
                                                                    src={headportrait(
                                                                        'single',
                                                                        i.icon,
                                                                    )}
                                                                    alt=""
                                                                    className="w-[18px]  h-[18px]"
                                                                />
                                                            </div>
                                                            <div className="flex flex-col gap-y-[5px] justify-center flex-1 min-w-[0]">
                                                                <span className="text-[#213044] text-[12px] font-[500] truncate w-full">
                                                                    {i.name}
                                                                </span>
                                                                <span className="text-[#999999] text-[12px] truncate">
                                                                    {i.description}
                                                                </span>
                                                            </div>
                                                        </div>
                                                        <div className="shrink-0 flex gap-x-[15px] items-center">
                                                            <div
                                                                className="edit cursor-pointer w-[20px] h-[20px] flex justify-center items-center opacity-0 transition"
                                                                onClick={() => {
                                                                    jumpAgentDetial(i);
                                                                }}
                                                            >
                                                                <img
                                                                    className="w-[16px] h-[16px]"
                                                                    src="/icons/edit_icon_1.svg"
                                                                />
                                                            </div>
                                                            <Switch
                                                                size="small"
                                                                disabled={disableInput}
                                                                defaultChecked
                                                                className="w-[28px]"
                                                                checked={i.active == 1}
                                                                onChange={() => {
                                                                    openRoomAgentstatus(i);
                                                                }}
                                                            ></Switch>
                                                        </div>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="w-full min-h-[220px] flex items-center justify-center">
                                                    <Empty
                                                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                                                    ></Empty>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="flex justify-center w-full h-full items-center">
                                            <Spin></Spin>
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="px-[20px]">
                                <div
                                    style={
                                        truncatable && !disableInput
                                            ? { border: '1px solid #1B64F3' }
                                            : {
                                                  background: '#d9d9d9',
                                                  color: 'rgba(0,0,0,0.25)',
                                                  cursor: 'not-allowed',
                                              }
                                    }
                                    onClick={throttle(() => {
                                        if (truncatable && !disableInput) clearContext();
                                    })}
                                    className="w-full h-[30px] transition text-[#1B64F3] flex items-center justify-center cursor-pointer rounded-[6px] hover:text-[#fff] hover:bg-[#1B64F3]"
                                >
                                    <span className="text-[12px]">
                                        {intl.formatMessage({
                                            id: 'app.chatroom.sidebar.agent_button',
                                        })}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="flex-1 min-h-[0] flex flex-col">
                        <div className="pt-[30px] px-[30px] text-[#666] text-[14px] shrink-0">
                            {intl.formatMessage({ id: 'app.chatroom.sidebar.othe_title' })}
                        </div>
                        <div className="px-[10px] flex-1 min-h-[0] py-[10px]">
                            <div
                                style={{ height: 'calc(100% - 20px)' }}
                                className="px-[10px]  overflow-y-auto"
                            >
                                {roomLoading.current ? (
                                    <div className="h-full flex flex-col">
                                        {roomRecentList && roomRecentList.length > 0 ? (
                                            roomRecentList.map(item => (
                                                <div
                                                    className="w-full transition hover:bg-[#FAFAFA] p-[10px] cursor-pointer"
                                                    onClick={() => {
                                                        jumpChatRoom(item);
                                                    }}
                                                    key={item.chatroom_id}
                                                >
                                                    <div className="flex pb-[10px]">
                                                        <div className="flex-1 min-w-[0] truncate text-[#333] text-[14px]">
                                                            {item.name}
                                                        </div>
                                                        {item.active == 0 ? (
                                                            <div className="flex items-center gap-x-[6px]">
                                                                <img
                                                                    className="w-[12px] h-[12px]"
                                                                    src="/icons/plaza_m2_c2.svg"
                                                                    alt=""
                                                                />
                                                                <span className="text-[12px] text-[#aaa]">
                                                                    {intl.formatMessage({
                                                                        id: 'app.chatroom.sidebar.othe_status',
                                                                    })}
                                                                </span>
                                                            </div>
                                                        ) : (
                                                            <div className="flex items-center gap-x-[6px]">
                                                                <img
                                                                    className="w-[12px] h-[12px]"
                                                                    src="/icons/plaza_m2_c1.svg"
                                                                    alt=""
                                                                />
                                                                <span className="text-[12px] text-[#aaa]">
                                                                    {intl.formatMessage({
                                                                        id: 'app.chatroom.sidebar.othe_status_succeed',
                                                                    })}
                                                                </span>
                                                            </div>
                                                        )}
                                                    </div>
                                                    <div className="flex gap-x-[10px]">
                                                        {item.agent_list &&
                                                        item.agent_list.length > 0 ? (
                                                            <>
                                                                {getAgentList(item.agent_list).map(
                                                                    (i: any, index: number) => (
                                                                        <div
                                                                            className="flex"
                                                                            key={index}
                                                                        >
                                                                            <div className="w-[30px] h-[30px] bg-[#F4F8F1] rounded-[6px] flex items-center justify-center">
                                                                                <img
                                                                                    src={headportrait(
                                                                                        'single',
                                                                                        i.icon,
                                                                                    )}
                                                                                    alt=""
                                                                                    className="w-[18px]  h-[18px]"
                                                                                />
                                                                            </div>
                                                                        </div>
                                                                    ),
                                                                )}
                                                                {item.agent_list.length >= 6 ? (
                                                                    <EllipsisOutlined />
                                                                ) : (
                                                                    <></>
                                                                )}
                                                            </>
                                                        ) : (
                                                            <></>
                                                        )}
                                                    </div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="w-full h-full">
                                                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE}></Empty>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="flex justify-center w-full h-full items-center">
                                        <Spin></Spin>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
                {agentShow ? (
                    <Agent
                        show={agentShow}
                        popupClose={popupClose}
                        popupSave={popupSave}
                        checkList={agentList}
                        zIndex={99}
                    />
                ) : (
                    <></>
                )}
            </div>
        </>
    );
};

export default memo(Sider);
