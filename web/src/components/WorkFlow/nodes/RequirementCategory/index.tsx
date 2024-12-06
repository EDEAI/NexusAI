/*
 * @LastEditors: biz
 */
import { useIntl } from '@umijs/max';
import { NodeProps, Position } from '@xyflow/react';
import { memo } from 'react';
import useStore from '../../store';
import CustomHandle from '../CustomHandle';

export default memo((props: NodeProps) => {
    const intl = useIntl();
    const { data, id } = props;
    console.log('data', data);

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

            <div className="flex flex-col gap-2 mb-2">
                {data.model && (
                    <div className=" -mr-2 p-2 flex bg-slate-100  rounded-md items-center gap-2 text-xs">
                        {modelList()}
                    </div>
                )}
                {data.wrap_list &&
                    data.wrap_list?.length > 0 &&
                    data.wrap_list.map((item, index) => (
                        <div className="">
                            <div
                                key={index}
                                className="relative box-border -mr-2 flex flex-col bg-slate-100  rounded-md items-center gap-2 text-xs"
                            >
                                <div key={index} className="p-2 flex items-center gap-2 w-full">
                                    <div className="text-xs font-medium text-slate-600 shrink-0">
                                        {intl.formatMessage({
                                            id: 'workflow.label.category',
                                            defaultMessage: '',
                                        })}{' '}
                                        {index + 1}
                                    </div>
                                    <div className="truncate">{item.que}</div>
                                </div>

                                <div className="absolute right-0 -mr-3 h-full flex items-center">
                                    <CustomHandle
                                        id={`${index}`}
                                        index={index}
                                        connectionCount={1}
                                        params={props}
                                        type="source"
                                        position={Position.Right}
                                    ></CustomHandle>
                                    {/* <CreateNodesToolbar
                                        {...props}
                                        sourceHandle={`${index}`}
                                        style={{ top: 'auto' }}
                                        position="right"
                                    ></CreateNodesToolbar> */}
                                </div>
                            </div>
                        </div>
                    ))}
            </div>
        </div>
    );
});
