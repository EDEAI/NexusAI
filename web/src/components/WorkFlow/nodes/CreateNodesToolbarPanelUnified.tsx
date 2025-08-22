/*
 * @LastEditors: biz
 * Unified version of CreateNodesToolbarPanel - Using NodePanelContent's complete logic + node creation functionality
 */
import { ObjectVariable, Variable } from '@/py2js/variables.js';
import autoAnimate from '@formkit/auto-animate';
import { Node, NodeProps, NodeToolbar, Position, useNodeId, useReactFlow } from '@xyflow/react';
import { useHover, useMount, useWhyDidYouUpdate } from 'ahooks';
import { memo, useCallback, useEffect, useRef, useState } from 'react';
import { useIntl } from 'umi';
import useOutsideClick from '../hooks/useOutsideClick';
import useStore from '../store';
import { BlockEnum } from '../types';
import NodePanelContent from '../components/NodePanel/components/NodePanelContent';

interface CreateNodesToolbarProps {
    position: 'right' | 'left';
    className?: string;
    style?: object;
    sourceHandle?: string;
    targetHandle?: string;
    show: boolean;
    onSelect?: (e) => void;
    marginTop?: number;
    marginRight?: number;
    marginBottom?: number;
    marginLeft?: number;
}

export function getNodePosition(currentNode: Node, position: 'right' | 'left' = 'right') {
    let x = currentNode.position.x + currentNode.measured.width + 30;
    const y = currentNode.position.y;
    if (position == 'left') {
        x = currentNode.position.x - currentNode.measured.width - 30;
    }
    return { x, y };
}
const MemoNodePanel = memo(({ onItemClick }: { onItemClick: (item: any, type?: string) => void }) => {
    return (
        <NodePanelContent
            visibleTabs={['node', 'agent', 'tool', 'skill']}
            defaultActiveTab="1"
            showTeamSwitch={false}
            showTagSearch={false}
            isMinWidth={false}
            isCollapsed={false}
            isNodePanel={true}
            onItemClick={onItemClick}
        />
    );
});
export default memo((props: NodeProps & CreateNodesToolbarProps) => {
    const intl = useIntl();
    const tools = useRef(null);
    const nodeId = useNodeId();

    const storeCreateNode = useStore(state => state.createNode);
    const setPreventScrolling = useStore(state => state.setPreventScrolling);

    const { getNode, addEdges } = useReactFlow();
    const ref = useRef(null);
    
    // Tool panel display state
    const [toolsShow, setToolsShow] = useState(false);
    const isCloseing = useRef(false);
    const setCloseing = () => {
        isCloseing.current = true;
        setTimeout(() => {
            isCloseing.current = false;
        }, 300);
    };
   
    
    const isHovering = useHover(tools, {
        onChange: isHover => {
            setPreventScrolling(!isHover);
        },
    });

    useEffect(() => {
       if(isCloseing.current) return;
        props?.show && setToolsShow(true);
        
    }, [props?.show]);

    useEffect(() => {
        tools.current && autoAnimate(tools.current);
    }, [tools]);

    // Smart positioning: Only adjust position through transform (don't change left/right, don't change NodeToolbar's position)
    const panelRef = tools as React.MutableRefObject<HTMLDivElement | null>;
    const [verticalShift, setVerticalShift] = useState<number>(0);
    const [horizontalShift, setHorizontalShift] = useState<number>(0);
    const measuringRef = useRef(false);
    const marginTop = props.marginTop ?? 12;
    const marginRight = props.marginRight ?? 12;
    const marginBottom = props.marginBottom ?? 12;
    const marginLeft = props.marginLeft ?? 12;

    const measureAndAdjust = useCallback(() => {
        const el = panelRef.current;
        if (!el || measuringRef.current) return;
        measuringRef.current = true;
        const originalTransform = el.style.transform;
        // Temporarily clear transform, measure based on unshifted position to avoid recursive jitter
        el.style.transform = 'translate(0px, 0px)';
        const rect = el.getBoundingClientRect();
        const vw = window.innerWidth;
        const vh = window.innerHeight;

        // Horizontal direction: Clamp to viewport through translateX (don't change left/right side)
        let dx = 0;
        if (rect.left < marginLeft) dx += marginLeft - rect.left;
        if (rect.right > vw - marginRight) dx -= rect.right - (vw - marginRight);

        // Vertical direction: Clamp to viewport through translateY
        let dy = 0;
        if (rect.top < marginTop) dy += marginTop - rect.top;
        if (rect.bottom > vh - marginBottom) dy -= rect.bottom - (vh - marginBottom);

        // Threshold to avoid jitter caused by small errors
        const approximatelyEqual = (a: number, b: number, eps = 0.5) => Math.abs(a - b) < eps;

        // Immediately restore transform, then update to target transform through state (avoid visual flicker)
        el.style.transform = originalTransform;

        if (!approximatelyEqual(dx, horizontalShift)) setHorizontalShift(dx);
        if (!approximatelyEqual(dy, verticalShift)) setVerticalShift(dy);

        measuringRef.current = false;
    }, [panelRef, horizontalShift, verticalShift, marginTop, marginRight, marginBottom, marginLeft]);

    useEffect(() => {
        if (!toolsShow) return;
        const raf = requestAnimationFrame(measureAndAdjust);
        const onResize = () => requestAnimationFrame(measureAndAdjust);
        const onScroll = () => requestAnimationFrame(measureAndAdjust);
        window.addEventListener('resize', onResize);
        window.addEventListener('scroll', onScroll, true);
        let ro: ResizeObserver | null = null;
        if (panelRef.current) {
            ro = new ResizeObserver(() => requestAnimationFrame(measureAndAdjust));
            ro.observe(panelRef.current);
        }
        return () => {
            cancelAnimationFrame(raf);
            window.removeEventListener('resize', onResize);
            window.removeEventListener('scroll', onScroll, true);
            ro && ro.disconnect();
        };
    }, [toolsShow, measureAndAdjust]);

    // Close toolbar when clicking outside
    useOutsideClick(tools, () => {
        if (toolsShow) {
            setCloseing();
            setToolsShow(false);
        }
    });

    // Node creation logic extracted and improved from original CreateNodesToolbarPanel
    const createNodeFromItem = useCallback((item: any, type?: string) => {
        console.log('Creating node from item:', { item, type });
        
        let createType;
        const lang = intl.locale === 'en-US' ? 'en_US' : 'zh_Hans';
        
        // Determine creation type based on type parameter or item characteristics
        if (type === 'agent') {
            createType = BlockEnum.Agent;
        } else if (type === 'tool') {
            createType = BlockEnum.Tool;
        } else if (type === 'skill') {
            createType = BlockEnum.Skill;
        } else if (type === 'node') {
            // Basic node, use item's type
            createType = item.type || item.icon;
        } else {
            // Auto-detect type
            if (item.baseData) {
                // Has baseData, usually from API data
                if (item.baseData.authorization_status !== undefined || 
                    item.baseData.groupName || 
                    item.baseData.credentials_for_provider) {
                    createType = BlockEnum.Tool;
                } else if (item.baseData.name) {
                    // Determine if Agent or Skill based on context or other fields
                    createType = BlockEnum.Agent; // Default to Agent
                }
            } else if (item.identity) {
                // Has identity field, usually a tool
                createType = BlockEnum.Tool;
            } else if (item.type) {
                // Use item's own type
                createType = item.type;
            } else {
                // Default to basic node
                createType = item.icon || 'defaultNode';
            }
        }

        const currentNode = getNode(nodeId);
        if (!currentNode) {
            console.error('Cannot find current node:', nodeId);
            return;
        }

        let createData: any = {};

        if (createType === BlockEnum.Tool) {
            // Special handling for tool nodes
            createData = {
                title:
                    item?.identity?.label?.[lang] ||
                    item?.identity?.label?.['en_US'] ||
                    item?.data?.title ||
                    item?.title ||
                    intl.formatMessage({ id: 'workflow.tool', defaultMessage: 'Tool' }),
                desc: 
                    item?.description?.human?.[lang] || 
                    item?.description?.human?.['en_US'] || 
                    item?.description?.llm || 
                    item?.data?.desc ||
                    item?.desc ||
                    '',
                icon: item?.icon || item?.categoryIcon || item?.data?.icon,
                baseData: item.baseData || item,
            };

            // Handle tool output information
            const output = item.output || item?.baseData?.output;
            if (output) {
                if (Array.isArray(output) && output.length > 0) {
                    const toolVariables = new ObjectVariable('output', 'object');
                    output.forEach(outputItem => {
                        const variable = new Variable(outputItem.name, outputItem.type);
                        toolVariables.addProperty(outputItem.name, variable);
                    });
                    createData.outputInfo = toolVariables.toObject();
                } else {
                    createData.outputInfo = output;
                }
            }
        } else if (createType === BlockEnum.Agent || createType === BlockEnum.Skill) {
            // Agent or Skill node
            createData = {
                title: item.title || item.data?.title || item.name || item.baseData?.name,
                desc: item.description || item.data?.desc || item.desc || item.baseData?.description || '',
                baseData: item.baseData || item,
            };
            if (item.icon || item.data?.icon) {
                createData.icon = item.icon || item.data?.icon;
            }
        } else {
            // Basic node
            createData = item.data ? { ...item.data } : {
                title: item.title || item.data?.title,
                desc: item.desc || item.description || item.data?.desc,
                icon: item.icon || item.data?.icon,
            };
        }

        try {
            // Create new node
            const newNode = storeCreateNode(createType, {
                position: getNodePosition(currentNode, props.position),
                data: createData,
            });

            // Create connection edge
            const edgeId = `${currentNode.id}-${newNode.id}-${Date.now()}`;
            const edgeInfo: any = {
                id: edgeId,
                source: props.position === 'right' ? currentNode.id : newNode.id,
                target: props.position === 'right' ? newNode.id : currentNode.id,
            };

            // Handle connection points
            if (props.sourceHandle) {
                if (props.position === 'right') {
                    edgeInfo.sourceHandle = props.sourceHandle;
                } else {
                    edgeInfo.targetHandle = props.sourceHandle;
                }
            }
            if (props.targetHandle) {
                if (props.position === 'right') {
                    edgeInfo.targetHandle = props.targetHandle;
                } else {
                    edgeInfo.sourceHandle = props.targetHandle;
                }
            }

            addEdges([edgeInfo]);
            
            // Close toolbar and notify
            setCloseing();
            setToolsShow(false);
            props.onSelect && props.onSelect(item);
            setPreventScrolling(true);
            
            console.log('Node created successfully:', { newNode, edgeInfo });
        } catch (error) {
            console.error('Failed to create node:', error);
        }
    }, [getNode, nodeId, storeCreateNode, props, addEdges, setPreventScrolling, intl]);

    // Handle click events from NodePanelContent
    const handleItemClick = useCallback((item: any, type?: string) => {
        console.log('Creating node from item:', { item, type });
        createNodeFromItem(item, type);
    }, [createNodeFromItem]);

    const scrollRef = useRef(null);

    useEffect(() => {
        const handleWheel = event => {
            event.stopPropagation();
        };

        const container = scrollRef.current;
        if (!container?.addEventListener) return;
        container.addEventListener('wheel', handleWheel, { passive: false });

        return () => {
            container.removeEventListener('wheel', handleWheel);
        };
    }, []);
  
    return (
        <div
            ref={ref}
            style={{ top: 'calc(50% - 9px)' }}
        >
            <NodeToolbar
                offset={20}
                isVisible={toolsShow}
                position={props.position === 'left' ? Position.Left : Position.Right}
            >
                <div
                    ref={tools}
                    className="w-[280px] h-[600px] bg-white rounded-md border border-blue-100 shadow-lg"
                    style={{
                        maxHeight: `calc(100vh - ${marginTop + marginBottom}px)`,
                        overflowY: 'auto',
                        transform: `translate(${horizontalShift}px, ${verticalShift}px)`,
                        willChange: 'transform',
                        width: `min(280px, calc(100vw - ${marginLeft + marginRight}px))`,
                    }}
                >
                    {/* Directly use NodePanelContent component, pass in node creation callback */}
                    <MemoNodePanel onItemClick={handleItemClick} />
                </div>
            </NodeToolbar>
        </div>
    );
});
