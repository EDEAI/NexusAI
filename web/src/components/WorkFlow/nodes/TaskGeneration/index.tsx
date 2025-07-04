/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import { memo } from 'react';
import useStore from '../../store';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    const { data, id } = props;
   
    const modelData = useStore(state => state.modelData);
    const modelList = () => {
        return modelData?.list?.find(x => x.model_config_id == props.data?.model)?.model_name;
    };

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
                {data.model &&modelList()?.length&& (
                    <div className=" -mr-2 p-2 flex bg-slate-100  rounded-md items-center gap-2 text-xs">
                        {modelList()}
                    </div>
                )}
            </div>
        </div>
    );
});
