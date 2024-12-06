/*
 * @LastEditors: biz
 */
import { useBoolean } from 'ahooks';
import { memo, useCallback, useRef, useState } from 'react';
import { NodeProps } from 'reactflow';
import useNodeIdUpdate from '../hooks/useNodeIdUpdate';
import useStore from '../store';
import { BlockEnum } from '../types';
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

const nodeResetNodeType = [BlockEnum.Skill];
export const Panel = memo(() => {
    // const nodes = useStore((state) => state.nodes);

    const [CurrentNode, setCurrentNode] = useState(null);
    const showChildNode = useStore(state => state.showChildNode);
    const [NodePanel, setNodePanel] = useState(null);
    const [selectId, setSelectId] = useState('');
    // const [selectType, setSelectType] = useState('');
    const [showState, { toggle }] = useBoolean(true);
    const runPanelShow = useStore(state => state.runPanelShow);
    // const previous = usePrevious(selectType, () => true);
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
        console.log(167, selectNode);

        if (selectNode) {
            setCurrentNode(selectNode);
            // setNodePanel(() => {
            //     return NodeCustom[selectNode.type].panel;
            // });
            // setSelectType(selectNode.type);
            // setSelectId(selectNode.id);
        } else {
            setCurrentNode(() => null);
            // setNodePanel(() => null);
        }
        setRunPanelNodeShow(false);
    });

    // useEffect(() => {
    //     // console.log('panelWrap nodes ', nodes);
    //     const selectNode = nodes.find((node) => node.data.selected);

    //     console.log('【:】', selectNode);
    //     if (selectNode) {
    //         setCurrentNode(selectNode);
    //         setNodePanel(() => {
    //             return NodeCustom[selectNode.type].panel;
    //         });
    //         setSelectType(selectNode.type);
    //         setSelectId(selectNode.id);
    //     } else {
    //         setCurrentNode(() => null);
    //         setNodePanel(() => null);
    //     }
    // }, [nodes]);
    // useNodeIdUpdate((nodeId,node)=>{
    //     if (node) {
    //         setCurrentNode(node);
    //         setNodePanel(() => {
    //             return NodeCustom[node.type].panel;
    //         });
    //         setSelectType(node.type);
    //         setSelectId(node.id);
    //     } else {
    //         setCurrentNode(() => null);
    //         setNodePanel(() => null);
    //     }
    // })
    // useUpdateEffect(() => {
    //     console.log('------id', previous, selectType);
    //     if (previous == selectType) {
    //         toggle();
    //         setTimeout(toggle, 500);
    //     }
    // }, [selectId]);
    useNodeIdUpdate((nodeId, node) => {
        // console.log('------id', previous, selectType,node);
        // if (previous == selectType&&!nodeResetNodeType.includes(selectType as BlockEnum)) {
        //     toggle();
        //     setTimeout(toggle, 500);
        // }
    });
    return (
        <>
            {CurrentNode && (
                <WrapPanel key={CurrentNode?.id} node={CurrentNode}>
                    {/* <CSSTransition in={showState} timeout={500} classNames="fade">
                        <NodePanel node={CurrentNode}></NodePanel>
                    </CSSTransition> */}
                    {/* {showState && <NodePanel key={CurrentNode?.id} node={CurrentNode}></NodePanel>} */}
                    <RenderPanel key={CurrentNode?.id} node={CurrentNode} />

                    {/* <RunPanelNode></RunPanelNode> */}
                </WrapPanel>
            )}

            <RunPanel></RunPanel>
        </>
    );
});
export const ChildPanel = memo(() => {
    // const [CurrentNode, setCurrentNode] = useState(null);
    const setRunPanelNodeShow = useStore(state => state.setRunPanelNodeShow);
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
