/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import { memo } from 'react';
import useStore from '../../store';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    const edges = useStore(state => state.edges);

    // Check if current node is connected to executor_list
    const isConnectedToExecutorList = edges.some(
        edge => 
            edge.source === props.id && 
            edge.targetHandle === 'executor_list'
    );

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
            <CustomHandle
                id="start_source"
                type="source"
                params={props}
                position={Position.Right}
            />
        </div>
    );
});
