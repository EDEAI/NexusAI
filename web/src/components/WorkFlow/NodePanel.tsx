/*
 * @LastEditors: biz
 */

import { SearchOutlined } from '@ant-design/icons';
import { ProForm, ProFormRadio, ProFormText } from '@ant-design/pro-components';
import { getLocale, useIntl } from '@umijs/max';
import { Tabs, TabsProps } from 'antd';
import { memo, useEffect, useState } from 'react';
import DraggablePanel from '../Panel/DraggablePanel';
import UserCon from './components/UserCon';
import { getBaseNode } from './nodes/nodeDisperse';
import useStore from './store';
import { BlockEnum } from './types';

export default memo(() => {
    const intl = useIntl();
    const lang = getLocale() == 'en-US' ? 'en_US' : 'zh_Hans';
    const baseNodes = Object.values(getBaseNode())
        .filter(
            item =>
                ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(
                    item.base.type,
                ),
        )
        .map(item => item.base);
    const [tabIndex, setTabIndex] = useState('1');
    const tabItems: TabsProps['items'] = [
        {
            key: '1',
            label: intl.formatMessage({ id: 'workflow.node', defaultMessage: '' }),
        },
        {
            key: '2',
            label: intl.formatMessage({ id: 'workflow.agent', defaultMessage: 'Agent' }),
        },
        {
            key: '3',
            label: intl.formatMessage({ id: 'workflow.tool', defaultMessage: '' }),
            children: <div>{}</div>,
        },
        {
            key: '4',
            label: intl.formatMessage({ id: 'workflow.skill', defaultMessage: '' }),
        },
    ];
    type TabKey = (typeof tabItems)[number]['key'];
    const [showTypes, setShowTypes] = useState<TabKey[]>(['1']);
    const [searchNode, setSearchNode] = useState(baseNodes);
    const toolData = useStore(state => state.toolData);
    const [searchTools, setSearchTools] = useState(toolData?.list || []);
    const agentData = useStore(state => state.agentData);
    const onDragStart = (event, nodeType, item) => {
        event.dataTransfer.setData(
            'application/reactflow',
            JSON.stringify({ type: nodeType, item }),
        );
        event.dataTransfer.effectAllowed = 'move';
    };

    useEffect(() => {
        console.log(toolData);
        setSearchTools(toolData?.list || []);
    }, [toolData]);

    const ToolToBaseData = () => {};
    const trandformData = e => {
        let setData = null;
        if (e == '1') {
            setData = baseNodes;
        } else if (e == '2') {
            setData = [];
        } else if (e == '3') {
            setData = toolData?.list || [];
        } else if (e == '4') {
            setData = [];
        }
        return setData;
    };
    const RenderNodeList = () => {
        console.log(searchNode);

        const RenderNodeList = ({ list }) =>
            list.map((item, index) => (
                <div
                    onDragStart={event => onDragStart(event, item.type, item)}
                    draggable
                    className="cursor-pointer"
                >
                    <UserCon key={index} title={item.data.title} icon={item.type}></UserCon>
                </div>
            ));
        const RenderToolsNodeList = ({ list }) =>
            list.map((item, index) => (
                <div key={index}>
                    <div className='text-[#333333]' > {item?.identity?.label[lang]}</div>
                    {item.tools.map((tool, toolIndex) => (
                        <div
                            onDragStart={event => onDragStart(event, item.type, item)}
                            draggable
                            className="cursor-pointer"
                        >
                            <UserCon
                                key={toolIndex}
                                title={tool?.identity?.label[lang]}
                                icon={item?.identity?.icon}
                            ></UserCon>
                        </div>
                    ))}
                </div>
            ));
        return (
            <div>
                <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-y-2 gap-2 pt-5">
                    {/* <RenderNodeList list={searchNode} /> */}
                    {
                        showTypes.includes('1')&&<RenderNodeList list={searchNode} />
                    }
                    {
                        showTypes.includes('2')&&<RenderNodeList list={searchNode} />
                    }
                    {
                        showTypes.includes('3')&&<RenderToolsNodeList list={searchTools} />
                    }
                    {
                        showTypes.includes('4')&&<RenderNodeList list={searchNode} />
                    }
                </div>
            </div>
        );
    };
    return (
        <DraggablePanel
            dragDirection="right"
            minWidth={270}
            className="fixed left-0 top-14 bg-white"
        >
            <div style={{ height: 'calc(100vh - 66px)' }}>
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    initialValues={{
                        team: 1,
                    }}
                >
                    <div className="flex gap-2 items-center text-base mb-4">
                        节点列表
                        <ProFormRadio.Group
                            name={`team`}
                            fieldProps={{
                                options: [
                                    {
                                        label: '团队',
                                        value: 0,
                                    },
                                    {
                                        label: '我的',
                                        value: 1,
                                    },
                                ],
                                size: 'small',
                                optionType: 'button',
                                buttonStyle: 'solid',
                            }}
                            formItemProps={{
                                className: 'mb-0',
                            }}
                        ></ProFormRadio.Group>
                    </div>

                    <ProFormText
                        fieldProps={{
                            prefix: <SearchOutlined />,
                        }}
                    ></ProFormText>
                </ProForm>

                <Tabs
                    defaultActiveKey={tabIndex}
                    onChange={e => {
            
                        setShowTypes([e as TabKey])
                    }}
                    items={tabItems}
                ></Tabs>
                <RenderNodeList></RenderNodeList>
                <div className="pt-4">
                    <div className="flex justify-between">
                        <div>我的Agent</div>
                        {/* <div className="cursor-pointer">更多</div> */}
                    </div>
                    <div className="grid grid-cols-2 gap-y-4 gap-2 pt-5">
                        {/* {JSON.stringify(agentData?.user?.list)} */}
                        {agentData?.user?.list.map(item => (
                            <div
                                key={item.app_id}
                                className="flex items-center gap-2"
                                onDragStart={event => onDragStart(event, BlockEnum.Agent, item)}
                                draggable
                            >
                                <div
                                    style={{
                                        background: item.icon_background || '',
                                    }}
                                    className="p-2 rounded-md bg-slate-400 shrink-0"
                                >
                                    <img src="/icons/agent.svg" className="size-5" alt="" />
                                </div>
                                <div className="truncate"> {item.name}</div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="pt-4">
                    <div className="flex justify-between">
                        <div>团队Agent</div>
                        {/* <div className="cursor-pointer">更多</div> */}
                    </div>
                    <div className="grid grid-cols-2 gap-y-4 gap-2 pt-5">
                        {/* {JSON.stringify(agentData?.user?.list)} */}
                        {agentData?.team?.list.map(item => (
                            <div
                                key={item.agent_id}
                                className="flex items-center gap-2"
                                onDragStart={event => onDragStart(event, BlockEnum.Agent, item)}
                                draggable
                            >
                                <div
                                    style={{
                                        background: item.icon_background || '',
                                    }}
                                    className="p-2 rounded-md bg-slate-400 shrink-0"
                                >
                                    <img src="/icons/agent.svg" className="size-5" alt="" />
                                </div>
                                <div className="truncate"> {item.name}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </DraggablePanel>
    );
});
