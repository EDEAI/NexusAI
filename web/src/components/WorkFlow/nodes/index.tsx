/*
 * @LastEditors: biz
 */
import { useBoolean } from 'ahooks';
import { memo, useCallback, useRef, useState } from 'react';
import { NodeProps } from 'reactflow';
import useNodeIdUpdate from '../hooks/useNodeIdUpdate';
import useStore from '../store';
import { NodeCustom } from './nodeDisperse';
import RunPanel from './RunPanel';
import WrapNode from './WrapNode';
import WrapPanel from './WrapNode/panel';
const empty = (props: NodeProps) => <> {props.type}</>;

export const Node = memo((options: NodeProps) => {
    // console.log('options', options);
    const { type } = options;
    const CustomNode = NodeCustom[type]?.node || empty;
    const updatedOptions = {
        ...options,
        positionAbsoluteX: options.xPos,
        positionAbsoluteY: options.yPos,
    };
    const wrapRef = useRef(null);

    return (
        <>
            <WrapNode ref={wrapRef} {...updatedOptions}>
                <CustomNode {...updatedOptions} rootRef={wrapRef}></CustomNode>
            </WrapNode>
        </>
    );
});

export const Panel = memo(() => {
    const [CurrentNode, setCurrentNode] = useState(null);
    const [showState, { toggle }] = useBoolean(true);

    const setRunPanelNodeShow = useStore(state => state.setRunPanelNodeShow);

    const RenderPanel = useCallback(
        props => {
            console.log('RenderPanel', CurrentNode?.type, NodeCustom[CurrentNode?.type] || null);
            const Panel = NodeCustom[CurrentNode?.type]?.panel || null;
            return showState ? <Panel {...props}></Panel> : null;
        },
        [CurrentNode],
    );

    useNodeIdUpdate((id, selectNode) => {
        if (selectNode) {
            setCurrentNode(selectNode);
        } else {
            setCurrentNode(() => null);
        }
        setRunPanelNodeShow(false);
    });

    return (
        <>
            {CurrentNode && (
                <WrapPanel key={CurrentNode?.id} node={CurrentNode}>
                    <RenderPanel key={CurrentNode?.id} node={CurrentNode} />
                </WrapPanel>
            )}

            <RunPanel></RunPanel>
        </>
    );
});
export const ChildPanel = memo(() => {
    const CurrentNode = useStore(state => state.showChildNode);
    const RenderPanel = useCallback(
        props => {
            console.log('RenderPanel', CurrentNode?.type, NodeCustom[CurrentNode?.type] || null);
            const Panel = NodeCustom[CurrentNode?.type]?.panel || null;
            return <Panel {...props}></Panel>;
        },
        [CurrentNode],
    );
    return (
        <>
            {CurrentNode && (
                <WrapPanel key={CurrentNode?.id} node={CurrentNode}>
                    <RenderPanel key={CurrentNode?.id} node={CurrentNode} />
                </WrapPanel>
            )}

            <RunPanel></RunPanel>
        </>
    );
});
