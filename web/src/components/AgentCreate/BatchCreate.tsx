/*
 * @LastEditors: biz
 */
import {
    ProForm,
    ProFormDigit,
    ProFormItem,
    ProFormTextArea,
    ProList,
} from '@ant-design/pro-components';
import { Form, Modal, Spin } from 'antd';
import { memo, useCallback, useState } from 'react';
import TagSearch, { TagSelect, useTags } from '../TagSearch';
import { BatchCreateFormData } from './types';

interface BatchCreateProps {
    open: boolean;
    onCancel: () => void;
    onOk: (data: BatchCreateFormData) => void;
    loading?: boolean;
}

const BatchCreate = memo(({ open, onCancel, onOk, loading }: BatchCreateProps) => {
    const [form] = Form.useForm();

    const [agentCreateResult, setAgentCreateResult] = useState(null);
    const { tagList } = useTags();
    const handleOk = async () => {
        const values = await form.validateFields();
        const prompts = values.prompts
            .split('\n')
            .map(p => p.trim())
            .filter(Boolean);

        onOk({
            count: values.count,
            prompts: prompts.join('\n'),
            additionalPrompt: values.additionalPrompt,
        });
    };
    const submitCreateAgent = val => {
        console.log(val);
        setAgentCreateResult({});
    };

    const RenderCreateInput = () => {
        const [submitDisabled, setSubmitDisabled] = useState(true);

        return (
            <div className="flex-1">
                <ProForm
                    onFinish={submitCreateAgent}
                    form={form}
                    onValuesChange={(_, allValues) => {
                        const { count, prompts } = allValues;
                        setSubmitDisabled(!count || !prompts?.trim());
                    }}
                    submitter={{
                        resetButtonProps: false,
                        submitButtonProps: {
                            loading,
                            className: 'w-full mt-3',
                            disabled: submitDisabled,
                        },
                        searchConfig: {
                            submitText: '生成',
                        },
                    }}
                >
                    <ProFormDigit
                        name="count"
                        label="生成数量"
                        min={1}
                        initialValue={10}
                        fieldProps={{
                            precision: 0,
                            step: 1,
                            controls: true,
                            parser: value => Math.floor(Number(value || 0)),
                            formatter: value => `${value}`.replace(/[^\d]/g, ''),
                        }}
                    />
                    <ProFormTextArea
                        name="prompts"
                        label="批量生成规则提示词"
                        placeholder="请输入补充性的提示词，将会添加到每个智能体的生成提示中"
                        fieldProps={{
                            rows: 18,
                        }}
                        formItemProps={{
                            className: '!mb-0',
                        }}
                    />
                </ProForm>
            </div>
        );
    };
    const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [agentList, setAgentList] = useState([
        {
            id: '1',
            key: '1',
            title: '20岁女性',
            subTitle: '能够处理客户咨询和投诉',
            content: '提供24/7的客服服务，快速响应客户问题',
            tags: [] as string[],
        },
        {
            id: '2',
            key: '2',
            title: '30岁女性',
            subTitle: '支持中英日法等多种语言翻译',
            content: '实时翻译多种语言，帮助您更好地与全球客户交流',
            tags: [] as string[],
        },
        {
            id: '3',
            key: '3',
            title: '40岁女性',
            subTitle: '能够生成新闻、博客等文章',
            content: '根据您的需求生成高质量的文章，提高您的内容输出效率',
            tags: [] as string[],
        },
        {
            id: '4',
            key: '4',
            title: '50岁女性',
            subTitle: '能够进行自然语言对话',
            content: '模拟人类对话，提供更加人性化的服务体验',
            tags: [] as string[],
        },
    ]);

    const handleTagChange = (tags: string[]) => {
        setSelectedTags(tags);
        setAgentList(prev =>
            prev.map(item => {
                if (selectedKeys.includes(item.id)) {
                    return { ...item, tags };
                }
                return item;
            }),
        );
    };

    const RenderAgentList = useCallback(() => {
        return (
            <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center px-2">
                    <span>已选择 {selectedKeys.length} 个智能体</span>
                    <a
                        onClick={() => {
                            const allKeys = agentList.map(item => item.id);
                            setSelectedKeys(
                                selectedKeys.length === agentList.length ? [] : allKeys,
                            );
                        }}
                    >
                        {selectedKeys.length === agentList.length ? '取消全选' : '全选'}
                    </a>
                </div>
                <ProList
                    showActions="hover"
                    grid={{ gutter: 26, column: 2 }}
                    rowKey="id"
                    tableAlertRender={false}
                    tableAlertOptionRender={false}
                    itemCardProps={{
                        className: '!mt-0 !p-0 h-full',
                        bodyStyle: {
                            padding: '0 20px 10px',
                        },
                    }}
                    metas={{
                        title: {},
                        subTitle: {
                            render: (_, record) => (
                                <div className="text-gray-700 text-xs">{record.content}</div>
                            ),
                        },
                        type: {},
                        avatar: {},
                        content: {
                            render: (_, record) => (
                                <div className='w-full'>
                                    <TagSelect
                                        options={tagList}
                                        value={record?.tags}
                                        className="w-full"
                                        variant='borderless'
                                    ></TagSelect>

                                    <div className="text-gray-700">{record.content}</div>
                                </div>
                            ),
                        },
                        actions: {
                            cardActionProps: 'extra',
                        },
                    }}
                    rowSelection={{
                        selectedRowKeys: selectedKeys,
                        onChange: keys => setSelectedKeys(keys),
                    }}
                    rowClassName="mb-0"
                    dataSource={agentList}
                />
            </div>
        );
    }, [selectedKeys, agentList]);

    const BeforeCreate = useCallback(
        () => (
            <div className="rounded-lg flex-1 border border-gray-200 p-4 bg-gray-50 flex justify-center items-center flex-col gap-2 text-[#1b64f3]">
                {loading ? (
                    <>
                        <Spin />
                        <div>生成中...</div>
                    </>
                ) : (
                    <>
                        <img src="/icons/agents_create.svg" className="size-16"></img>
                        <div>待生成智能体</div>
                    </>
                )}
            </div>
        ),
        [loading],
    );

    return (
        <Modal
            title="批量生成智能体"
            className="min-w-[1000px]"
            bodyProps={{
                className: '!h-[600px] overflow-y-auto p-4',
            }}
            open={open}
            onCancel={onCancel}
            onOk={handleOk}
            confirmLoading={loading}
        >
            {agentCreateResult ? (
                <div className="flex flex-col gap-4 h-full">
                    <ProFormItem tooltip="为选择的智能体设置标签" label="设置标签">
                        <TagSearch
                            disabled={!selectedKeys?.length}
                            value={selectedTags}
                            onChange={handleTagChange}
                            className="w-full"
                        />
                    </ProFormItem>
                    <RenderAgentList />
                </div>
            ) : (
                <div className="flex gap-4 h-full">
                    <BeforeCreate />
                    <RenderCreateInput />
                </div>
            )}
        </Modal>
    );
});

export default BatchCreate;
