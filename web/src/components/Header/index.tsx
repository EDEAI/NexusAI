/*
 * @LastEditors: biz
 */
import { history, Link, useIntl } from '@umijs/max';
import React from 'react';
import { SelectLang } from '../RightContent';
import { AvatarDropdown, AvatarName } from '../RightContent/AvatarDropdown';
import {creationsearchdata} from "@/utils/useUser";

const Header: React.FC = () => {
    const { location } = history;
    let pathname = location?.pathname;
    const intl = useIntl();
    //chat_room Check whether the route is a dynamic one
    if(pathname.indexOf('chat_room')!=-1){
        let pathnameArray:any =  pathname.split('/')
        let isPathnameId = pathnameArray[pathnameArray.length-1] - 1
        if(!isNaN(isPathnameId)){ pathname = '/chat_room'}
    }
   
    const menuList = [
        {
            name: intl.formatMessage({ id: 'component.menu.dashboard', defaultMessage: '' }),
            icon: '/images/home.svg',
            activeIcon: '/images/home_active.svg',
            children: [
                {
                    name: intl.formatMessage({
                        id: 'component.menu.dashboard',
                        defaultMessage: '',
                    }),
                    path: '/plaza',
                },
            ],
        },
        {
            name: intl.formatMessage({ id: 'component.menu.workspace', defaultMessage: '' }),
            icon: '/images/workflow.svg',
            activeIcon: '/images/workflow_active.svg',
            children: [
                {
                    name: intl.formatMessage({
                        id: 'component.menu.workspace',
                        defaultMessage: '',
                    }),
                    path: '/workspace',
                },
            ],
        },
        {
            name: intl.formatMessage({ id: 'component.menu.creation', defaultMessage: '' }),
            icon: '/images/creation.svg',
            activeIcon: '/images/creation_active.svg',
            children: [
                {
                    name: intl.formatMessage({
                        id: 'component.menu.creation',
                        defaultMessage: '',
                    }),
                    path: '/creation',
                },
                {
                    name: intl.formatMessage({
                        id: 'component.menu.agent',
                        defaultMessage: 'Agent',
                    }),
                    path: '/Agents',
                },
                {
                    name: intl.formatMessage({
                        id: 'component.menu.skill',
                        defaultMessage: '',
                    }),
                    path: '/Skill',
                },
                // {
                //     name: intl.formatMessage({
                //         id: 'component.menu.knowledgeBase',
                //         defaultMessage: '',
                //     }),
                //     path: '/createkb',
                // },
                {
                    name: intl.formatMessage({
                        id: 'component.menu.teamAgent',
                        defaultMessage: 'Agent',
                    }),
                    path: '/ReadOnlyAgent',
                },
                {
                    name: intl.formatMessage({
                        id: 'component.menu.teamSkill',
                        defaultMessage: '',
                    }),
                    path: '/ReadOnlySkill',
                },
                {
                    name: intl.formatMessage({
                        id: 'component.menu.workflow',
                        defaultMessage: '',
                    }),
                    path: '/workspace/workflow',
                },
            ],
        },
        {
            name: intl.formatMessage({ id: 'component.menu.meeting', defaultMessage: '' }),
            icon: '/icons/plaza_m2_c2.svg',
            activeIcon: '/icons/plaza_m2_c1.svg',
            children: [
                {
                    name: intl.formatMessage({
                        id: 'component.menu.chatRoomList',
                        defaultMessage: '',
                    }),
                    path: '/meeting',
                },
                {
                    name: intl.formatMessage({
                        id: 'component.menu.chatRoom',
                        defaultMessage: '',
                    }),
                    path: '/chat_room',
                },
            ],
        },
        {
            name: intl.formatMessage({ id: 'component.menu.knowledgeBase', defaultMessage: '' }),
            icon: '/icons/creation/zhishik1.svg',
            activeIcon: '/icons/creation/pitchzhishik.svg',
            children: [
                {
                    name: intl.formatMessage({
                        id: 'component.menu.knowledgeBase',
                        defaultMessage: '',
                    }),
                    path: '/knowledgebase',
                },
                {
                    name: intl.formatMessage({
                        id: 'component.menu.knowledgeBase',
                        defaultMessage: '',
                    }),
                    path: '/createkb',
                },
            ],
        },
    ];
    return (
        <div className="w-full h-full bg-[#F7F7F7] flex items-center justify-between px-[30px]">
            <div className="logo">
                <Link to={menuList[0].children[0].path}>
                    <img src="/images/logo.svg" alt="logo" className="h-6" />
                </Link>
            </div>
            <div className="flex-1 flex justify-center items-center">
                {menuList.map((item, index) => {
                
                    if (item.children.some(x => x.path == pathname)) {
                        
                        return (
                            <div
                                key={index}
                                onClick={() => {
                                    creationsearchdata('SET',6)
                                    history.push(item.children[0].path);
                                }}
                                className="flex items-center justify-center bg-white h-8 px-[15px] py-[6px] rounded-lg shadow-black mr-5 cursor-pointer"
                            >
                                <img src={item.activeIcon} alt={item.name} className="mr-2" />
                                <span className="text-[#1B64F3]">{item.name}</span>
                            </div>
                        );
                    }
                    return (
                        <div
                            key={index}
                            onClick={() => {
                                creationsearchdata('SET',6)
                                history.push(item.children[0].path);

                            }}
                            className="flex items-center justify-center h-8 px-[15px] py-[6px] rounded-lg shadow-black mr-5 cursor-pointer hover:bg-[#EEEFF1]"
                        >
                            <img src={item.icon} alt={item.name} className="mr-2" />
                            <span className="text-[#213044]">{item.name}</span>
                        </div>
                    );
                })}
            </div>
            <div className="user flex h-full">
                <div className=" flex items-center mr-8">
                    <SelectLang></SelectLang>
                </div>
                <div className="">
                    <AvatarDropdown>
                        <div className="cursor-pointer flex items-center h-[55px]">
                            <AvatarName></AvatarName>
                            <img src="/images/arrow.svg" className="w-4 h-4 ml-[10px]" />
                        </div>
                    </AvatarDropdown>
                </div>
            </div>
        </div>
    );
};

export default Header;
