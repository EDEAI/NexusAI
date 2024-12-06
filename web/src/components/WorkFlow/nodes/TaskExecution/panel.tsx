/*
 * @LastEditors: biz
 */
import Callword from '@/components/callword';
import useUserStore from '@/store/user';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import {
    ProForm,
    ProFormDependency,
    ProFormSelect,
    ProFormTextArea,
} from '@ant-design/pro-components';
import { offset, useDismiss, useFloating, useInteractions } from '@floating-ui/react';
import { useIntl } from '@umijs/max';
import { useMount } from 'ahooks';
import { Button, Typography } from 'antd';
import _ from 'lodash';
import { memo, useEffect, useRef, useState } from 'react';
import { v4 as uuid } from 'uuid';
import { SelectModelConfigId } from '../../components/Form/Select';
import {
    SwitchImportToKnowledgeBase,
    SwitchManualConfirmation,
} from '../../components/Form/Switch';
import useStore from '../../store';
import { AppNode, BlockEnum } from '../../types';
import { resetFormNodes } from '../../utils/resetFormNodes';
import CreateNodesToolbar from '../CreateNodesToolbar';
import { getBaseNode } from '../nodeDisperse';
type PromptItem = {
    serializedContent: string;
    value: object;
};

export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const modelData = useStore(state => state.modelData);
    const datasetData = useStore(state => state.datasetData);
    const teamDatasetData = useStore(state => state.teamDatasetData);
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    const getModelData = useStore(state => state.getModelData);
    const setShowChildNode = useStore(state => state.setShowChildNode);

    const [createNodeOpen, setCreateNodeOpen] = useState(false);
    const currentUpdateNodePanel = useUserStore(state => state.currentUpdateNodePanel);
    const setCurrentUpdateNodeValue = useUserStore(state => state.setCurrentUpdateNodeValue);
    const setSelect = useStore(state => state.setSelect);
    const [executorList, setExecutorList] = useState(node?.data?.executor_list || []);
    const { refs, floatingStyles, context } = useFloating({
        placement: 'left-start',
        middleware: [offset(25)],
        open: createNodeOpen,
        onOpenChange: setCreateNodeOpen,
    });
    const dismiss = useDismiss(context, {
        outsidePress: true,
        outsidePressEvent: 'click',
    });

    // const setTaskExecutionData=useDataStore(state=>state.setTaskExecutionData)
    const { getReferenceProps, getFloatingProps } = useInteractions([dismiss]);

    useMount(() => {
        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });

    // useEffect(() => {
    //     console.log(node?.data?.executor_list);
    // }, [node?.data]);

    // useUpdateEffect(() => {}, [node.id]);

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        console.log(addItem);

        updateNodeData(node.id, allValues);
    };
    const createChildNode = (type: BlockEnum) => {
        if (type == BlockEnum.LLM) {
            const childNode = getBaseNode(type)?.base;
            childNode.id = node.id;
            childNode.currentId = uuid();
            childNode.data['isChild'] = true;
            console.log(childNode);
            setShowChildNode(childNode);
            updateNodeData(node.id, {
                executor_list: [...(node?.data?.executor_list || []), childNode],
            });
        } else {
            setCreateNodeOpen(true);
        }
    };

    const onCreateNodesSelect = (value: string) => {
        console.log(value);
        const childNode = getBaseNode(BlockEnum.Agent)?.base;
        childNode.id = node.id;
        childNode.currentId = uuid();
        childNode.data['title'] = value['title'];
        childNode.data['desc'] = value['description'] || '';
        childNode.data['isChild'] = true;
        childNode.data['baseData'] = value;
        setShowChildNode(childNode);
        updateNodeData(node.id, {
            executor_list: [...(node?.data?.executor_list || []), childNode],
        });
        setCreateNodeOpen(false);
    };

    const delExecutor = i => {
        console.log(node?.data?.executor_list);
        const executor_list = _.cloneDeep(node?.data?.executor_list || []).filter((_, index) => {
            console.log(i, index);

            return index !== i;
        });
        // executor_list.splice(i, 1);
        node.data.executor_list = [];
        console.log(executor_list);

        updateNodeData(node.id, {
            executor_list: executor_list,
        });
        setSelect(node?.id, true);
    };
    const updateNodeDataHelper = (itemNode, data) => {
        if (itemNode?.data?.['isChild']) {
            const parentNode = node;
            const executor_list = _.cloneDeep(parentNode?.data?.executor_list);
            const editIndex = executor_list?.findIndex(x => x.currentId == itemNode?.currentId);

            if (!executor_list?.[editIndex]?.data) return;
            executor_list[editIndex].data = Object.assign(
                executor_list[editIndex].data || {},
                data,
            );
            // console.log('executor_list', executor_list);

            updateNodeData(parentNode?.id, {
                executor_list: executor_list,
            });
            // setSelect(node?.id, true);
        }
    };
    const RenderChildren = memo(e => {
        const itemFormRef = useRef(null);
        useMount(() => {
            resetFormNodes(itemFormRef, e);
        });

        useEffect(() => {
            if (
                currentUpdateNodePanel?.index == e.index &&
                currentUpdateNodePanel?.item?.id == e?.id
            ) {
                const datas = currentUpdateNodePanel?.data;

                itemFormRef.current.setFieldsValue(datas);
                // resetFormNodes(formRef, x);
            }
        }, [currentUpdateNodePanel]);
        const itemSetNodeChange = (addItem: { [key: string]: any }, allValues) => {
            updateNodeDataHelper(e, allValues);
            setCurrentUpdateNodeValue({
                data: allValues,
                index: e.index,
                item: e,
            });
        };
        return (
            <ProForm
                submitter={{
                    render: () => [],
                }}
                formRef={itemFormRef}
                onValuesChange={itemSetNodeChange}
            >
                <div
                    onClick={() => setShowChildNode(e)}
                    className="group p-2 min-h-[40px] relative border border-gray-300 hover:border-blue-400 rounded-md cursor-pointer flex flex-col justify-center"
                >
                    <div className="flex items-center">
                        <div className="bg-blue-400 p-1 mr-2 rounded">
                            <img src={`/icons/${e.type}.svg`} alt="" />
                        </div>
                        <Typography.Paragraph className="!mb-0" ellipsis>
                            {e?.data?.title}
                        </Typography.Paragraph>
                    </div>
                    <div className="flex flex-col gap-3">
                        <Typography.Paragraph
                            type="secondary"
                            className="!mb-0"
                            ellipsis={{
                                rows: 2,
                            }}
                        >
                            {e?.data?.desc}
                        </Typography.Paragraph>
                        <ProFormSelect
                            name="retrieval_task_datasets"
                            placeholder={intl.formatMessage({
                                id: 'workflow.label.selectKnowledgeBaseTask',
                                defaultMessage: '',
                            })}
                            formItemProps={{
                                className: '!mb-0',
                            }}
                            showSearch
                            mode="multiple"
                            allowClear={false}
                            options={teamDatasetData?.list || []}
                            fieldProps={{
                                onClick: event => event.stopPropagation(), //
                                onBlur: () => {
                                    setSelect(node?.id, true);
                                },
                            }}
                        ></ProFormSelect>
                    </div>

                    <Button
                        className="absolute right-1 top-1  opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                        icon={<DeleteOutlined />}
                        type="link"
                        onClick={event => {
                            event.stopPropagation();
                            delExecutor(e.index);
                        }}
                    ></Button>
                </div>
            </ProForm>
        );
    });

    //
    return (
        <>
            <div className="pt-4" ref={refs.setReference} {...getReferenceProps()}>
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    autoFocusFirstInput={false}
                    formRef={formRef}
                    omitNil={false}
                    layout="horizontal"
                    onValuesChange={setNodeChange}
                >
                    <ProFormSelect
                        name="variable"
                        label={intl.formatMessage({
                            id: 'workflow.label.selectVariable',
                            defaultMessage: '',
                        })}
                        showSearch
                        allowClear={false}
                        request={async () => {
                            return getVariables(node.id).filter(
                                x =>
                                    x.type == BlockEnum.TaskGeneration ||
                                    x.type == BlockEnum.TaskExecution,
                            );
                        }}
                    ></ProFormSelect>
                    <SelectModelConfigId form={formRef} name={`model`}></SelectModelConfigId>
                    {/* <ProFormSelect
                        name="model"
                        label={intl.formatMessage({
                            id: 'workflow.label.selectModel',
                            defaultMessage: '',
                        })}
                        showSearch
                        allowClear={false}
                        request={async () => {
                            const res = (await getModelData()) || [];
                            console.log(res);
                            return res;
                        }}
                    ></ProFormSelect> */}

                    <div className="user-form">
                        <SwitchManualConfirmation></SwitchManualConfirmation>
                        <SwitchImportToKnowledgeBase></SwitchImportToKnowledgeBase>
                    </div>
                    <ProFormDependency name={['import_to_knowledge_base']}>
                        {({ import_to_knowledge_base }) => {
                            return (
                                import_to_knowledge_base && (
                                    <ProFormSelect
                                        className="flex-1"
                                        label={intl.formatMessage({
                                            id: 'workflow.label.output',
                                            defaultMessage: 'output',
                                        })}
                                        showSearch
                                        name={`import_to_knowledge_base.output.output`}
                                        request={async () => datasetData?.list || []}
                                    ></ProFormSelect>
                                )
                            );
                        }}
                    </ProFormDependency>
                    <div className="flex">
                        <div className="flex-1 pt-2 border-stone-300 border rounded-md my-2">
                            <div className="px-2 flex justify-between cursor-default">
                                <div>
                                    <div className="text-sm text-gray-500 font-bold pb-1">
                                        <Callword
                                            name={intl.formatMessage({
                                                id: 'workflow.label.instruction',
                                                defaultMessage: '',
                                            })}
                                            title={intl.formatMessage({
                                                id: 'workflow.tooltip.instruction2',
                                                defaultMessage:
                                                    '，',
                                            })}
                                        ></Callword>
                                    </div>
                                </div>
                                <div></div>
                            </div>
                            <div className="overflow-y-auto">
                                <ProFormTextArea
                                    name="prompt"
                                    fieldProps={{
                                        variant: 'borderless',
                                        placeholder: intl.formatMessage({
                                            id: 'workflow.placeholder.enterInstruction',
                                            defaultMessage: '',
                                        }),
                                        autoSize: { minRows: 1, maxRows: 40 },
                                        count: {
                                            show: ({ value, count, maxLength }) => {
                                                return (
                                                    <div className="pr-2 text-blue-400">
                                                        {count}
                                                    </div>
                                                );
                                            },
                                        },
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                </ProForm>

                <div className="mt-4">
                    <Callword
                        name={intl.formatMessage({
                            id: 'workflow.label.executor',
                            defaultMessage: '',
                        })}
                        title={intl.formatMessage({
                            id: 'workflow.tooltip.executor',
                            defaultMessage:
                                'agent/LLM，',
                        })}
                    ></Callword>
                    <div className="flex flex-col gap-2 mt-2">
                        {node?.data?.executor_list?.map((e, i) => {
                            return (
                                <RenderChildren
                                    {...e}
                                    key={e?.currentId}
                                    index={i}
                                ></RenderChildren>
                            );
                        })}
                    </div>
                    <div className="flex justify-between gap-2 overflow-hidden py-1 mt-2">
                        <Button
                            onClick={() => createChildNode(BlockEnum.LLM)}
                            icon={<PlusOutlined />}
                            className="flex-1"
                        >
                            {intl.formatMessage({
                                id: 'workflow.button.llm',
                                defaultMessage: 'LLM',
                            })}
                        </Button>
                        <Button
                            onClick={() => createChildNode(BlockEnum.Agent)}
                            icon={<PlusOutlined />}
                            className="flex-1"
                        >
                            {intl.formatMessage({
                                id: 'workflow.button.agent',
                                defaultMessage: 'Agent',
                            })}
                        </Button>
                    </div>
                </div>
                {createNodeOpen && (
                    <div
                        className="cccc"
                        ref={refs.setFloating}
                        style={floatingStyles}
                        {...getFloatingProps()}
                    >
                        <CreateNodesToolbar
                            enabledIndexs={['2']}
                            defaultActiveKey={'2'}
                            onSelect={onCreateNodesSelect}
                        ></CreateNodesToolbar>
                    </div>
                )}
            </div>
        </>
    );
});
