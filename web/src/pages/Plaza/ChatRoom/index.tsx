
import { roomDetails } from '@/api/plaza';
import {Empty} from 'antd';
import 'highlight.js/styles/atom-one-dark.css';
import React, { memo, useEffect, useRef, useState } from 'react';
import { history, useParams } from 'umi';
import Sidebar from '../components/Sider/index';
import {ChatRoomContent} from '@/components/ChatRoomContent'
import MeetingSummary from '../components/MeetingSummary/index';

const EmptyDom :React.FC<{}> = parmas =>{
    return(
        <div className="flex items-center h-full justify-center">
            <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
            ></Empty>
        </div>
    )
}
// Chat room
const Chatroom: React.FC = memo(() => {
    const { id } = useParams<{ id: string }>();
    // agent list
    const agentList = useRef([]);
    // Room details
    const getRoomDetail = useRef(null);
    // Whether the room details request was successful
    const [roomSuccess, setRoomSuccess] = useState(false);
    // Get agent_list details
    const getRoomDetails = async () => {
        if (id) {
            let res = await roomDetails({ id });
            if (res.code == 0) {
                setRoomSuccess(true);
                getRoomDetail.current = res.data;
                agentList.current = res.data.agent_list;
            } else {
                history.replace(`/meeting`);
            }
        }
    };
    useEffect(() => {
        getRoomDetails();
    }, []);
    return (
        <>
            <div className="w-full flex bg-[#fff] overflow-hidden" style={{ height: 'calc(100vh - 56px)' }}>
                <Sidebar
                    roomDetail={getRoomDetail.current}
                    setAgent={agentList}
                ></Sidebar>
                <div className="flex-1">
                    {roomSuccess?
                        <ChatRoomContent agentList={agentList}/>
                    :<EmptyDom/>}
                </div>
                <>
                    <MeetingSummary id={id}/>
                </>
            </div>
        </>
    );
});

export default Chatroom;
