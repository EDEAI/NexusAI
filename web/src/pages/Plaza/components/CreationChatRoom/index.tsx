import { createRoom, roomDetails, updataRoom } from '@/api/plaza';
import { headportrait } from '@/utils/useUser';
import { CloseOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Col, Form, Input, InputNumber, message, Row } from 'antd';
import { throttle } from 'lodash';
import React, { useEffect, useRef, useState } from 'react';
import { useLocation } from 'umi';
import Agent from './selectApp';
const { TextArea } = Input;
interface CreationChatRoom {
    show?: any;
    id?: any;
    close?: any;
    save?: any;
    isUpdata?: any;
}
const ChatroomDetial: React.FC<CreationChatRoom> = param => {
    const intl = useIntl();
    let { show, id, close, save, isUpdata } = param;
    const [form] = Form.useForm();
    // Is editing
    // const [isedit,setIsedit]:any = useState(false)
    const isedit = useRef(false);
    // Get location
    const location: any = useLocation();
    // Get DOM
    const domContent = useRef(null);
    // tips
    const [messageApi, contextHolder] = message.useMessage();
    // Create or update data
    const [roomdataUse, setRoomdataUse] = useState({
        name: '',
        description: '',
        max_round: 10,
        // enable_api: 0,
        // is_public: 0,
        // active: 0,
        agent: [],
    });
    // Agent selected list
    const [checkAgentList, setcheckAgentList] = useState([]);
    // Determine if creation or update is complete
    const isCreateRooms = useRef(false);
    // Create room & update room
    const createRooms = throttle(async (e: any) => {
        if (isCreateRooms.current) return;
        isCreateRooms.current = true;
        let agentArr = checkAgentList.map(({ agent_id, active = 1 }) => ({ agent_id, active }));
        if (!roomdataUse.name) {
            isCreateRooms.current = false;
            return;
        }
        if (agentArr.length == 0) {
            isCreateRooms.current = false;
            messageApi.open({
                type: 'error',
                content: intl.formatMessage({ id: 'app.create_chatroom.label_4_tips' }),
            });
            return;
        }
        setRoomdataUse({
            ...roomdataUse,
            agent: agentArr,
        });
        messageApi.open({
            key: 'create',
            type: 'loading',
            content: 'Loading...',
        });

        let res = !isedit.current
            ? await createRoom({ ...roomdataUse, agent: agentArr })
            : await updataRoom({ ...roomdataUse, agent: agentArr }, id);
        if (res.code == 0) {
            messageApi.open({
                key: 'create',
                type: 'success',
                content: !isedit.current
                    ? intl.formatMessage({ id: 'app.create_chatroom.succeed' })
                    : intl.formatMessage({ id: 'app.edit_chatroom.succeed' }),
                duration: 2,
            });
            save(true);
            currentCancel();
        }
        isCreateRooms.current = false;
    }, 300);
    // Show or hide popup
    const [agentShow, setAgentShow] = useState(false);
    // Parse URL parameters
    const parseSearch = (search: string) => {
        let result: any = {};
        search
            .slice(1)
            .split('&')
            .forEach(pair => {
                const tmp = pair.split('=');
                result[tmp[0]] = tmp[1];
            });
        return result;
    };
    // Get room details
    const getChatRoom = async (id: string) => {
        let res = await roomDetails({ id });
        if (res.code == 0) {
            let info = res.data.chat_info;
            setRoomdataUse({
                ...roomdataUse,
                name: info.name,
                description: info.description,
                max_round: res.data.max_round ? res.data.max_round : 10,
                agent: res.data.agent_list,
            });
            setcheckAgentList(res.data.agent_list);
        }
    };
    const addAgent = () => {
        setAgentShow(true);
    };
    // agent popup Close
    const popupClose = () => {
        setAgentShow(false);
    };
    // agent popup Save
    const popupSave = (obj: any) => {
        setcheckAgentList([...obj.checkItem]);
    };
    // show agent popup
    const showPopup = () => {
        // domContent.current.style='display:flex;opacity:1'
        isedit.current = false;
        if (isUpdata) {
            if (id != 0) {
                isedit.current = true;
                getChatRoom(id);
            }
        }
    };

    // Close chat popup
    const currentCancel = () => {
        // domContent.current.style='opacity:0;display:none'
        form.setFieldsValue({
            Title: '',
            Description: '',
            MaxRound: 10,
        });
        setRoomdataUse({
            ...roomdataUse,
            name: '',
            description: '',
            max_round: 10,
            agent: [],
        });
        setcheckAgentList([]);
        isCreateRooms.current = false;
        close();
    };
    useEffect(() => {
        if (show) {
            showPopup();
        }
    }, [show]);
    useEffect(() => {
        form.setFieldsValue({
            Title: roomdataUse.name,
            Description: roomdataUse.description,
            MaxRound: roomdataUse.max_round,
        });
    }, [roomdataUse, form]);
    return (
        <>
            <div
                ref={domContent}
                className="w-full h-full fixed top-[0] left-[0] bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-20"
            >
                <div className="w-[980px] h-[646px] bg-[#fff] rounded-[6px]">
                    {contextHolder}
                    <div className="w-full flex relative" style={{ height: '100%' }}>
                        <div
                            className="w-full relative box-border flex-1"
                            style={{ height: '100%' }}
                        >
                            <Form
                                form={form}
                                className="h-full"
                                initialValues={{
                                    Title: roomdataUse.name,
                                    Description: roomdataUse.description,
                                    MaxRound: roomdataUse.max_round,
                                }}
                            >
                                <div className="flex flex-col h-full">
                                    <div
                                        className="text-[16px] flex items-center p-[20px]"
                                        style={{ borderBottom: '1px solid #ebebeb' }}
                                    >
                                        <span className="flex-1 text-[14px] font-[500] text-[#213044]">
                                            {isedit.current
                                                ? intl.formatMessage({
                                                      id: 'app.edit_chatroom.title',
                                                  })
                                                : intl.formatMessage({
                                                      id: 'app.create_chatroom.title',
                                                  })}
                                        </span>
                                        <CloseOutlined
                                            className="text-[16px] cursor-pointer"
                                            onClick={currentCancel}
                                        />
                                    </div>
                                    <div className="flex-1 min-h-[0] overflow-auto">
                                        <div className="pt-[20px] px-[20px]">
                                            <div className="text-[12px] text-[#213044]">
                                                <span style={{ color: 'red', paddingRight: '4px' }}>
                                                    *
                                                </span>
                                                {intl.formatMessage({
                                                    id: 'app.create_chatroom.label_1',
                                                })}
                                            </div>
                                            <div className="pt-[15px]">
                                                <Form.Item
                                                    name="Title"
                                                    rules={[
                                                        {
                                                            required: true,
                                                            message: intl.formatMessage({
                                                                id: 'app.create_chatroom.label_1_tips',
                                                            }),
                                                        },
                                                    ]}
                                                    style={{ marginBottom: '0px' }}
                                                >
                                                    <Input
                                                        placeholder={intl.formatMessage({
                                                            id: 'app.create_chatroom.label_1_pl',
                                                        })}
                                                        maxLength={50}
                                                        style={{
                                                            height: 40,
                                                            background: '#F7F7F7',
                                                        }}
                                                        className="placeholder:text-[#bbb] placeholder:text-[12px] h-[40px] border-[#eee] text-[#213044]"
                                                        onChange={e => {
                                                            setRoomdataUse({
                                                                ...roomdataUse,
                                                                name: e.target.value,
                                                            });
                                                        }}
                                                    />
                                                </Form.Item>
                                            </div>
                                            {/* <span style={{color:'red',paddingRight:'4px'}}>*</span> */}
                                            <div className="text-[12px] text-[#213044] pt-[20px]">
                                                {intl.formatMessage({
                                                    id: 'app.create_chatroom.label_2',
                                                })}
                                            </div>
                                            <div className="pt-[10px]">
                                                <Form.Item
                                                    name="Description"
                                                    style={{ marginBottom: '0px' }}
                                                >
                                                    <TextArea
                                                        showCount
                                                        maxLength={1000}
                                                        placeholder={intl.formatMessage({
                                                            id: 'app.create_chatroom.label_2_pl',
                                                        })}
                                                        value={roomdataUse.description}
                                                        style={{
                                                            height: 57,
                                                            resize: 'none',
                                                            background: '#F7F7F7',
                                                        }}
                                                        className="placeholder:text-[#bbb] placeholder:text-[12px] h-[40px] border-[#eee] text-[#213044]"
                                                        onChange={e => {
                                                            setRoomdataUse({
                                                                ...roomdataUse,
                                                                description: e.target.value,
                                                            });
                                                        }}
                                                    />
                                                </Form.Item>
                                            </div>
                                            <div className="text-[12px] text-[#213044] pt-[20px]">
                                                <span style={{ color: 'red', paddingRight: '4px' }}>
                                                    *
                                                </span>
                                                {intl.formatMessage({
                                                    id: 'app.create_chatroom.label_3',
                                                })}
                                            </div>
                                            <div className="pt-[10px]">
                                                <Form.Item
                                                    name="MaxRound"
                                                    rules={[
                                                        {
                                                            required: true,
                                                            message: intl.formatMessage({
                                                                id: 'app.create_chatroom.label_3_tips',
                                                            }),
                                                        },
                                                    ]}
                                                    style={{ marginBottom: '0px' }}
                                                >
                                                    <InputNumber
                                                        min={10}
                                                        step={1}
                                                        max={100}
                                                        size="large"
                                                        style={{ background: '#F7F7F7' }}
                                                        className="placeholder:text-[#bbb] placeholder:text-[12px]  border-[#eee] text-[#213044] w-full"
                                                        onChange={e => {
                                                            setRoomdataUse({
                                                                ...roomdataUse,
                                                                max_round: e,
                                                            });
                                                        }}
                                                        formatter={value =>
                                                            value !== undefined
                                                                ? Math.floor(value).toString()
                                                                : roomdataUse.max_round.toString()
                                                        }
                                                    />
                                                </Form.Item>
                                            </div>
                                            <div className="text-[14px]  pt-[20px] flex">
                                                <span style={{ color: 'red', paddingRight: '4px' }}>
                                                    *
                                                </span>
                                                <span className="text-[12px] text-[#213044]">
                                                    {intl.formatMessage({
                                                        id: 'app.create_chatroom.label_4',
                                                    })}
                                                </span>
                                            </div>
                                            <div className="pt-[15px] pb-[20px] overflow-hidden w-full">
                                                <Row gutter={[15, 15]}>
                                                    <Col span={6}>
                                                        <div
                                                            className="text-[12px] text-[#BBBBBB] h-[62px] rounded-[4px] bg-[#F7F7F7] leading-[62px] text-center cursor-pointer"
                                                            onClick={addAgent}
                                                            style={{ border: '1px solid #EEEEEE' }}
                                                        >
                                                            {intl.formatMessage({
                                                                id: 'app.create_chatroom.add_button',
                                                            })}
                                                        </div>
                                                    </Col>
                                                    {checkAgentList && checkAgentList.length ? (
                                                        checkAgentList.map((item: any) => (
                                                            <Col span={6} key={item.agent_id}>
                                                                <div
                                                                    className={`bg-[#fff] flex gap-x-[20px] p-[10px] cursor-pointer border-solid border-[1px] rounded-[4px] border-[#eee]`}
                                                                >
                                                                    <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] relative flex items-center justify-center shrink-0">
                                                                        <img
                                                                            src={headportrait(
                                                                                'single',
                                                                                item.icon,
                                                                            )}
                                                                            alt=""
                                                                            className="w-[20px]  h-[20px]"
                                                                        />
                                                                        {/* <div className='w-[16px]  h-[16px] bg-[#fff] absolute bottom-[-2px] right-[-2px]'>
                                                                                <img src="/icons/robot_icon.svg" alt="" className='w-[12px]  h-[12px]'/>
                                                                            </div> */}
                                                                    </div>
                                                                    <div className="flex flex-col gap-y-[5px] justify-center flex-1 min-w-[0]">
                                                                        <div className="text-[#213044] text-[12px] font-[500] w-full truncate">
                                                                            {item.name}
                                                                        </div>
                                                                        <div className="text-[#999] text-[12px] w-full truncate">
                                                                            {item.description}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </Col>
                                                        ))
                                                    ) : (
                                                        <></>
                                                    )}
                                                </Row>
                                            </div>
                                        </div>
                                    </div>
                                    <div
                                        className="p-[20px] flex gap-x-[20px] justify-end"
                                        style={{ borderTop: '1px solid #e8e8e8' }}
                                    >
                                        <Button
                                            className="text-[14px] text-[#213044] w-[88px] h-[40px]"
                                            style={{ border: '1px solid #D8D8D8' }}
                                            onClick={currentCancel}
                                        >
                                            {intl.formatMessage({
                                                id: 'app.create_chatroom.cancel',
                                            })}
                                        </Button>
                                        <Button
                                            type="primary"
                                            className="bg-[#1B64F3] rounded-[4px] w-[88px] h-[40px]"
                                            htmlType="submit"
                                            onClick={createRooms}
                                        >
                                            {intl.formatMessage({ id: 'app.create_chatroom.save' })}
                                        </Button>
                                    </div>
                                </div>
                                {/* <Button type="primary" className='' htmlType="submit" onClick={createRooms}>
                                    { !isedit ?'Create Romm':'Updata Romm'}
                                </Button> */}
                            </Form>
                        </div>
                    </div>
                </div>
                <Agent
                    show={agentShow}
                    popupClose={popupClose}
                    popupSave={popupSave}
                    checkList={checkAgentList}
                />
            </div>
        </>
    );
};

export default ChatroomDetial;
