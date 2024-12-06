/*
 * @LastEditors: biz
 */
import { SearchOutlined } from '@ant-design/icons';
import autoAnimate from '@formkit/auto-animate';
import { Node, NodeProps, NodeToolbar, Position, useNodeId, useReactFlow } from '@xyflow/react';
import { useHover, useMount } from 'ahooks';
import type { TabsProps } from 'antd';
import { Input, Tabs, Tooltip, Typography } from 'antd';
import { memo, useEffect, useRef, useState } from 'react';
import { getLocale, useIntl } from 'umi';
import UserCon from '../components/UserCon';
import useOutsideClick from '../hooks/useOutsideClick';
import useStore from '../store';
import { BlockEnum } from '../types';
import { getBaseNode } from './nodeDisperse';
interface CreateNodesToolbarProps {
    position: 'right' | 'left';
    className?: string;
    style?: object;
    sourceHandle?: string;
    targetHandle?: string;
    show: boolean;
    onSelect?: (e) => void;
}

export function getNodePosition(currentNode: Node, position: 'right' | 'left' = 'right') {
    let x = currentNode.position.x + currentNode.measured.width + 30;
    const y = currentNode.position.y;
    if (position == 'left') {
        x = currentNode.position.x - currentNode.measured.width - 30;
    }
    return { x, y };
}
export default memo((props: NodeProps & CreateNodesToolbarProps) => {
    const intl = useIntl();
    const baseNodes = Object.values(getBaseNode()).filter(
        item =>
            ![BlockEnum.Start, BlockEnum.Agent, BlockEnum.Tool, BlockEnum.Skill].includes(
                item.icon,
            ),
    );
    const lang = getLocale() == 'en-US' ? 'en_US' : 'zh_Hans';
    const [searchNode, setSearchNode] = useState(baseNodes);
    const [toolsShow, setToolsShow] = useState(false);
    const [showAddNodeBtn, setShowAddNodeBtn] = useState(false);
    const [tabIndex, setTabIndex] = useState('1');
    const tools = useRef(null);
    const nodeId = useNodeId();

    const agentData = useStore(state => state.agentData);
    const agentList = [...(agentData?.team?.list || []), ...(agentData?.user?.list || [])];

    const skillData = useStore(state => state.skillData);
    const skillList = [...(skillData?.user?.list || []), ...(skillData?.team?.list || [])];
    const toolData = useStore(state => state.toolData);
    const storeCreateNode = useStore(state => state.createNode);
    const setPreventScrolling = useStore(state => state.setPreventScrolling);

    const { getNode, addEdges, getEdges } = useReactFlow();
    const ref = useRef(null);
    const isHovering = useHover(tools, {
        onChange: isHover => {
            setPreventScrolling(!isHover);
        },
    });
    useMount(() => {
        setSearchNode(trandformData('1'));
    });
    useEffect(() => {
        tools.current && autoAnimate(tools.current);
        props?.show && setToolsShow(true);
    }, [tools, props?.show]);

    // useEffect(() => {
    //     setShowAddNodeBtn(props.data.selected);
    //     if (!props.data.selected) {
    //         setToolsShow(false);
    //     }
    // }, [props, tools]);
    useOutsideClick(tools, () => {
        setToolsShow(false);
    });

    const trandformData = e => {
        let setData = null;
        if (e == '1') {
            setData = baseNodes;
        } else if (e == '2') {
            setData =
                agentList.map(item => {
                    return {
                        ...item,
                        title: item.name,
                        icon: BlockEnum.Agent,
                    };
                }) || [];
        } else if (e == '3') {
            setData = [];
        } else if (e == '4') {
            setData =
                skillList?.map(item => {
                    return {
                        ...item,
                        title: item.name,
                        icon: BlockEnum.Skill,
                    };
                }) || [];
        }
        return setData;
    };

    const onTabChange = e => {
        console.log('onTabChange', e);
        setTabIndex(e);
        setSearchNode(trandformData(e));
    };

    const search = (e: React.ChangeEvent<HTMLInputElement>) => {
        let searchFrom = trandformData(tabIndex);
        const searchNode = searchFrom.filter(item =>
            item.title.toLowerCase().includes(e.target.value.toLowerCase()),
        );
        setSearchNode(searchNode);
    };

    const createNode = item => {
        let createType;
        if (tabIndex == '2') {
            createType = BlockEnum.Agent;
        } else if (tabIndex == '3') {
            createType = BlockEnum.Tool;
        } else if (tabIndex == '4') {
            createType = BlockEnum.Skill;
        }

        const currentNode = getNode(nodeId);
        let createData = {};
        if (createType) {
            if (createType == BlockEnum.Tool) {
                createData = {
                    title:
                        item?.identity?.label[lang] ||
                        intl.formatMessage({ id: 'workflow.tool', defaultMessage: '' }),
                    desc: item.description?.human[lang] || item.description?.llm || '',
                    icon: item?.icon,
                    baseData: item,
                };
            } else {
                createData = {
                    title: item.title,
                    desc: item.description || '',
                    baseData: item,
                };
            }
        }

        const newNode = storeCreateNode(createType || item.icon, {
            position: getNodePosition(currentNode, props.position),
            data: createData,
        });
        const edgeInfo: any = {
            id: `${currentNode.id}-${newNode.id}-${props.sourceHandle}`,
            source: props.position == 'right' ? currentNode.id : newNode.id,
            target: props.position == 'right' ? newNode.id : currentNode.id,
        };

        if (props.sourceHandle) {
            if (props.position == 'right') {
                edgeInfo.sourceHandle = props.sourceHandle;
            } else {
                edgeInfo.targetHandle = props.sourceHandle;
            }
        }
        if (props.targetHandle) {
            if (props.position == 'right') {
                edgeInfo.targetHandle = props.targetHandle;
            } else {
                edgeInfo.sourceHandle = props.targetHandle;
            }
        }
        addEdges([edgeInfo]);
        setToolsShow(false);
        props.onSelect && props.onSelect(item);
        setPreventScrolling(true);
    };

    const scrollRef = useRef(null);

    useEffect(() => {
        const handleWheel = event => {
            event.stopPropagation();
        };

        const container = scrollRef.current;
        if (!container?.addEventListener) return;
        container.addEventListener('wheel', handleWheel, { passive: false });

        return () => {
            container.removeEventListener('wheel', handleWheel);
        };
    }, [showAddNodeBtn]);

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
    return (
        <div
            ref={ref}
            style={{ top: 'calc(50% - 9px)' }}
            className={` ${isHovering ? 'bg-slate-700' : ''}`}
        >
            <NodeToolbar
                offset={20}
                isVisible={toolsShow}
                position={props.position == 'left' ? Position.Left : Position.Right}
            >
                <div
                    ref={tools}
                    className="p-2 w-[240px] pt-4 bg-white rounded-md cursor-pointer border border-blue-100"
                >
                    <Input
                        onChange={search}
                        allowClear
                        placeholder={intl.formatMessage({
                            id: 'workflow.searchNode',
                            defaultMessage: '',
                        })}
                        prefix={<SearchOutlined />}
                    />
                    {/* {useNodeId()} */}
                    <Tabs
                        defaultActiveKey={tabIndex}
                        onChange={e => onTabChange(e)}
                        items={tabItems}
                    ></Tabs>
                    <div style={{ maxHeight: 'calc(100vh - 500px)' }} className="overflow-y-auto">
                        {tabIndex != '3'
                            ? searchNode.map((item, index) => (
                                  <Tooltip placement="left" title={item?.base?.data?.['descTools']}>
                                      <div
                                          onClick={e => {
                                              console.log(item);

                                              e.stopPropagation();
                                              createNode(item);
                                          }}
                                          className="hover:bg-slate-100 px-2 rounded"
                                          key={index}
                                      >
                                          <UserCon
                                              key={index}
                                              title={item.title}
                                              icon={item.icon}
                                          ></UserCon>
                                      </div>
                                  </Tooltip>
                              ))
                            : toolData?.list?.map(item => {
                                  return (
                                      <div>
                                          <div className="py-2">
                                              <Typography.Title level={5}>
                                                  {item?.identity?.label[lang]}
                                              </Typography.Title>
                                          </div>
                                          <div>
                                              {item?.tools?.map((tool, toolIndex) => {
                                                  return (
                                                      <div
                                                          className="flex items-center gap-2 px-2 hover:bg-slate-100 "
                                                          onClick={e => {
                                                              e.stopPropagation();
                                                              createNode({
                                                                  ...tool,
                                                                  authorization_status:
                                                                      item.authorization_status,
                                                                  icon: item?.identity?.icon,
                                                                  groupName: item?.identity?.name,
                                                                  credentials_for_provider:
                                                                      item?.credentials_for_provider,
                                                              });
                                                          }}
                                                      >
                                                          <UserCon
                                                              key={toolIndex}
                                                              title={
                                                                  tool?.identity?.label[lang] ||
                                                                  intl.formatMessage({
                                                                      id: 'workflow.tool',
                                                                      defaultMessage: '',
                                                                  })
                                                              }
                                                              icon={item?.identity?.icon}
                                                          ></UserCon>
                                                          {/* <div className="p-1  rounded-md flex justify-center items-center shrink-0">
                                                              <img
                                                                  className="size-6"
                                                                  src={item?.identity?.icon}
                                                                  alt=""
                                                              />
                                                          </div>
                                                          <div>
                                                              {tool?.identity?.label?.zh_Hans ||
                                                                  ''}
                                                          </div> */}
                                                      </div>
                                                  );
                                              })}
                                          </div>
                                      </div>
                                  );
                              })}
                    </div>
                </div>
            </NodeToolbar>
        </div>
    );
});
