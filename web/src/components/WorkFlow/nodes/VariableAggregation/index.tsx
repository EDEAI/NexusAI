/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import _ from 'lodash';
import { memo, useCallback } from 'react';
import useStore from '../../store';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    const getVariables = useStore(state => state.getOutputVariables);

    const VarList = useCallback(() => {
        if (!props?.data?.variables || !_.isArray(props?.data?.variables)) return null;
        return props?.data?.variables?.map(x => {
            return (
                <div className="relative mb-2 box-border -mr-2 flex flex-col bg-slate-100 px-2 py-1 rounded-md  gap-2 text-xs">
                    <>{getVariables(props.id, x.variable)?.label}</>
                </div>
            );
        });
    }, [props?.data?.variables]);

    return (
        <div>
            <CustomHandle
                id="start_target"
                type="target"
                params={props}
                position={Position.Left}
            ></CustomHandle>
            <CustomHandle
                id="start_source"
                type="source"
                params={props}
                connectionCount={1}
                position={Position.Right}
            ></CustomHandle>
            {/* <CreateNodesToolbar {...props} position="left"></CreateNodesToolbar> */}
            {/* <CreateNodesToolbar {...props} position="right"></CreateNodesToolbar> */}

            <div>
                <VarList></VarList>
            </div>
        </div>
    );
});
