/*
 * @LastEditors: biz
 */
import { PlusOutlined } from '@ant-design/icons';
import { Handle, HandleProps, useHandleConnections, useUpdateNodeInternals } from '@xyflow/react';
import { useMount, useUpdateEffect } from 'ahooks';
import { memo, useCallback, useRef, useState } from 'react';
import { HANDLE_COLOR } from '../config';
import useOutsideClick from '../hooks/useOutsideClick';
import useStore from '../store';
import { BlockEnum } from '../types';
import CreateNodesToolbarPanel from './CreateNodesToolbarPanel';

interface CustomHandleProps {
    id: string;
    type: 'source' | 'target';
    className?: string;
    index?: number;
    connectionCount?: number;
    enableToolbar?: boolean;
    [key: string]: any;
}
const CustomHandle = memo((props: CustomHandleProps & HandleProps) => {
    const { className, index, connectionCount = 1000, params, enableToolbar = true, ...rest } = props;
    const addHandleList = useStore(state => state.addHandleList);
    const [selected, setSelected] = useState(false);
    const [toolsShow, setToolsShow] = useState(false);
    const [stopClose, setStopClose] = useState(false);
    const toolBarRef = useRef(null);
    const updateNodeInternals = useUpdateNodeInternals();
    const connections = useHandleConnections({
        id: props.id,
        type: props.type,
        nodeId: params?.id,
        onConnect: () => {
            console.log('onConnect', props.id, props.type);
        },
    });

    useMount(() => {
        addHandleList([
            {
                id: props.id,
                type: props.type,
                connections,
            },
        ]);
    });
    useUpdateEffect(() => {
        addHandleList([
            {
                id: props.id,
                type: props.type,
                connections,
            },
        ]);
    }, [props.id, props.type, connections]);
    useOutsideClick(toolBarRef, () => {
        setTimeout(() => {
            setToolsShow(false);
        }, 300);
    });
    useUpdateEffect(() => {
        setSelected(params?.data?.selected);
        setToolsShow(false);
    }, [params?.data?.selected]);

    const renderToolbarClass = useCallback(() => {
        const isSource = props.type === 'source';
        const baseClass = '!rounded-full flex items-center justify-center text-xs';

        if (connections.length >= connectionCount) {
            return '!w-0 !h-0';
        }

        if (selected || params?.nodeHover || params?.type === BlockEnum.Start) {
            return `!size-6 ${isSource ? '!-right-3' : '!-left-3'} ${baseClass}`;
        }
        return `!w-2 ${isSource ? '!-right-1' : '!-left-1'} ${
            connectionCount > 1 ? '!h-5' : '!h-2'
        }`;
    }, [selected, connections.length, props.type, params?.nodeHover]);
    const onSelect = item => {
        setTimeout(() => {
            setToolsShow(false);
            updateNodeInternals(params?.id);
        }, 100);
    };
    return (
        <Handle
            {...rest}
            className={`custom-handle  round ${renderToolbarClass()} duration-200 hover:scale-150 hover:-translate-y-1/2 ${className}`}
            isConnectable={connections.length < connectionCount}
            style={{
                background:
                    connections.length < connectionCount
                        ? HANDLE_COLOR.DEFAULT
                        : HANDLE_COLOR.DISABLE,
                height: 10,
                width: 3,
                borderRadius: '0.125rem',
            }}
            onClick={e => {
                e.stopPropagation();
                setToolsShow(true);
            }}
        >
            {(selected || props?.params?.nodeHover || params?.type == BlockEnum.Start) &&
                connections.length < connectionCount && (
                    <PlusOutlined className="pointer-events-none text-white" />
                )}
            {enableToolbar && (
                <div ref={toolBarRef}>
                    <CreateNodesToolbarPanel
                        {...params}
                        show={toolsShow}
                        onSelect={onSelect}
                        sourceHandle={props.id}
                        position={props.type == 'source' ? 'right' : 'left'}
                    />
                </div>
            )}
        </Handle>
    );
});

export default CustomHandle;
