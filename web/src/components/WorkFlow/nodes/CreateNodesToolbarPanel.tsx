/*
 * @LastEditors: biz
 */
import { ObjectVariable, Variable } from '@/py2js/variables.js';
import { SearchOutlined } from '@ant-design/icons';
import autoAnimate from '@formkit/auto-animate';
import { Node, NodeProps, NodeToolbar, Position, useNodeId, useReactFlow } from '@xyflow/react';
import { useHover, useMount, useUpdateEffect } from 'ahooks';
import type { TabsProps } from 'antd';
import { Input, Tabs, Tooltip } from 'antd';
import Fuse from 'fuse.js';
import { debounce } from 'lodash';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
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

    useUpdateEffect(() => {
        if (!toolsShow) {
            setTabIndex('1');
            setSearchNode(trandformData('1'));
        }
    }, [toolsShow]);
    // useEffect(() => {
    //     setShowAddNodeBtn(props.data.selected);
    //     if (!props.data.selected) {
    //         setToolsShow(false);
    //     }
    // }, [props, tools]);
    useOutsideClick(tools, () => {
        setToolsShow(false);
    });

    const trandformData = useCallback(
        e => {
            let setData = null;
            if (e == '1') {
                setData = baseNodes;
            } else if (e == '2') {
                setData =
                    agentList.map(item => {
                        return {
                            ...item,
                            title: item.name,
                        };
                    }) || [];
            } else if (e == '3') {
                setData = [];
                toolData?.list?.forEach((category, categoryIndex) => {
                    category.tools?.forEach((tool, toolIndex) => {
                        setData.push({
                            ...tool,
                            title:
                                tool?.identity?.label[lang] ||
                                intl.formatMessage({
                                    id: 'workflow.tool',
                                    defaultMessage: '',
                                }),
                            categoryName: category?.identity?.label[lang],
                            categoryIcon: category?.identity?.icon,
                            authorization_status: category.authorization_status,
                            groupName: category?.identity?.name,
                            credentials_for_provider: category?.credentials_for_provider,
                            categoryIndex,
                            toolIndex,
                        });
                    });
                });
            } else if (e == '4') {
                setData =
                    skillList?.map(item => {
                        return {
                            ...item,
                            title: item.name,
                        };
                    }) || [];
            }
            return setData;
        },
        [baseNodes, agentList, toolData, skillList, lang, intl],
    );

    const onTabChange = e => {
        console.log('onTabChange', e);
        setTabIndex(e);
        setSearchNode(trandformData(e));
    };

    const performSearch = useCallback(
        (keyword: string, currentTabIndex: string) => {
            let searchFrom = trandformData(currentTabIndex);

            if (!keyword) {
                setSearchNode(searchFrom);
                return;
            }

            let searchKeys: string[] = [];
            if (currentTabIndex === '1') {
                searchKeys = ['title', 'type', 'data.desc', 'data.title'];
            } else if (currentTabIndex === '2') {
                searchKeys = ['title', 'name', 'description'];
            } else if (currentTabIndex === '3') {
                searchKeys = [
                    'title',
                    'categoryName',
                    'description.human.zh_Hans',
                    'description.human.en_US',
                ];
            } else if (currentTabIndex === '4') {
                searchKeys = ['title', 'name', 'description'];
            }

            const fuse = new Fuse(searchFrom, {
                keys: searchKeys,
                threshold: 0.3,
                includeScore: true,
            });

            const results = fuse.search(keyword);
            const searchResults = results.map(result => result.item);
            setSearchNode(searchResults);
        },
        [trandformData],
    );

    const debouncedSearch = useCallback(
        debounce((keyword: string, currentTabIndex: string) => {
            performSearch(keyword, currentTabIndex);
        }, 300),
        [performSearch],
    );

    const search = (e: React.ChangeEvent<HTMLInputElement>) => {
        const keyword = e.target.value;
        debouncedSearch(keyword, tabIndex);
    };

    useEffect(() => {
        return () => {
            debouncedSearch.cancel();
        };
    }, [debouncedSearch]);

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
        let createData: any = {};

        if (createType) {
            if (createType == BlockEnum.Tool) {
                createData = {
                    title:
                        item?.identity?.label[lang] ||
                        intl.formatMessage({ id: 'workflow.tool', defaultMessage: '' }),
                    desc: item.description?.human[lang] || item.description?.llm || '',
                    icon: item?.icon || item?.categoryIcon,
                    baseData: item,
                };

                if (item.output) {
                    if (Array.isArray(item.output) && item.output.length > 0) {
                        const toolVariables = new ObjectVariable('output', 'object');
                        item.output.forEach(item => {
                            const variable = new Variable(item.name, item.type);
                            toolVariables.addProperty(item.name, variable);
                        });
                        createData.outputInfo = toolVariables.toObject();
                    } else {
                        createData.outputInfo = item.output;
                    }
                }
            } else {
                createData = {
                    title: item.title,
                    desc: item.description || '',
                    baseData: item,
                };
                if (item.icon) {
                    createData.icon = item.icon;
                }
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
                    {/* <NodePanelContent onItemClick={(e)=>{
                        console.log('onItemClick',e);
                    }}></NodePanelContent> */}
                    <Input
                        onChange={search}
                        allowClear
                        placeholder={intl.formatMessage({
                            id: 'workflow.searchNode',
                            defaultMessage: '',
                        })}
                        prefix={<SearchOutlined />}
                    />
                    <Tabs
                        defaultActiveKey={tabIndex}
                        onChange={e => onTabChange(e)}
                        items={tabItems}
                    ></Tabs>
                    <div style={{ maxHeight: 'calc(100vh - 500px)' }} className="overflow-y-auto">
                        {tabIndex == '3'
                            ? (() => {
                                  const groupedTools = searchNode.reduce(
                                      (groups: any, tool: any) => {
                                          const categoryName = tool.categoryName || 'Unknown';
                                          if (!groups[categoryName]) {
                                              groups[categoryName] = {
                                                  categoryName,
                                                  categoryIcon: tool.categoryIcon,
                                                  tools: [],
                                              };
                                          }
                                          groups[categoryName].tools.push(tool);
                                          return groups;
                                      },
                                      {},
                                  );

                                  return Object.values(groupedTools).map(
                                      (group: any, groupIndex) => (
                                          <div key={groupIndex}>
                                              <div className="py-2">
                                                  <UserCon
                                                      title={group.categoryName}
                                                      icon={group.categoryIcon}
                                                  />
                                              </div>
                                              <div>
                                                  {group.tools.map((tool, toolIndex) => (
                                                      <div
                                                          key={toolIndex}
                                                          className="flex items-center gap-2 px-2 hover:bg-slate-100 rounded py-2 text-gray-500"
                                                          onClick={e => {
                                                              e.stopPropagation();
                                                              createNode(tool);
                                                          }}
                                                      >
                                                          {tool.title}
                                                      </div>
                                                  ))}
                                              </div>
                                          </div>
                                      ),
                                  );
                              })()
                            : searchNode.map((item, index) => (
                                  <Tooltip
                                      key={index}
                                      placement="left"
                                      title={item?.base?.data?.['descTools']}
                                  >
                                      <div
                                          onClick={e => {
                                              console.log(item);
                                              e.stopPropagation();
                                              createNode(item);
                                          }}
                                          className="hover:bg-slate-100 px-2 rounded"
                                      >
                                          <UserCon title={item.title} icon={item.icon} />
                                      </div>
                                  </Tooltip>
                              ))}
                    </div>
                </div>
            </NodeToolbar>
        </div>
    );
});
