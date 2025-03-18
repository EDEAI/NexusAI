import { delChatroom, getChatroom, upRoomStatus } from '@/api/plaza';
import Scroll from '@/components/InfiniteScroll';
import { headportrait } from '@/utils/useUser';
import { EllipsisOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import type { MenuProps } from 'antd';
import { Col, Dropdown, Empty, message, Modal, Row, Spin, Button } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import { history } from 'umi';
import CreationChatRoom from '../components/CreationChatRoom/index';
// import Menus from '../components/Menus/index';

// Add new application
const AddRoom = (obj: any) => {
    return (
        <Col className="gutter-row" xs={24} sm={24} md={12} lg={8} xl={6}>
            <div
                className="h-[236px] rounded-[8px] bg-[#EFF0F2] flex flex-col items-center justify-center gap-y-[10px] cursor-pointer"
                style={{ border: '1px solid #E9E9E9' }}
                onClick={() => {
                    obj.setCreateShow(true);
                    obj.isUpdataChatRoom.current = false;
                    obj.upDataId.current = 0;
                }}
            >
                <img src="/icons/plaza_m2_c2.svg" className="w-[42px] h-[42px]" alt="" />
                <span className="text-[#213044] text-[12px]">
                    {obj.intl.formatMessage({ id: 'app.chatroom_list.create' })}
                </span>
            </div>
        </Col>
    );
};
// Card operation area
const Operation = ({ item, resetList, setCreateShow, isUpdataChatRoom, upDataId, intl }: any) => {
    const [messageApi, contextHolder] = message.useMessage();
    const { confirm } = Modal;
    const showModal = () => {
        confirm({
            title: intl.formatMessage({ id: 'app.chatroom.del.title' }),
            icon: <ExclamationCircleFilled />,
            content: intl.formatMessage({ id: 'app.chatroom.del.tips' }),
            okText: intl.formatMessage({ id: 'app.chatroom.del.confirm' }),
            okType: 'danger',
            cancelText: intl.formatMessage({ id: 'app.chatroom.del.cancel' }),
            onOk() {
                delRoom();
            },
        });
    };
// Delete room
    const delRoom = async () => {
        let res = await delChatroom({
            id: item.chatroom_id,
        });
        if (res.code == 0) {
            messageApi.open({
                key: 'del',
                type: 'success',
                content: intl.formatMessage({ id: 'app.chatroom.del.delsuccess' }),
                duration: 10,
            });
            resetList(item.chatroom_id);
        }
    };
// Edit room
    const editRoom = async () => {
        setCreateShow(true);
        isUpdataChatRoom.current = true;
        upDataId.current = item.chatroom_id;
    };
// Menu options
    const items: MenuProps['items'] = [
        {
            key: '1',
            label: (
                <div className="py-[3px] px-[3px]">
                    <div
                        className="flex gap-x-[5px] text-[12px] text-[#213044] items-center p-y-[8]"
                        onClick={editRoom}
                    >
                        <img src="/icons/edit_icon.svg" className="w-[16px] h-[16px]" />
                        <span>{intl.formatMessage({ id: 'app.chatroom_list.fun_button_1' })}</span>
                    </div>
                </div>
            ),
        },
        {
            key: '2',
            label: (
                <div className="py-[3px] px-[3px]">
                    <div
                        className="flex gap-x-[5px] text-[12px] text-[#E12222] items-center"
                        onClick={showModal}
                    >
                        <img src="/icons/delete_icon.svg" className="w-[16px] h-[16px]" />
                        <span>{intl.formatMessage({ id: 'app.chatroom_list.fun_button_2' })}</span>
                    </div>
                </div>
            ),
        },
    ];
    // const openRoomstatus = async () => {
    //     await upRoomStatus(
    //         { smart_selection: item.smart_selection == 1 ? 0 : 1 },
    //         item.chatroom_id,
    //     );
    //     resetList(item.chatroom_id, item.smart_selection == 1 ? 0 : 1);
    // };
    return (
        <>
            {contextHolder}
            <div className="flex  items-center">
                <div className="flex gap-x-[6px] items-center flex-1">
                    {/* <span className="text-[12px] text-[#666] line">
                        {intl.formatMessage({ id: 'app.chatroom_list.switch' })}
                    </span>
                    <Switch
                        size="small"
                        value={item.smart_selection == 1}
                        onChange={openRoomstatus}
                    ></Switch> */}
                </div>
                <Dropdown menu={{ items }} placement="topRight" className="cursor-pointer">
                    <div className="w-[18px] h-[18px] bg-[#ebebeb] rounded-[4px] flex justify-center items-center">
                        <EllipsisOutlined
                            className="hover:text-[#1B64F3]"
                            style={{ fontSize: '14px' }}
                        />
                    </div>
                </Dropdown>
            </div>
        </>
    );
};
const MeetingCont = () => {
    const intl = useIntl();

    const [meeting, setMeeting] = useState(null);

    const [closeLoading, setcloseLoading] = useState(false);

    const [parameter, setParameter] = useState({
        page: 1,
        page_size: 20,
        name: '',
    });
    const [ishasMore, setishasMore] = useState(true);

    const isUpdataChatRoom = useRef(false);

    const upDataId = useRef(0);

    const [createShow, setCreateShow] = useState(false);

    const chatRoomList = async (isInit = false) => {
        let res = await getChatroom(parameter);
        if (isInit) {
            setcloseLoading(true);
        }
        if (res.code == 0) {
            setishasMore(res.data.total_pages > parameter.page);
            if (res.data.total_pages >= parameter.page && !isInit) {
                res.data.list = meeting.list.concat(res.data.list);
            }
            if (res.data.list && res.data.list.length) {
                res.data.list.forEach((item: any) => {
                    if (item.agent_list && item.agent_list.length) {
                        item.agent_list.length =
                            item.agent_list.length > 6 ? 6 : item.agent_list.length;
                    }
                });
            }
            setMeeting(res.data);
        }
    };

    useEffect(() => {
        chatRoomList(true);
        setishasMore(true);
    }, []);

    const upSlide = (e: any) => {
        setParameter((pre: any) => {
            return {
                ...pre,
                page: parameter.page++,
            };
        });
        chatRoomList();
    };

    const resetList = (id: number, status: any = undefined) => {
        if (meeting && meeting.list.length) {
            if (status != undefined) {
                setMeeting({
                    ...meeting,
                    list: meeting.list.map((x: any) => {
                        return {
                            ...x,
                            smart_selection: x.chatroom_id === id ? status : x.smart_selection,
                            // active:x.chatroom_id === id && status == 0  ? 0 : x.active
                        };
                    }),
                });
            } else {
                setMeeting({
                    ...meeting,
                    list: meeting.list.filter((x: any) => x.chatroom_id !== id),
                });
            }
        }
    };

    const gotoChat = (item: any) => {
        // history.push(`/chat_room?id=${item.chatroom_id}`)
        history.push(`/chat_room/${item.chatroom_id}`);
    };

    const popupClose = () => {
        setCreateShow(false);
    };

    const popupSave = (updata: any) => {
        if (updata) {
            chatRoomList(true);
        }
    };
    return (
        // onScroll={upSlide}
        <div
            className="pt-0 w-full"
            id="Meeting"
            style={{ height: 'calc(100vh - 94px)', overflowY: 'auto' }}
        >
            <Scroll
                dataLength={meeting && meeting.list.length}
                elid={'Meeting'}
                ishasMore={ishasMore}
                upSlide={upSlide}
                isFooter={true}
                pageNumber={parameter.page}
            >
                <div className="px-[30px] pt-[30px]">
                    <Row gutter={[20, 20]} style={{ margin: 0 }}>
                        {meeting && meeting.list.length && closeLoading ? (
                            <AddRoom
                                setCreateShow={setCreateShow}
                                isUpdataChatRoom={isUpdataChatRoom}
                                intl={intl}
                                upDataId={upDataId}
                            ></AddRoom>
                        ):<></>}
                        {meeting && meeting.list.length ? (
                            meeting.list.map((item: any, index: number) => (
                                <Col
                                    key={index}
                                    className="gutter-row"
                                    xs={24}
                                    sm={24}
                                    md={12}
                                    lg={8}
                                    xl={6}
                                    xxl={6}
                                >
                                    <div
                                        className="relative h-[236px] rounded-[8px] cursor-pointer shadow-lg shadow-gray-100 hover:shadow-gray-200"
                                        onClick={() => {
                                            gotoChat(item);
                                        }}
                                    >
                                        <div
                                            className="bg-[#fff] rounded-[8px] h-full"
                                            style={{
                                                boxShadow: '0px 2px 4px 0px rgba(0,0,0,0.05)',
                                            }}
                                        >
                                            <div className="flex pt-[20px] pb-[15px] px-[20px] text-[#213044] text-[14px] font-[500] gap-x-[6px]">
                                                <span className="flex-1 min-w-[0px] truncate">
                                                    {item.name}
                                                </span>
                                                <div className="flex gap-x-[5px] items-center">
                                                    <img
                                                        src={`${
                                                            item.active == 0
                                                                ? '/icons/plaza_m2_c2.svg'
                                                                : '/icons/plaza_m2_c1.svg'
                                                        }`}
                                                        className="w-[14px] h-[14px]"
                                                    />
                                                    <span className="text-[12px]">
                                                        {item.active == 0 ? (
                                                            <span className="text-[#aaa]">
                                                                {intl.formatMessage({
                                                                    id: 'app.chatroom_list.status',
                                                                })}
                                                            </span>
                                                        ) : (
                                                            <span className="text-[#1B64F3]">
                                                                {intl.formatMessage({
                                                                    id: 'app.chatroom_list.status_succeed',
                                                                })}
                                                            </span>
                                                        )}
                                                    </span>
                                                </div>
                                            </div>
                                            <div>
                                                <div className="px-[20px]">
                                                    <div style={{ borderBottom: '1px solid #eee' }}>
                                                        {
                                                            <div className="text-[#666666] text-[12px] font-[400] w-full truncate min-h-[14px]">
                                                               { item.description ? item.description : <></>}
                                                           </div>
                                                          
                                                        }
                                                        <div className="py-[20px] h-[115px] overflow-hidden">
                                                            {item.agent_list &&
                                                            item.agent_list.length ? (
                                                                <Row gutter={[20, 18]}>
                                                                    {item.agent_list.map(
                                                                        (item: any, index: any) => (
                                                                            <Col
                                                                                key={index}
                                                                                md={12}
                                                                                lg={12}
                                                                                xl={12}
                                                                                xxl={8}
                                                                            >
                                                                                <div className="flex gap-x-[10px] items-center">
                                                                                    <div className="w-[30px] h-[30px] shrink-0 flex items-center rounded-[6px] justify-center bg-[#F4F8F1]">
                                                                                        {/* <img src="/icons/gandUp.svg" alt="" className='w-[18px]  h-[18px]'/> */}
                                                                                        <img
                                                                                            src={headportrait(
                                                                                                'single',
                                                                                                item.icon,
                                                                                            )}
                                                                                            alt=""
                                                                                            className="w-[18px]  h-[18px]"
                                                                                        />
                                                                                    </div>
                                                                                    <div className="text-[#666] text-[12px] truncate">
                                                                                        {item.name}
                                                                                    </div>
                                                                                </div>
                                                                            </Col>
                                                                        ),
                                                                    )}
                                                                </Row>
                                                            ) : (
                                                                <Empty
                                                                    style={{
                                                                        margin: '0px',
                                                                        fontSize: '12px',
                                                                    }}
                                                                    imageStyle={{
                                                                        width: '60px',
                                                                        margin: '0 auto',
                                                                        marginBottom: '2px',
                                                                    }}
                                                                    description={intl.formatMessage(
                                                                        {
                                                                            id: 'app.dashboard.None',
                                                                        },
                                                                    )}
                                                                    image={
                                                                        Empty.PRESENTED_IMAGE_SIMPLE
                                                                    }
                                                                ></Empty>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                                <div
                                                    className="pt-[15px] pb-[16px] px-[20px]"
                                                    onClick={e => {
                                                        e.stopPropagation();
                                                        return false;
                                                    }}
                                                >
                                                    <Operation
                                                        item={item}
                                                        resetList={resetList}
                                                        setCreateShow={setCreateShow}
                                                        isUpdataChatRoom={isUpdataChatRoom}
                                                        upDataId={upDataId}
                                                        intl={intl}
                                                    ></Operation>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Col>
                            ))
                        ) : (
                            <>
                                {!closeLoading ? (
                                    <div
                                        className="w-full h-full flex items-center justify-center "
                                        style={{ height: 'calc(100vh - 300px)' }}
                                    >
                                        <Spin size="large" />
                                    </div>
                                ):<>
                                    <div className='w-full flex items-center flex-wrap justify-center mt-48'>
                                        <div className="w-full flex items-center justify-center mb-2.5">
                                            <img src="/icons/default.svg" alt="" />
                                        </div>    
                                        <div className="w-full text-center mb-3 text-[#666] text-sm">
                                            {intl.formatMessage({ id: 'creation.margindescribe' })} ~
                                        </div>
                                        <div className="w-full text-center">
                                            {' '}
                                            <Button
                                                color="primary"
                                                onClick={() => {
                                                    setCreateShow(true);
                                                    isUpdataChatRoom.current = false;
                                                    upDataId.current = 0;
                                                }}
                                            >
                                                {intl.formatMessage({ id: 'app.chatroom_list.create' })}
                                            </Button>{' '}
                                        </div>
                                    </div>                                
                                
                                </>}
                            </>
                        )}
                        {createShow ? (
                            <CreationChatRoom
                                show={createShow}
                                id={upDataId.current}
                                close={popupClose}
                                save={popupSave}
                                isUpdata={isUpdataChatRoom.current}
                            ></CreationChatRoom>
                        ) : (
                            <></>
                        )}
                    </Row>
                </div>
            </Scroll>
        </div>
    );
};

const Meeting: React.FC = () => {
    return (
        <>
            <div className="w-full">
                {/* <div className="px-[30px] w-full">
                    <Menus path="/plaza" keys="meeting"></Menus>
                </div> */}
                <MeetingCont></MeetingCont>
            </div>
        </>
    );
};
export default Meeting;
