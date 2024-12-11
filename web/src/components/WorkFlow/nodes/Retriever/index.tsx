/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import { memo } from 'react';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    return (
        <div>
            <CustomHandle
                id="start_target"
                type="target"
                params={props}
                connectionCount={1}
                position={Position.Left}
            ></CustomHandle>
            <CustomHandle
                id="start_source"
                type="source"
                params={props}
                position={Position.Right}
            ></CustomHandle>
          
        </div>
    );
});
