import { TagSelect } from '@/components/TagSearch';
import { useTagStore } from '@/store/tags';
import { useNodePanel } from '@/hooks/useNodePanel';
import { SearchOutlined } from '@ant-design/icons';
import { ProForm, ProFormItem, ProFormRadio, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Spin, Tabs } from 'antd';
import { debounce } from 'lodash';
import VirtualList from 'rc-virtual-list';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import DraggableList from '../DraggableList';
import { useMount, useTrackedEffect, useUpdateEffect, useWhyDidYouUpdate } from 'ahooks';



interface NodePanelContentProps {
    visibleTabs?: ('node' | 'agent' | 'tool' | 'skill' | 'workflow')[];
    defaultActiveTab?: string;
    showTeamSwitch?: boolean;
    showTagSearch?: boolean;
    isMinWidth?: boolean;
    isCollapsed?: boolean;
    onWidthChange?: (width: number) => void;
    isNodePanel?: boolean;
    onItemClick?: (item: any, type?: string) => void;
}

interface ListItemProps {
    data: any;
    index: number;
    onDragStart: (event: React.DragEvent, type: string, item: any) => void;
    onItemClick: (item: any) => void;
    type: 'workflow' | 'normal' | 'tools';
    typeBadge?: {
        icon: string;
        tooltip: string;
        color: string;
    };
}

export default memo(
    ({
        visibleTabs,
        defaultActiveTab,
        showTeamSwitch = true,
        showTagSearch = true,
        isMinWidth = false,
        isCollapsed = false,
        onItemClick,
        isNodePanel = false,
    }: NodePanelContentProps) => {
        const intl = useIntl();
        const { tags } = useTagStore();
        const isFirstGettingData = useRef(true);
        useMount(()=>{
            console.log('131');
            
        })
        // Use the new hook to manage all node panel functionality
        const {
            filterData,
            onFilterChange,
            tabIndex,
            setTabIndex,
            tabConfigs,
            tabItems,
            getCurrentTabConfig,
            onDragStart,
            lang,
        } = useNodePanel({
            visibleTabs,
            defaultActiveTab,
            cacheExpiry: 60000,
        });
        // useTrackedEffect((changes)=>{
        //     console.log('Index of changed dependencies: ', changes);
        // },[ filterData,
        //     onFilterChange,
        //     tabIndex,
        //     setTabIndex,
        //     tabConfigs,
        //     tabItems,
        //     getCurrentTabConfig,
        //     onDragStart,
        //     lang])
        const RenderNodeList = useCallback(
            ({ tabIndex, showName = true,autoHeight=false }) => {
                const currentConfig = tabConfigs.find(config => config.key === tabIndex);
                const [list, setList] = useState<any[]>([]);
                const [loading, setLoading] = useState(true);
                const [displayList, setDisplayList] = useState<any[]>([]);
                const [pageSize] = useState(20);
                const [containerHeight, setContainerHeight] = useState(500);
                const containerRef = useRef<HTMLDivElement>(null);
                const dataFetchedRef = useRef(false);
              
              
                const getItemHeight = useCallback(
                    (item?: any) => {
                        if (currentConfig?.type === 'tools' && item) {
                          
                            const titleHeight = 60;
                            const toolItemHeight = 36;
                            const toolsCount = item.tools?.length || 0;
                            return titleHeight + toolsCount * toolItemHeight;
                        }
                        return 54; 
                    },
                    [currentConfig?.type],
                );

            
                const getEstimatedTotalHeight = useCallback(() => {
                    if (currentConfig?.type === 'tools') {
                        return list.reduce((total, item) => total + getItemHeight(item), 0);
                    }
                    return list.length * getItemHeight();
                }, [currentConfig?.type, list, getItemHeight]);

                useEffect(() => {
                    const updateContainerHeight = () => {
                        if (containerRef.current) {
                            const height = containerRef.current.clientHeight;
                            setContainerHeight(height);
                        }
                    };

                    const handleResize = (e: CustomEvent) => {
                        setContainerHeight(e.detail.height);
                    };

                    updateContainerHeight();

                    if (containerRef.current) {
                        containerRef.current.addEventListener(
                            'containerResize',
                            handleResize as EventListener,
                        );
                    }

                    window.addEventListener('resize', updateContainerHeight);

                    return () => {
                        if (containerRef.current) {
                            containerRef.current.removeEventListener(
                                'containerResize',
                                handleResize as EventListener,
                            );
                        }
                        window.removeEventListener('resize', updateContainerHeight);
                    };
                }, []);

                useEffect(() => {
                    return () => {
                        dataFetchedRef.current = false;
                    };
                }, [currentConfig?.tabKey]);
            
                const fetchData = async () => {
                    if (
                        dataFetchedRef.current &&
                        !filterData.keyword &&
                        filterData.tag.length === 0
                    ) {
                        return;
                    }

                    setLoading(true);
                    try {
                        if (!currentConfig) return;
                        const data = await currentConfig.getData();
                        const processedData =
                            data?.map((item: any, index: number) => ({
                                ...item,
                                id: `${currentConfig.tabKey}-${index}`,
                            })) || [];

                        setList(processedData);
                        setDisplayList(processedData.slice(0, pageSize));
                        dataFetchedRef.current = true;
                    } catch (error) {
                        console.error('Failed to fetch data:', error);
                    } finally {
                        setLoading(false);
                    }
                };
                useMount(()=>{
                    if(!isFirstGettingData.current&&list.length>0){
                        return;
                    }
                    isFirstGettingData.current = false;
                    fetchData();
                })
                useWhyDidYouUpdate('RenderNodeList',[list,currentConfig,filterData,pageSize])
                useUpdateEffect(() => {
                    
                    fetchData();
                    
                }, [currentConfig, filterData, pageSize]);

                const loadMoreData = useCallback(() => {
                    const currentLength = displayList.length;
                    if (currentLength < list.length) {
                        const nextItems = list.slice(currentLength, currentLength + pageSize);
                        setDisplayList(prev => [...prev, ...nextItems]);
                    }
                }, [displayList.length, list, pageSize]);

                const debouncedLoadMore = useCallback(debounce(loadMoreData, 100), [loadMoreData]);

                const onScroll = (e: React.UIEvent<HTMLElement, UIEvent>) => {
                    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
                    const isNearBottom = scrollHeight - scrollTop - clientHeight < 10;

                    if (isNearBottom) {
                        debouncedLoadMore();
                    }
                };

                const onToolsScroll = (e: React.UIEvent<HTMLElement, UIEvent>) => {
                    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;

                    let displayedContentHeight = 0;
                    for (let i = 0; i < displayList.length; i++) {
                        displayedContentHeight += getItemHeight(displayList[i]);
                    }

                    const isNearDisplayedBottom =
                        scrollTop + clientHeight >= displayedContentHeight - 50;

                    if (isNearDisplayedBottom && displayList.length < list.length) {
                        debouncedLoadMore();
                    }
                };

                const handleItemClick = useCallback(
                    (item: any) => {
                        if (!currentConfig) return;
                        console.log('Clicked item:', item);

                        switch (currentConfig.tabKey) {
                            case 'tool':
                                console.log(`Tool ${item.identity?.label?.[lang]}`);
                                break;
                            case 'workflow':
                                console.log(`Workflow ${item.data?.title}`);
                                break;
                            case 'agent':
                                console.log(`Agent ${item.data?.title}`);
                                break;
                            default:
                                console.log(`Clicked ${currentConfig.tabKey} item:`, item);
                        }

                        if (onItemClick) {
                            onItemClick(item, currentConfig.tabKey);
                        }
                    },
                    [currentConfig, lang, onItemClick],
                );

                const ListItem = memo(
                    ({ data, index, onDragStart, onItemClick, type, typeBadge }: ListItemProps) => (
                        <DraggableList
                            typeBadge={typeBadge}
                            list={[data]}
                            onDragStart={onDragStart}
                            type={type}
                            onItemClick={onItemClick}
                        />
                    ),
                );

                if (!currentConfig) return null;

                return (
                    <div ref={containerRef} className="overflow-y-auto h-full">
                        <Spin spinning={loading}>
                            {filterData?.keyword ? (
                                <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-2">
                                    {displayList.map(item => (
                                        <ListItem
                                            key={item.id}
                                            data={item}
                                            index={displayList.indexOf(item)}
                                            onDragStart={onDragStart}
                                            onItemClick={handleItemClick}
                                            type={currentConfig.type}
                                            typeBadge={
                                                filterData?.keyword &&
                                                currentConfig.tabKey != 'node'
                                                    ? {
                                                          icon: `/icons/${currentConfig.tabKey}.svg`,
                                                          tooltip: currentConfig.tabKey,
                                                          color: '#1b64f3',
                                                      }
                                                    : undefined
                                            }
                                        />
                                    ))}
                                </div>
                            ) : currentConfig.type === 'tools' ? (
                                <div
                                    className="overflow-y-auto"
                                    style={{ height: autoHeight?containerHeight:undefined }}
                                    onScroll={onToolsScroll}
                                >
                                    <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-2">
                                        {displayList.map(item => (
                                            <ListItem
                                                key={item.id}
                                                data={item}
                                                index={displayList.indexOf(item)}
                                                onDragStart={onDragStart}
                                                onItemClick={handleItemClick}
                                                type={currentConfig.type}
                                                typeBadge={
                                                    filterData?.keyword &&
                                                    currentConfig.tabKey != 'node'
                                                        ? {
                                                              icon: `/icons/${currentConfig.tabKey}.svg`,
                                                              tooltip: currentConfig.tabKey,
                                                              color: '#1b64f3',
                                                          }
                                                        : undefined
                                                }
                                            />
                                        ))}
                                    </div>
                                </div>
                            ) : (
                             
                                <VirtualList
                                    data={displayList}
                                    height={autoHeight?containerHeight:undefined}
                                    itemHeight={getItemHeight()}
                                    itemKey="id"
                                    onScroll={onScroll}
                                >
                                    {item => (
                                        <ListItem
                                            data={item}
                                            index={displayList.indexOf(item)}
                                            onDragStart={onDragStart}
                                            onItemClick={handleItemClick}
                                            type={currentConfig.type}
                                            typeBadge={
                                                filterData?.keyword &&
                                                currentConfig.tabKey != 'node'
                                                    ? {
                                                          icon: `/icons/${currentConfig.tabKey}.svg`,
                                                          tooltip: currentConfig.tabKey,
                                                          color: '#1b64f3',
                                                      }
                                                    : undefined
                                            }
                                        />
                                    )}
                                </VirtualList>
                            )}
                        </Spin>
                    </div>
                );
            },
            isNodePanel?[tabIndex]:[tabIndex, filterData, isMinWidth, tabConfigs, onDragStart, lang, onItemClick],
        );





        return (
            <div className="h-full flex flex-col">
                {!isCollapsed && (
                    <div className="px-4 py-3">
                        <ProForm
                            submitter={false}
                            initialValues={filterData}
                            onValuesChange={onFilterChange}
                        >
                            {showTeamSwitch && (
                                <div className="flex gap-2 items-center text-base mb-4">
                                    {intl.formatMessage({
                                        id: 'workflow.nodeList',
                                        defaultMessage: '',
                                    })}
                                    <ProFormRadio.Group
                                        name="team"
                                        fieldProps={{
                                            options: [
                                                {
                                                    label: intl.formatMessage({
                                                        id: 'workflow.team',
                                                        defaultMessage: '',
                                                    }),
                                                    value: 2,
                                                },
                                                {
                                                    label: intl.formatMessage({
                                                        id: 'workflow.mine',
                                                        defaultMessage: '',
                                                    }),
                                                    value: 1,
                                                },
                                            ],
                                            size: 'small',
                                            optionType: 'button',
                                            buttonStyle: 'solid',
                                        }}
                                        formItemProps={{ className: 'mb-0' }}
                                    />
                                </div>
                            )}

                            <ProFormText
                                fieldProps={{
                                    prefix: <SearchOutlined />,
                                    placeholder: intl.formatMessage({
                                        id: 'workflow.search',
                                        defaultMessage: '',
                                    }),
                                }}
                                name="keyword"
                            />
                            {
                                showTagSearch && (
                                    
                            <div className="w-full">
                                <ProFormItem name={'tag'}>
                                    <TagSelect
                                        className="w-full"
                                        options={tags}
                                        listStyle={isMinWidth ? 'horizontal' : 'vertical'}
                                        allowClear
                                        placeholder={intl.formatMessage({
                                            id: 'creation.placeholder.selectTags',
                                            defaultMessage: '',
                                        })}
                                        onChange={e => {}}
                                    ></TagSelect>
                                </ProFormItem>
                            </div>
                                )
                            }
                        </ProForm>
                        {filterData?.keyword ? null : (
                            <Tabs
                                activeKey={tabIndex}
                                items={tabItems}
                                onChange={key => {
                                    setTabIndex(key);
                                }}
                            />
                        )}
                    </div>
                )}
                <div className="flex-1 overflow-y-auto">
                    {filterData?.keyword ? (
                        <div className="grid gap-4">
                            {tabConfigs.map((item, index) => (
                                <div key={item.key} className="space-y-2">
                                    {!isCollapsed && (
                                        <div className="text-base font-medium px-2">
                                            {intl.formatMessage({
                                                id: item.label,
                                                defaultMessage: item.defaultMessage,
                                            })}
                                        </div>
                                    )}
                                    <RenderNodeList
                                        key={item.key}
                                        tabIndex={index + 1 + ''}
                                        showName={!isMinWidth}
                                        autoHeight={true}
                                    />
                                </div>
                            ))}
                        </div>
                    ) : (
                        <RenderNodeList tabIndex={tabIndex} showName={!isMinWidth} />
                    )}
                </div>
            </div>
        );
    },
);
