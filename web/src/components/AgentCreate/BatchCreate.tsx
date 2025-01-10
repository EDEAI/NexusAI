/*
 * @LastEditors: biz
 */
import { batchAgentCreate, bindTag } from '@/api/workflow';
import useSocketStore from '@/store/websocket';
import { CompressOutlined, ExpandOutlined } from '@ant-design/icons';
import { useSelections, useUpdateEffect } from 'ahooks';
import { Button, Modal, Progress, Spin, message } from 'antd';
import { forwardRef, memo, useEffect, useImperativeHandle, useMemo, useState } from 'react';
import TagSearch, { TagSelect, useTags } from '../TagSearch';
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
}

interface ContinueGenerateButtonProps {
    agentList: any[];
    batchParams: BatchAgentParams;
    onGenerate: (params: BatchAgentParams) => Promise<boolean>;
}

const ContinueGenerateButton = memo(
    ({ agentList, batchParams, onGenerate }: ContinueGenerateButtonProps) => {
        const [loading, setLoading] = useState(false);
        const [hidden, setHidden] = useState(false);

        // 判断是否显示按钮
        const shouldShow = useMemo(() => {
            if (!agentList?.length || !batchParams) return false;
            // 数量达到上限时不显示
            if (agentList.length >= batchParams.loop_limit) return false;
            // 数量必须是 loop_count 的倍数
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

        // 当 agentList 长度变化时，重置 hidden 状态
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
                继续生成下一批
            </Button>
        );
    },
);

const BatchCreate = memo(
    forwardRef<BatchCreateRef, BatchCreateProps>(
        ({ open, onCancel, onOk, loading, params, onReset }, ref) => {
            const [batchParams, setBatchParams] = useState<BatchAgentParams | undefined>(params);
            const { tagList,refreshTags } = useTags();
            const [agentList, setAgentList] = useState<any[]>([]);
            const [selectedTags, setSelectedTags] = useState<string[]>([]);
            const [agentTagsMap, setAgentTagsMap] = useState<Record<number | string, string[]>>({});
            const [selectedAgent, setSelectedAgent] = useState<any | null>(null);
            const batchMessages = useSocketStore(state =>
                state.getTypedMessages('generate_agent_batch'),
            );
            const setFlowMessage = useSocketStore(state => state.setFlowMessage);

            // 重置组件状态
            const resetState = () => {
                setAgentList([]);
                setSelectedTags([]);
                setAgentTagsMap({});
                setSelectedAgent(null);
                unSelectAll()
            };

            const handleCloseAgentDetail = () => {
                setSelectedAgent(null);
            };

            const { selected, allSelected, isSelected, toggle, unSelectAll, toggleAll } =
                useSelections(
                    agentList.map(item => item.id),
                    [],
                );

            const handleTagChange = (tags: string[]) => {
                setSelectedTags(tags);
            };

            const handleBindTag = async () => {
                try {
                    const res = await bindTag(selectedTags, selected);
                    if (res.code === 0) {
                        message.success('标签设置成功');

                        const newTagsMap = { ...agentTagsMap };
                        selected.forEach(id => {
                            newTagsMap[id] = selectedTags;
                        });
                        setAgentTagsMap(newTagsMap);

                        setAgentList(prev =>
                            prev.map(item =>
                                selected.includes(item.id) ? { ...item, tags: selectedTags } : item,
                            ),
                        );
                        unSelectAll();
                    }
                } catch (error) {
                    message.error('标签设置失败');
                }
            };

            const handleSingleAgentTagChange = async (id: number, tags: string[]) => {
                try {
                    const res = await bindTag(tags, [id]);
                    if (res.code === 0) {
                        setAgentTagsMap(prev => ({
                            ...prev,
                            [id]: tags,
                        }));

                        setAgentList(prev =>
                            prev.map(item => (item.id === id ? { ...item, tags } : item)),
                        );
                    }
                } catch (error) {
                    message.error('标签设置失败');
                }
            };

            const handleAgentClick = (agent: any) => {
                setSelectedAgent(agent);
            };

            useEffect(() => {
                if (open) {
                    // 如果是通过 handleBatchGenerate 打开（有新的 params）
                    // if (params && (!batchParams || params.app_run_id !== batchParams.app_run_id)) {
                    //     resetState();
                    // }
                    setBatchParams(params);
                }
            }, [params, open]);

            // 当模态框关闭时重置状态
            // useEffect(() => {
            //     if (!open) {
            //         resetState();
            //     }
            // }, [open]);

            useUpdateEffect(() => {
                if (!open) return;
                const currentMessage = batchMessages
                    .filter(
                        item =>
                            item?.data?.app_run_id === batchParams?.app_run_id &&
                            item?.data?.exec_data?.loop_id === batchParams.loop_id,
                    )
                    .map((x, i) => ({
                        ...JSON.parse(x.data.exec_data.outputs.value),
                        key: i,
                        loop_id: x.data?.exec_data?.loop_id,
                        id: x.data?.exec_data?.outputs?.id || i,
                        tags: agentTagsMap[x.data?.exec_data?.outputs?.id || i] || [],
                    }))
                    .reverse();

                if (currentMessage?.length) {
                    setAgentList(currentMessage);
                }
            }, [batchMessages, agentTagsMap]);

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
                        return true;
                    }
                    return false;
                } catch (error) {
                    console.error(error);
                    return false;
                }
            };

            // 暴露重置方法给父组件
            useImperativeHandle(ref, () => ({
                reset: resetState,
            }));

            return (
                <Modal
                    title="批量生成智能体"
                    destroyOnClose
                    className="min-w-[1000px]"
                    bodyProps={{
                        className: '!h-[700px] overflow-y-auto p-4',
                    }}
                    footer={null}
                    open={open}
                    onCancel={onCancel}
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
                                        onTagChange={() => {
                                            
                                            refreshTags();
                                        
                                        }}
                                        className="w-full flex-1"
                                    />
                                </div>
                                <Button
                                    disabled={!selected?.length}
                                    type="primary"
                                    onClick={handleBindTag}
                                >
                                    {selected?.length ? `为${selected?.length}个智能体` : ''}
                                    设置标签
                                </Button>
                            </div>
                            <div>
                                <div className="flex justify-between items-center px-2 mt-4">
                                    <div className="flex items-center gap-2">
                                        <span>
                                            已生成智能体 {agentList?.length}/
                                            {batchParams.loop_limit}
                                        </span>
                                        <ContinueGenerateButton
                                            agentList={agentList}
                                            batchParams={batchParams}
                                            onGenerate={handleBatchGenerate}
                                        />
                                    </div>
                                    <a onClick={toggleAll}>{allSelected ? '取消全选' : '全选'}</a>
                                </div>
                                <div className="px-2">
                                    <Progress
                                        percent={(agentList?.length / batchParams.loop_limit) * 100}
                                        size="small"
                                        showInfo={false}
                                    />
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto">
                                <div className="grid grid-cols-2 gap-6">
                                    {agentList.map(item => (
                                        <div
                                            key={item.key}
                                            className={`rounded-lg relative border p-4 cursor-pointer transition-all hover:border-blue-500 ${
                                                isSelected(item.id)
                                                    ? 'border-blue-500 bg-blue-100'
                                                    : 'border-gray-200'
                                            }`}
                                            onClick={() => toggle(item.id)}
                                        >
                                            <Button
                                                type="text"
                                                icon={<ExpandOutlined />}
                                                className="absolute right-2 top-2"
                                                onClick={e => {
                                                    e.stopPropagation();
                                                    handleAgentClick(item);
                                                }}
                                            />
                                            <div className="text-blue-600 font-medium">
                                                {item.name}
                                            </div>
                                            <div className="text-gray-500 mt-2">
                                                {item.description}
                                            </div>
                                            <TagSelect
                                                options={tagList}
                                                value={item.tags}
                                                className="w-full mt-2"
                                                variant="borderless"
                                                onChange={tags => {
                                                    handleSingleAgentTagChange(item.id, tags);
                                                }}
                                                onClick={e => e.stopPropagation()}
                                            />
                                        </div>
                                    ))}
                                </div>
                                {agentList?.length ? null : (
                                    <div className="flex justify-center items-center flex-col w-full h-full">
                                        <Spin></Spin>
                                        <div>生成中...</div>
                                    </div>
                                )}
                            </div>
                            {/* <div className="-mb-4 py-1">
                        已生成{agentList?.length || 0}个智能体，是否继续生成？
                        <Button size="small">继续生成</Button>
                    </div> */}
                        </div>
                    </div>
                    {selectedAgent && (
                        <div className="absolute z-[1011] left-0 top-0 bg-white w-full h-full flex flex-col shadow-md rounded-lg">
                            <div className="flex-1 overflow-auto relative">
                                <ResultDisplay
                                    initialValues={selectedAgent}
                                    loading={false}
                                    readOnly={true}
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
