/*
 * @LastEditors: wnagchi 1305bcd@gmail.com
 */

import { getAgentList, getSkillList } from '@/api/workflow';
import { QuestionCircleOutlined, SearchOutlined } from '@ant-design/icons';
import { ProForm, ProFormRadio, ProFormText } from '@ant-design/pro-components';
import { useFloating, useHover, useInteractions } from '@floating-ui/react';
import { getLocale, useIntl } from '@umijs/max';
import { useSetState } from 'ahooks';
import { Tabs, TabsProps, Tooltip } from 'antd';
import { memo, useEffect, useState } from 'react';
import DraggablePanel from '../Panel/DraggablePanel';
import UserCon from './components/UserCon';
import { getBaseNode } from './nodes/nodeDisperse';
import useStore from './store';
import { BlockEnum } from './types';

export default memo(() => {
    const intl = useIntl();
    const lang = getLocale() == 'en-US' ? 'en_US' : 'zh_Hans';
    const originNodes = getBaseNode();
    const baseNodes = Object.values(originNodes)
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
    const agentData = useStore(state => state.agentData);
    const skillData = useStore(state => state.skillData);
    const toolData = useStore(state => state.toolData);

    const [searchNode, setSearchNode] = useState(baseNodes);
    const [searchTools, setSearchTools] = useState(toolData?.list || []);
    const [searchAgent, setSearchAgent] = useState([]);
    const [searchSkill, setSearchSkill] = useState([]);
    // const [searchSkill, setSearchSkill] = useState(searchSkill);
    interface SearchNodeList {
        [BlockEnum.Agent]?: any;
        [BlockEnum.Skill]?: any;
    }
    const [searchNodeList, setSearchNodeList] = useSetState<SearchNodeList>({
        [BlockEnum.Agent]: [],
        [BlockEnum.Skill]: [],
    });
    const [filterData, setFilterData] = useState({
        team: 1,
        keyword: '',
    });
    const onDragStart = (event, nodeType, item) => {
        event.dataTransfer.setData(
            'application/reactflow',
            JSON.stringify({ type: nodeType, item }),
        );
        event.dataTransfer.effectAllowed = 'move';
    };

    useEffect(() => {
        console.log(agentData);
        setSearchTools(toolData?.list || []);
    }, [toolData]);

    const ToolToBaseData = () => {};

    const getAppsData = async (nodeType: BlockEnum.Agent | BlockEnum.Skill) => {
        let res = {};
        const teamStatus = filterData.team == 1 ? 3 : 2;
        let originNode = null;

        let list = [];
        if (nodeType == BlockEnum.Agent) {
            res = await getAgentList(teamStatus);
            originNode = originNodes[BlockEnum.Agent]?.base;
        } else {
            res = await getSkillList(teamStatus);
            originNode = originNodes[BlockEnum.Skill]?.base;
        }

        if (res?.code == 0 && res?.data?.list?.length) {
            list = res.data.list.map(item => {
                return {
                    ...originNode,
                    data: {
                        ...originNode.data,
                        title: item.name,
                        desc: item.description,
                    },
                    baseData: item,
                };
            });
        }
        setSearchNodeList({ [nodeType]: list });
    };

    useEffect(() => {
        getAppsData(BlockEnum.Agent);
        getAppsData(BlockEnum.Skill);
        // trandformAgentData(filterData);
        // trandformSkillData(filterData);
    }, [filterData]);
    const onFilterChange = (e, all) => {
        if (e['team'] != undefined) {
            setFilterData(all);
        }
    };

    const RenderNodes = ({ list }) =>
        list.map((item, index) => (
            <div
                onDragStart={event => onDragStart(event, item.type, item)}
                draggable
                className="cursor-pointer hover:bg-blue-100 rounded-md px-2 box-border"
            >
                <UserCon
                    key={index}
                    title={item.data.title}
                    icon={item?.baseData?.icon || item.type}
                ></UserCon>
            </div>
        ));
    const RenderToolsNodeList = ({ list }) =>
        list.map((item, index) => {
            // const [isOpen, setIsOpen] = useState(false);

            // const { refs, floatingStyles, context } = useFloating({
            //     open: isOpen,
            //     onOpenChange: setIsOpen,
            // });

            // const hover = useHover(context);

            // const { getReferenceProps, getFloatingProps } = useInteractions([hover]);
            return (
                <div key={index}>
                    {/* {isOpen && (
                        <div
                            className="floating shadow-md"
                            ref={refs.setFloating}
                            style={floatingStyles}
                            {...getFloatingProps()}
                        >
                            {item?.identity?.description[lang]}
                        </div>
                    )} */}
                    <div
                        className="text-[#333333] mb-2"
                    >
                        {item?.identity?.label[lang]}
                        <Tooltip placement="right" title={item?.identity?.description[lang]}>
                            <QuestionCircleOutlined className="cursor-pointer ml-1" />
                        </Tooltip>
                    </div>
                    {item.tools.map((tool, toolIndex) => (
                        <Tooltip placement="right" title={tool?.description?.human?.[lang]}>
                            <div
                                onDragStart={event => onDragStart(event, item.type, item)}
                                draggable
                                className="cursor-pointer hover:bg-blue-100 rounded-md px-2 box-border"
                            >
                                <UserCon
                                    key={toolIndex}
                                    title={tool?.identity?.label[lang]}
                                    icon={item?.identity?.icon}
                                ></UserCon>
                            </div>
                        </Tooltip>
                    ))}
                </div>
            );
        });
    const RenderNodeList = () => {
        return (
            <div>
                <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-y-2 gap-2 pt-5">
                    {/* <RenderNodeList list={searchNode} /> */}
                    {showTypes.includes('1') && <RenderNodes list={searchNode} />}
                    {showTypes.includes('2') && (
                        <RenderNodes list={searchNodeList[BlockEnum.Agent]} />
                    )}
                    {showTypes.includes('3') && <RenderToolsNodeList list={searchTools} />}
                    {showTypes.includes('4') && (
                        <RenderNodes list={searchNodeList[BlockEnum.Skill]} />
                    )}
                </div>
            </div>
        );
    };
    return (
        <DraggablePanel
            dragDirection="right"
            minWidth={270}
            className="fixed left-0 top-16 bg-white"
        >
            <div style={{ height: 'calc(100vh - 110px)' }} className="flex flex-col">
                <div>
                    <ProForm
                        submitter={{
                            render: () => null,
                        }}
                        initialValues={{
                            team: 1,
                        }}
                        onValuesChange={onFilterChange}
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
                            name="keyword"
                        ></ProFormText>
                    </ProForm>

                    <Tabs
                        defaultActiveKey={tabIndex}
                        onChange={e => {
                            setShowTypes([e as TabKey]);
                        }}
                        items={tabItems}
                    ></Tabs>
                </div>
                <div className="overflow-y-auto flex-1">
                    <RenderNodeList></RenderNodeList>
                </div>
            </div>
        </DraggablePanel>
    );
});
