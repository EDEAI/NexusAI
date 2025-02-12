/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import { memo } from 'react';
import useStore from '../../store';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    const modelData = useStore(state => state.modelData);
    const edges = useStore(state => state.edges);

    // Check if current node is connected to executor_list
    const isConnectedToExecutorList = edges.some(
        edge => edge.source === props.id && edge.targetHandle === 'executor_list',
    );

    const modelList = () => {
        const modeName = modelData?.list?.find(
            x => x.model_config_id == props.data?.model_config_id,
        )?.model_name;
        if (!modeName) return null;
        return (
            <div className="relative mb-2 box-border -mr-2 flex flex-col bg-slate-100 px-2 py-1 rounded-md gap-2 text-xs">
                {modeName}
            </div>
        );
    };

    return (
        <div>
            {!isConnectedToExecutorList && (
                <CustomHandle
                    id="start_target"
                    type="target"
                    params={props}
                    position={Position.Left}
                />
            )}

            {isConnectedToExecutorList && (
                <div className="mt-2 mb-4">
                    <CustomHandle
                        id="retrieval_task_datasets"
                        type="target"
                        params={props}
                        enableToolbar={false}
                        className="!top-[65px]"
                        position={Position.Left}
                        isValidConnection={() => true}
                    ></CustomHandle>
                    <div className="pl-2">知识库检索</div>
                </div>
            )}

            <CustomHandle
                id="start_source"
                type="source"
                connectionCount={isConnectedToExecutorList ? 1 : 999}
                params={props}
                position={Position.Right}
            />
            {modelList()}
        </div>
    );
});
