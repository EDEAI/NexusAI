/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import { memo } from 'react';
import VariableInNode from '../../components/VariableInNode';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    return (
        <div>
            <CustomHandle
                id="start_target"
                params={props}
                type="target"
                position={Position.Left}
            ></CustomHandle>
            <CustomHandle
                id="start_source"
                params={props}
                type="source"
                position={Position.Right}
            ></CustomHandle>
          

            <VariableInNode value={props.data.variables?.value}></VariableInNode>
        </div>
    );
});
