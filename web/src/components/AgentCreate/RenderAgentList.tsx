import { bindTag } from '@/api/workflow';
import { useAutoAnimate } from '@formkit/auto-animate/react';
import { useSelections } from 'ahooks';
import { Button, message } from 'antd';
import { DefaultOptionType } from 'antd/es/select';
import { memo, useEffect, useState } from 'react';
import TagSearch, { TagSelect } from '../TagSearch';

interface AgentItem {
    id: number;
    key: number;
    name: string;
    description: string;
    obligations: string;
    abilities: Array<{
        name: string;
        content: string;
        output_format: number;
    }>;
    tags?: string[];
}

interface RenderAgentListProps {
    tagList: DefaultOptionType[];
    onSelect?: (keys: (string | number)[]) => void;
    onTagChange?: (tags: string[]) => void;
    data?: AgentItem[];
    columns?: number;
}

export const RenderAgentList = memo(
    ({ tagList, onSelect, onTagChange, data, columns = 3 }: RenderAgentListProps) => {
        const [agentList, setAgentList] = useState<AgentItem[]>([]);
        const [selectedTags, setSelectedTags] = useState<string[]>([]);

        const handleTagChange = (tags: string[]) => {
            setSelectedTags(tags);
            onTagChange?.(tags);
        };

        const handleSingleAgentTagChange = async (id: number, tags: string[]) => {
            try {
                const res = await bindTag(tags, [id]);
                if (res.code === 0) {
                    // message.success('标签设置成功');
                    setAgentList(prev =>
                        prev.map(item => (item.id === id ? { ...item, tags } : item)),
                    );
                }
            } catch (error) {
                message.error('标签设置失败');
            }
        };

        useEffect(() => {
            if (data) {
                setAgentList(prev => {
                    return data.map(newItem => {
                        const existingItem = prev?.find(p => p.id === newItem.id);
                        return {
                            ...newItem,
                            tags: existingItem?.tags || newItem.tags || [],
                        };
                    });
                });
            }
        }, [data]);

        const handleBindTag = async () => {
            try {
                const res = await bindTag(selectedTags, selected);
                if (res.code === 0) {
                    message.success('标签设置成功');

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

        const {
            selected,
            allSelected,
            isSelected,
            toggle,
            unSelectAll,
            toggleAll,
            partiallySelected,
        } = useSelections(
            agentList.map(item => item.id),
            [],
        );

        const handleToggleAll = () => {
            toggleAll();
        };

        useEffect(() => {
            onSelect?.(selected);
        }, [selected, onSelect]);

        const [parent] = useAutoAnimate({
            duration: 150,
            easing: 'ease-out',
            disrespectUserMotionPreference: true,
        });
        return (
            <div className="flex flex-col gap-2 h-full">
                <div className="flex gap-2">
                    <div className="w-full">
                        <TagSearch
                            allowClear
                            onChange={handleTagChange}
                            className="w-full flex-1"
                        />
                    </div>
                    <Button disabled={!selected?.length} type="primary" onClick={handleBindTag}>
                        {selected?.length ? `为${selected?.length}个智能体` : ''}设置标签
                    </Button>
                </div>
                <div className="flex justify-between items-center px-2 mt-4">
                    <span>已选择 {selected.length} 个智能体</span>
                    <a onClick={handleToggleAll}>{allSelected ? '取消全选' : '全选'}</a>
                </div>
                <div ref={parent} className="flex-1 overflow-y-auto">
                    <div className={`grid grid-cols-${columns} gap-6`}>
                        {agentList.map(item => (
                            <div
                                key={item.key}
                                className={`rounded-lg border p-4 cursor-pointer transition-all ${
                                    isSelected(item.id)
                                        ? 'border-blue-500 bg-blue-100'
                                        : 'border-gray-200'
                                }`}
                                onClick={() => toggle(item.id)}
                            >
                                <div className="text-blue-600 font-medium">{item.name}</div>
                                <div className="text-gray-500 mt-2">{item.description}</div>
                                <TagSelect
                                    options={tagList}
                                    value={item.tags}
                                    className="w-full mt-2"
                                    variant="borderless"
                                    onChange={tags => handleSingleAgentTagChange(item.id, tags)}
                                />
                            </div>
                        ))}
                    </div>
                    {(agentList?.length) ? null : (
                        <div className="flex justify-center items-center flex-col w-full h-full">
                            <img src="/icons/agent_create.svg" className="size-16"></img>
                            <div>待生成智能体</div>
                        </div>
                    )}
                </div>
                {/* <div className='-mb-4 py-1'>
                已生成10个智能体，是否继续生成？<Button size='small'>继续生成</Button>
                </div> */}
            </div>
        );
    },
);
