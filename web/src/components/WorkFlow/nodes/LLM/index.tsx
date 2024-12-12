/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import { memo } from 'react';
import useStore from '../../store';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
 
    const modelData = useStore(state => state.modelData);
    const modelList = () => {
        const modeName = modelData?.list?.find(
            x => x.model_config_id == props.data?.model_config_id,
        )?.model_name;
        if (!modeName) return null;
        return (
            <div className="relative mb-2 box-border -mr-2 flex flex-col bg-slate-100 px-2 py-1 rounded-md  gap-2 text-xs">
                {modeName}
            </div>
        );
    };
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
                position={Position.Right}
            ></CustomHandle>
      
            {modelList()}
        </div>
    );
});
