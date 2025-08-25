/*
 * @LastEditors: biz
 */
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
                connectionCount={1}
                params={props}
                id="start"
                type="source"
                position={Position.Right}
            ></CustomHandle>
            
            {/* <CreateNodesToolbar position="right" {...props}></CreateNodesToolbar> */}
            <VariableInNode value={props.data.variables?.value}></VariableInNode>
        </div>
    );
});
