/*
 * @LastEditors: biz
 */
import { FunctionOutlined } from '@ant-design/icons';
import { NodeProps, Position } from '@xyflow/react';
import { useMount } from 'ahooks';
import { memo, useState } from 'react';
import useStore from '../../store';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    const { data, id } = props;
    console.log('data', data);
    const [variables, setVariables] = useState([]);
    const getVariables = useStore(state => state.getOutputVariables);
    useMount(() => {
        setVariables(getVariables(id));
    });
    return (
        <div>
            <CustomHandle
                id="start_target"
                type="target"
                params={props}
                position={Position.Left}
            ></CustomHandle>

            {/* <CreateNodesToolbar {...props} position="left"></CreateNodesToolbar> */}

            <div className="flex flex-col gap-2 mb-2">
                {data.count &&
                    data.count?.length > 0 &&
                    data.count.map((item, index) => (
                        <div key={index} className="">
                            <div className="text-xs font-m pb-1">
                                {index == 0 ? 'IF' : 'ELSE-IF'}
                            </div>
                            <div
                                key={index}
                                className="relative box-border -mr-2 flex flex-col bg-slate-100  rounded-md items-center gap-2 text-xs"
                            >
                                {item.labels &&
                                    item.labels.map((x, i) => (
                                        <div
                                            key={i}
                                            className="p-2 flex items-center gap-2 w-full mr-2"
                                        >
                                            <FunctionOutlined />
                                            <div className="truncate max-w-32">
                                                {getVariables(id).find(
                                                    item => item.value == x.variable,
                                                )?.label || ''}
                                            </div>
                                            <div className="text-gray-400">{x?.count}</div>
                                            <div className="truncate">{x.target}</div>
                                        </div>
                                    ))}
                                <div className="absolute right-0 -mr-3 h-full flex items-center">
                                    <CustomHandle
                                        id={`${index}`}
                                        index={index}
                                        type="source"
                                        params={props}
                                        position={Position.Right}
                                        connectionCount={1}
                                    ></CustomHandle>
                                    {/* <CreateNodesToolbar
                                        {...props}
                                        sourceHandle={`${index}`}
                                        // style={{ top: 'auto' }}
                                        position="right"
                                    ></CreateNodesToolbar> */}
                                </div>
                            </div>
                        </div>
                    ))}

                <div className="mt-2">
                    <div className="text-xs font-m pb-1"></div>
                    <div className="relative box-border -mr-2 flex flex-col bg-slate-100  rounded-md items-center gap-2 text-xs">
                        <div className="p-2 flex items-center gap-2 w-full mr-2">
                            <FunctionOutlined />

                            <div className="text-gray-400">ELSE</div>
                            <div className="truncate"></div>
                        </div>

                        <div className="absolute right-0 -mr-3 h-full flex items-center">
                            <CustomHandle
                                id={`start_source_else`}
                                index={data.count?.length || 1}
                                type="source"
                                params={props}
                                position={Position.Right}
                                connectionCount={1}
                                // nodeInfo={props}
                            ></CustomHandle>
                            {/* <CreateNodesToolbar
                                {...props}
                                sourceHandle={`start_source_else`}
                                // style={{ top: 'auto' }}
                                position="right"
                            ></CreateNodesToolbar> */}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
});
