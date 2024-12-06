/*
 * @LastEditors: biz
 */
import { NodeProps, Position } from '@xyflow/react';
import { Typography } from 'antd';
import { memo } from 'react';
import CustomHandle from '../CustomHandle';
const { Text } = Typography;
export default memo((props: NodeProps) => {
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
            {/* <CreateNodesToolbar {...props} position="left"></CreateNodesToolbar>
            <CreateNodesToolbar {...props} position="right"></CreateNodesToolbar> */}
            <div>
                <div className="relative mb-2 box-border -mr-2 flex  bg-slate-100 px-2 py-1 rounded-md  gap-2 text-xs">
                    <div className="flex items-center">{props?.data?.method}</div>
                    <div className="text-slate-600 truncate">
                        <Text
                            ellipsis={{
                                tooltip: props?.data?.url,
                            }}
                        >
                            {props?.data?.url}
                        </Text>
                    </div>
                </div>
            </div>
        </div>
    );
});
