/*
 * @LastEditors: biz
 */
import { agentCreate, batchAgentCreate } from '@/api/workflow';
import { useTagStore } from '@/store/tags';
import useUserStore, { UPDATE_NOTIFICATIONS } from '@/store/user';
import useSocketStore from '@/store/websocket';
import { CompressOutlined, DeleteOutlined, HistoryOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useSelections, useUpdateEffect } from 'ahooks';
import { Button, Modal, Progress, Skeleton, Spin, message } from 'antd';
import { forwardRef, memo, useEffect, useImperativeHandle, useMemo, useState } from 'react';
import TagSearch from '../TagSearch';
import ResultDisplay from './ResultDisplay';

interface BatchAgentParams {
    app_run_id: number;
    loop_count: number;
    loop_limit: number;
    supplement_prompt: string;
    loop_id: number;
}

interface BatchCreateProps {
    open: boolean;
    onCancel: () => void;
    onOk: () => Promise<void>;
    loading?: boolean;
    params?: BatchAgentParams;
    onReset?: () => void;
    onPreview?: (text: string) => void;
}

interface ContinueGenerateButtonProps {
    agentList: any[];
    batchParams: BatchAgentParams;
    onGenerate: (params: BatchAgentParams) => Promise<boolean>;
}

const ContinueGenerateButton = memo(
    ({ agentList, batchParams, onGenerate }: ContinueGenerateButtonProps) => {
        const intl = useIntl();
        const [loading, setLoading] = useState(false);
        const [hidden, setHidden] = useState(false);

        const shouldShow = useMemo(() => {
            if (!agentList?.length || !batchParams) return false;
            if (agentList.length >= batchParams.loop_limit) return false;
            return !hidden && agentList.length % batchParams.loop_count === 0;
        }, [agentList?.length, batchParams?.loop_count, batchParams?.loop_limit, hidden]);

        const handleClick = async () => {
            try {
                setLoading(true);
                const success = await onGenerate(batchParams);
                if (success) {
                    setHidden(true);
                }
            } finally {
                setLoading(false);
            }
        };

        useEffect(() => {
            setHidden(false);
        }, [agentList.length]);

        if (!shouldShow) return null;

        return (
            <Button
                type="primary"
                color="primary"
                variant="filled"
                size="small"
                loading={loading}
                onClick={handleClick}
            >
                {intl.formatMessage({ id: 'agent.batch.continue' })}
            </Button>
        );
    },
);

const BatchCreate = memo(
    forwardRef<BatchCreateRef, BatchCreateProps>(
        ({ open, onCancel, onOk, loading, params, onReset, onPreview }, ref) => {
            const intl = useIntl();
            const [batchParams, setBatchParams] = useState<BatchAgentParams | undefined>(params);
            const { tags, fetchTags } = useTagStore();
            const [agentList, setAgentList] = useState<any[]>([]);
            const [selectedTags, setSelectedTags] = useState<string[]>([]);
            const [agentTagsMap, setAgentTagsMap] = useState<Record<number | string, string[]>>({});
            const [selectedAgent, setSelectedAgent] = useState<any | null>(null);
            const [selectedAgentIndex, setSelectedAgentIndex] = useState<number>(-1);
            const batchMessages = useSocketStore(state =>
                state.getTypedMessages('generate_agent_batch'),
            );
            const [moreLoading, setMoreLoading] = useState(false);
            const [lastCheck, setLastCheck] = useState(Date.now());
            const { shouldComponentUpdate, clearUpdateNotification, setUpdateNotification } =
                useUserStore(state => ({
                    shouldComponentUpdate: state.shouldComponentUpdate,
                    clearUpdateNotification: state.clearUpdateNotification,
                    setUpdateNotification: state.setUpdateNotification,
                }));

            const resetState = () => {
                setAgentList([]);
                setSelectedTags([]);
                setAgentTagsMap({});
                setSelectedAgent(null);
                setSelectedAgentIndex(-1);
                unSelectAll();
            };

            const handleCloseAgentDetail = () => {
                setSelectedAgent(null);
                setSelectedAgentIndex(-1);
            };

            const { selected, allSelected, isSelected, toggle, unSelectAll, toggleAll } =
                useSelections(
                    agentList.map(item => item.id),
                    [],
                );

            const handleTagChange = (tags: string[]) => {
                setSelectedTags(tags);
            };

            useUpdateEffect(() => {
                handleBindTag();
            }, [selectedTags]);

            const handleBindTag = async () => {
                const currentSelect = agentList.map(x => x.id);
                const newTagsMap = { ...agentTagsMap };
                currentSelect.forEach(id => {
                    newTagsMap[id] = selectedTags;
                });
                setAgentTagsMap(newTagsMap);
                setAgentList(prev => prev.map(item => ({ ...item, tags: selectedTags })));
            };

            const handleAgentClick = (agent: any) => {
                setSelectedAgent(agent);
                const index = agentList.findIndex(item => item.key === agent.key);
                setSelectedAgentIndex(index);
            };

            useEffect(() => {
                if (open) {
                    setBatchParams(params);
                    setMoreLoading(true);
                }
            }, [params, open]);

            useUpdateEffect(() => {
                if (!open) return;
                const currentMessage = batchMessages
                    .filter(
                        item =>
                            item?.data?.app_run_id === batchParams?.app_run_id &&
                            item?.data?.exec_data?.loop_id === batchParams.loop_id,
                    )
                    .map((x, i) => {
                        const outputs = JSON.parse(x.data.exec_data.outputs.value);
                        return (Array.isArray(outputs) ? outputs : [outputs]).map((output, j) => ({
                            ...output,
                            key: `${i}-${j}`,
                            loop_id: x.data?.exec_data?.loop_id,
                            id: x.data?.exec_data?.outputs?.id || `${i}-${j}`,
                            tags: selectedTags.length
                                ? selectedTags
                                : agentTagsMap[x.data?.exec_data?.outputs?.id || `${i}-${j}`] || [],
                        }));
                    })
                    .flat()
                    .reverse();

                if (currentMessage?.length) {
                    setAgentList(prevList => {
                        const existingAgents = new Map(prevList.map(agent => [agent.key, agent]));
                        const mergedList = currentMessage.map(newAgent => {
                            const existingAgent = existingAgents.get(newAgent.key);
                            return existingAgent ? existingAgent : newAgent;
                        });
                        return mergedList;
                    });
                    setMoreLoading(false);
                }
            }, [batchMessages, agentTagsMap, selectedTags]);

            const handleOk = async () => {
                onOk?.();
            };

            const handleBatchGenerate = async (currentParams?: BatchAgentParams) => {
                try {
                    const params = currentParams || batchParams;
                    if (!params) return;

                    const res = await batchAgentCreate(params);
                    console.log(res);
                    if (res.code == 0) {
                        setBatchParams(prev => {
                            return {
                                ...prev,
                                ...res.data,
                            };
                        });
                        setMoreLoading(true);
                        return true;
                    }
                    return false;
                } catch (error) {
                    console.error(error);
                    return false;
                }
            };

            useImperativeHandle(ref, () => ({
                reset: resetState,
            }));

            const createAgents = () => {
                const reduxAgents = agentList.filter(item => !selected.includes(item.id));
                Modal.confirm({
                    title: intl.formatMessage({ id: 'agent.batch.confirm.title' }),
                    content: intl.formatMessage(
                        { id: 'agent.batch.confirm.content' },
                        { count: reduxAgents.length },
                    ),
                    centered: true,
                    mask: false,
                    onOk: async () => {
                        const formattedAgents = reduxAgents.map(agent => ({
                            name: agent.name,
                            description: agent.description,
                            obligations: agent.obligations,
                            abilities: agent.abilities.map(ability => ({
                                ...ability,
                                status: 1,
                            })),
                            tags: agent.tags.map(tag => Number(tag)),
                        }));
                        const res = await agentCreate({
                            agents: formattedAgents,
                        });
                        if (res.code == 0) {
                            message.success(
                                intl.formatMessage({ id: 'agent.batch.create.success' }),
                            );
                            handleOk();
                            setUpdateNotification(UPDATE_NOTIFICATIONS.AGENT_LIST, {
                                action: 'create',
                                data: {},
                            });
                        }
                    },
                });
            };
            const Footer = () => {
                return (
                    <div className="flex justify-end gap-2">
                        <div></div>
                        <div>
                            <Button onClick={createAgents} type="primary">
                                {intl.formatMessage({ id: 'agent.batch.button.confirm' })}
                            </Button>
                        </div>
                    </div>
                );
            };

            const MoreLoading = () => {
                let moreNumber =
                    (batchParams?.loop_count > batchParams.loop_limit
                        ? batchParams.loop_limit
                        : batchParams?.loop_count) || 0;
                if (batchParams?.loop_limit && agentList.length) {
                    const remaining = batchParams.loop_limit - agentList.length;
                    if (remaining < moreNumber) {
                        moreNumber = Math.max(0, remaining);
                    }
                }

                moreNumber = Math.floor(Math.max(0, moreNumber));

                if (moreNumber <= 0) return null;

                return Array.from({ length: moreNumber }).map((_, index) => (
                    <div
                        key={`l${index}`}
                        className="rounded-lg relative border p-4 border-gray-300"
                    >
                        <Skeleton active paragraph={{ rows: 2 }} />
                        <div className="absolute left-0 top-0 w-full h-full flex items-center justify-center">
                            <Spin size="large"></Spin>
                        </div>
                    </div>
                ));
            };

            const handleAgentChange = (values: any) => {
                if (selectedAgentIndex === -1) return;

                setAgentList(prev => {
                    const newList = [...prev];
                    newList[selectedAgentIndex] = {
                        ...newList[selectedAgentIndex],
                        ...values,
                    };
                    return newList;
                });
            };

            return (
                <Modal
                    title={intl.formatMessage({ id: 'agent.batch.title' })}
                    destroyOnClose
                    className="min-w-[1000px]"
                    bodyProps={{
                        className: '!h-[700px] overflow-y-auto p-4',
                    }}
                    footer={Footer}
                    open={open}
                    onCancel={onCancel}
                    centered
                    onOk={handleOk}
                    confirmLoading={loading}
                >
                    <div className="flex flex-col gap-4 h-full relative">
                        <div className="flex flex-col gap-2 h-full">
                            <div className="flex gap-2">
                                <div className="w-full">
                                    <TagSearch
                                        allowClear
                                        onChange={handleTagChange}
                                        placeholder={intl.formatMessage({
                                            id: 'agent.batch.set.tags',
                                        })}
                                        onTagChange={() => {
                                            fetchTags();
                                        }}
                                        showAddButton={false}
                                        listStyle="horizontal"
                                        className="w-full flex-1"
                                    />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between items-center px-2 mt-4">
                                    <div className="flex items-center gap-2">
                                        <span>
                                            {intl.formatMessage({ id: 'agent.batch.generated' })}{' '}
                                            {agentList?.length}/{batchParams.loop_limit}
                                        </span>
                                        <ContinueGenerateButton
                                            agentList={agentList}
                                            batchParams={batchParams}
                                            onGenerate={handleBatchGenerate}
                                        />
                                    </div>
                                </div>
                                {agentList?.length != batchParams.loop_limit && (
                                    <div className="px-2">
                                        <Progress
                                            percent={
                                                (agentList?.length / batchParams.loop_limit) * 100
                                            }
                                            size="small"
                                            showInfo={false}
                                        />
                                    </div>
                                )}
                            </div>

                            <div className="flex-1 overflow-y-auto">
                                <div className="grid grid-cols-2 gap-6">
                                    {moreLoading && <MoreLoading />}
                                    {agentList.map(item => (
                                        <div
                                            key={item.key}
                                            className={`rounded-lg relative border p-4 cursor-pointer transition-all ${
                                                isSelected(item.id)
                                                    ? 'border-gray-100 text-gray-300'
                                                    : 'border-gray-300 hover:border-blue-500 '
                                            }`}
                                            onClick={() => handleAgentClick(item)}
                                        >
                                            <Button
                                                type="text"
                                                icon={
                                                    isSelected(item.id) ? (
                                                        <HistoryOutlined />
                                                    ) : (
                                                        <DeleteOutlined />
                                                    )
                                                }
                                                className={`absolute right-2 top-2`}
                                                onClick={e => {
                                                    e.stopPropagation();
                                                    toggle(item.id);
                                                }}
                                            />
                                            <div
                                                className={`font-medium ${
                                                    isSelected(item.id)
                                                        ? 'border-gray-100 text-gray-300'
                                                        : 'text-blue-600'
                                                }`}
                                            >
                                                {item.name}
                                            </div>
                                            <div
                                                className={`mt-2 line-clamp-2 ${
                                                    isSelected(item.id)
                                                        ? 'border-gray-100 text-gray-300'
                                                        : 'text-gray-500'
                                                }`}
                                            >
                                                {item.description}
                                            </div>
                                            {/* <TagSelect
                                                options={tags}
                                                value={item.tags}
                                                className="w-full mt-2"
                                                variant="borderless"
                                                listStyle='horizontal'
                                                tagColor={isSelected(item.id) ? 'default' : 'blue'}
                                                aria-readonly
                                                disabled={true}   
                                                onClick={e => e.stopPropagation()}
                                            /> */}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                    {selectedAgent && (
                        <div className="absolute z-[1011] left-0 top-0 bg-white w-full h-full flex flex-col shadow-md rounded-lg">
                            <div className="flex-1 overflow-auto relative">
                                <ResultDisplay
                                    initialValues={selectedAgent}
                                    loading={false}
                                    onChange={handleAgentChange}
                                />
                                <Button
                                    type="text"
                                    icon={<CompressOutlined />}
                                    onClick={handleCloseAgentDetail}
                                    className="absolute top-2 right-2"
                                ></Button>
                            </div>
                        </div>
                    )}
                </Modal>
            );
        },
    ),
);

export interface BatchCreateRef {
    reset: () => void;
}

export default BatchCreate;
