/*
 * @LastEditors: biz
 */
import useUserStore from '@/store/user';
import { ProForm, ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { NodeProps, Position } from '@xyflow/react';
import { useHover, useMemoizedFn, useMount, useUpdateEffect } from 'ahooks';
import _ from 'lodash';
import { memo, useRef, useState } from 'react';
import useStore from '../../store';
import { resetFormNodes } from '../../utils/resetFormNodes';
import CustomHandle from '../CustomHandle';
import { NODE_COLOR } from '../../config';

export default memo((props: NodeProps) => {
    const intl = useIntl();

    const { data, id } = props;
    // console.log('data', data);
    const setShowChildNode = useStore(state => state.setShowChildNode);
    const setPreventScrolling = useStore(state => state.setPreventScrolling);
    const teamDatasetData = useStore(state => state.teamDatasetData);
    const updateNodeData = useStore(state => state.updateNodeData);
    const currentUpdateNodeValue = useUserStore(state => state.currentUpdateNodeValue);
    const setCurrentUpdateNodePanel=useUserStore(state=>state.setCurrentUpdateNodePanel)
    // const modelData = useStore(state => state.modelData);
    // const modelList = () => {
    //     return modelData?.list?.find(x => x.model_config_id == props.data?.model)?.model_name;
    // };
    const updateNodeDataHelper = (node, data) => {
        if (node?.data?.['isChild']) {
            const parentNode = props;
            const executor_list = _.cloneDeep(parentNode?.data?.executor_list);
            const editIndex = executor_list?.findIndex(x => x.currentId == node?.currentId);
            if (!executor_list?.[editIndex]?.data) return;
            executor_list[editIndex].data = Object.assign(
                executor_list[editIndex].data || {},
                data,
            );

            updateNodeData(parentNode?.id, {
                executor_list: executor_list,
            });
        }
    };

    const RenderChildrenItem = useMemoizedFn(({ x, index }) => {
        const [selectOpen, setSelectOpen] = useState(false);
        const ref = useRef(null);
        const formRef = useRef(null);
        const isHovering = useHover(ref, {
            onChange: isHover => {
                setPreventScrolling(!isHover);
            },
        });
        const setNodeChange = (addItem: { [key: string]: any }, all, index) => {
            updateNodeDataHelper(x, all);
            setCurrentUpdateNodePanel({
                data:all,
                index,
                item:x
            })
        };
        useMount(() => {
            resetFormNodes(formRef, x);
        });
        useUpdateEffect(() => {
            if (currentUpdateNodeValue?.index == index&&currentUpdateNodeValue?.item?.id==x?.id) {
                const currentValues = formRef.current.getFieldsValue();
                const datas=currentUpdateNodeValue?.data
                if(currentValues!==datas){
                    formRef.current.setFieldsValue(datas);
                }

                // resetFormNodes(formRef, x);
            }
        }, [currentUpdateNodeValue]);
        return (
            <ProForm
                submitter={{
                    render: () => [],
                }}
                formRef={formRef}
                onValuesChange={(item, all) => setNodeChange(item, all, index)}
            >
                <div
                    onClick={() => setShowChildNode(x)}
                    className=" -mr-2 p-2 flex flex-col bg-slate-100 transition hover:bg-slate-200 cursor-pointer rounded-md gap-2 text-xs"
                >
                    <div className="flex gap-2 items-center">
                        <div style={{ backgroundColor: NODE_COLOR[x.type] }} className="bg-blue-400 p-1 rounded">
                            <img src={`/icons/${x.type}.svg`} className="size-4" alt="" />
                        </div>
                        {x?.data?.title}
                    </div>
                    <div className="right-0 top-0">
                        <ProFormSelect
                            name="retrieval_task_datasets"
                            placeholder={intl.formatMessage({
                                id: 'workflow.label.selectKnowledgeBaseTask',
                                defaultMessage: '',
                            })}
                            formItemProps={{
                                className: '!mb-0',
                            }}
                            mode="multiple"
                            allowClear={false}
                            options={teamDatasetData?.list || []}
                            fieldProps={{
                                open: selectOpen,
                                getPopupContainer: () => ref.current,
                                maxTagCount: 'responsive',
                                maxTagTextLength: 7,
                                // maxTagPlaceholder: (omittedValues) => `+ ${omittedValues.length}`,
                                onClick: event => event.stopPropagation(), //
                                onFocus: () => {
                                    //
                                    setSelectOpen(true);
                                },
                                onBlur: () => {
                                    //
                                    setSelectOpen(false);
                                },
                            }}
                        ></ProFormSelect>
                        <div ref={ref}></div>
                    </div>
                </div>
            </ProForm>
        );
    });
    return (
        <div>
            <CustomHandle
                id="start_target"
                type="target"
                params={props}
                connectionCount={1}
                position={Position.Left}
            ></CustomHandle>

            {/* <CreateNodesToolbar {...props} position="left"></CreateNodesToolbar> */}
            <CustomHandle
                id={`task_generation`}
                params={props}
                type="source"
                position={Position.Right}
            ></CustomHandle>

            <div className="flex flex-col gap-2 mb-2">
                {data?.executor_list &&
                    Array.isArray(data?.executor_list) &&
                    data?.executor_list.map((x, i) => {
                        return <RenderChildrenItem key={x?.currentId} x={x} index={i} />;
                    })}
            </div>
        </div>
    );
});
