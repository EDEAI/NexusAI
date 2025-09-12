import { GetagentInfo } from '@/api/agents';
import { agentdefault, creationsearchdata } from '@/utils/useUser';

import { login } from '@/api';
import useUserInfo from '@/hooks/useUserInfo';
import { API } from '@/types/api';
import { useIntl } from '@umijs/max';
import { message, Spin } from 'antd';
import React, { useEffect, useState } from 'react';
import { setLocale } from 'umi';
import Chat from './Chat';
import { createRoom } from '@/api/plaza';
const USERNAME = IFRAME_TEST_USERNAME;
const PASSWORD = IFRAME_TEST_PASSWORD;

const Agents: React.FC = () => {
    const intl = useIntl();
    const [Detaillist, setDetaillist] = useState(null);

    const [Fourthly_abilities_list, setFourthly_abilities_list] = useState(null);
    const [Operationbentate, setOperationbentate] = useState(null);
    const [loading, setLoading] = useState(true);
    const [iframeHeight, setIframeHeight] = useState(`${window.innerHeight}px`);

    useEffect(() => {
        init();
    }, []);

    useEffect(() => {
        const handleResize = () => {
            setIframeHeight(`${window.innerHeight}px`);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const init = async () => {
        await handleSubmit({
            password: PASSWORD,
            username: USERNAME,
        });
        
        const agent=await getAgent();
        await createChatRoom(agent.agent.agent_id);
        document.body.style.overflow = 'hidden';
    };

    const setChatroomId=async (agent_id:any,chatroom_id:any)=>{
        const chatroomIds=localStorage.getItem('agent_chat_quickly_chatroom_ids');
        let localObj={
            [agent_id]:chatroom_id
        }
        if(chatroomIds){
            const chatroom_id_obj=JSON.parse(chatroomIds);
            localObj={
                ...chatroom_id_obj,
                [agent_id]:chatroom_id,
                
            }
        }
        localStorage.setItem('agent_chat_quickly_chatroom_ids',JSON.stringify(localObj));
    }

    const checkHasChatroomId= (agent_id:any)=>{
        const chatroomIds=localStorage.getItem('agent_chat_quickly_chatroom_ids');
        if(chatroomIds){
            const chatroom_id_obj=JSON.parse(chatroomIds);
            return chatroom_id_obj[agent_id];
        }
    }

    const createChatRoom=async (agent_id:any)=>{
        const hasChatroomId= checkHasChatroomId(agent_id);
        if(hasChatroomId){
            setDetaillist(prev=>{
                return {
                    ...prev,
                    agent_chatroom_id:hasChatroomId
                }
            })
            setTimeout(()=>{
                setLoading(false);
            },400)
            return;
        }
        const res= await createRoom({
            description:'hhhhhhhhhhhhhhhhhhhhh',
            name:`这是由agent[${agent_id}]创建的临时聊天室`,
            max_round:10,
            agent:[
                {
                    agent_id,
                    active:1
                }
            ]
        })
        if(res.code==0){
            setChatroomId(agent_id,res.data.chatroom_id);
            setDetaillist(prev=>{
                return {
                    ...prev,
                    agent_chatroom_id:res.data.chatroom_id
                }
            })
        }
        setTimeout(()=>{
            setLoading(false);
        },400)
    }
    const handleSubmit = async (values: API.LoginParams) => {
        try {
            //
            const { password, username } = values;
            const msg = await login({
                password,
                username,
            });

            if (msg?.access_token) {
                await fetchUserInfo();
                return true;
            }
        } catch (error) {
            console.log(error);
            return false;
        }
    };
    const { refreshUserInfo, userInfo } = useUserInfo();
    const fetchUserInfo = async () => {
        await refreshUserInfo();
        creationsearchdata('SET', 6, false, '');
        setTimeout(() => {
            setLocale(userInfo?.language == 'en' ? 'en-US' : 'zh-CN');
        }, 100);
    };
    const getAgent = async (app_id?: any) => {
        let params = new URLSearchParams(window.location.search);

        let res = null;
        if (!!params.get('app_id') || !!app_id) {
            res = await GetagentInfo(app_id ? app_id : params.get('app_id'), params.get('type'));
        } else {
            res = await agentdefault();
        }
        const data = res.data;
        if (res.data.callable_items) {
            res.data.agent.selected_skills = [];
            res.data.agent.selected_workflows = [];
            res.data.callable_items.forEach((item: any) => {
                if (item.item_type == 1) {
                    res.data.agent.selected_skills.push({
                        ...item,
                        mode: 4,
                    });
                } else {
                    res.data.agent.selected_workflows.push({
                        ...item,
                        mode: 2,
                    });
                }
            });
        }
        setDetaillist(res.data);
        setOperationbentate(
            res.data.agent.publish_status === 0 && res.data.is_creator === 1 ? 'false' : 'true',
        );
        if (res.data.agent.publish_status === 1) {
            message.warning(intl.formatMessage({ id: 'agent.message.listwarning' }), 5);
        }

        const newabilitieslist = data.agent_abilities_list.filter((item: any, i: any) => {
            return item.status === 1;
        });

        // setFourthly_abilities_list(
        //     selectlistdata(newabilitieslist).concat([
        //         { value: 0, label: intl.formatMessage({ id: 'agent.allability' }) },
        //     ]),
        // );
        
        return data;
    };

    const selectlistdata = (list: any) => {
        return list.map((item: any) => {
            return { value: item.agent_ability_id, label: item.name };
        });
    };

    const firstjudgingcondition = () => {
        return false;
    };

    const secondjudgingcondition = () => {
        return false;
    };

    const agentupdata = () => {};

    return (
        <div className=" flex bg-white absolute w-full h-full top-0 left-0" style={{ height: iframeHeight }}>
            {loading ? (
                <div className="w-full h-full flex items-center justify-center">
                    <Spin size="large" />
                </div>
            ) : (
            <Chat
                saveInfo={{
                    firstjudgingcondition,
                    secondjudgingcondition,
                    agentupdata,
                }}
                operationbentate={Operationbentate}
                iframe={{
                        height: iframeHeight,
                }}
                data={{
                    abilitiesList: Fourthly_abilities_list,
                    detailList: Detaillist,
                }}
            />
            )}
        </div>
    );
};
export default Agents;
