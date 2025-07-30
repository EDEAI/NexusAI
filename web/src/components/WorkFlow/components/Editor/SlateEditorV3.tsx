import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import { isEqual } from 'lodash';
import React, {
    Fragment,
    ReactNode,
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import ReactDOM from 'react-dom';
import { createEditor, Descendant, Editor, Node, Point, Range, Transforms, Location } from 'slate';
import { withHistory } from 'slate-history';
import { Editable, ReactEditor, Slate, useFocused, useSelected, withReact } from 'slate-react';
import { CURRENT_NODE_ID } from '../../config';
import useStore from '../../store';
import './SlateEditorV3.css';

// ===== Type Definitions =====
export interface Variable {
    name: string;
    label: string;
    value: string;
    title?: string;
    id?: string;
    createVar?: {
        name: string;
    };
}

export interface MentionOption {
    name: string;
    label: string;
    value: string;
    title?: string;
    id?: string;
}

export interface MentionElement {
    type: 'mention';
    id: string;
    character: string;
    base: Variable;
    children: Array<{ text: string; bold?: boolean; italic?: boolean }>;
}

export interface ParagraphElement {
    type: 'paragraph';
    children: Array<{ text: string }>;
}

export type CustomElement = MentionElement | ParagraphElement;
export type CustomText = { text: string; bold?: boolean; italic?: boolean };

declare module 'slate' {
    interface CustomTypes {
        Element: CustomElement;
        Text: CustomText;
    }
}

export interface MentionEditorProps {
    value?: Descendant[];
    onChange?: (value: Descendant[]) => void;
    id?: string;
    placeholder?: string;
    options?: MentionOption[];
    variables?: Variable[];
}

// ===== Utility Functions =====
const IS_MAC = typeof navigator !== 'undefined' && /Mac OS X/.test(navigator.userAgent);

const Portal = ({ children }: { children?: ReactNode }) => {
    return typeof document === 'object' ? ReactDOM.createPortal(children, document.body) : null;
};

const initialValue: Descendant[] = [
    {
        type: 'paragraph',
        children: [{ text: '' }],
    },
];

// ===== Custom Hooks =====

// Smart Position Hook for popup positioning
const useSmartPosition = (
    targetRange: Range | undefined,
    editor: Editor,
    popupRef: React.RefObject<HTMLDivElement>,
    isVisible: boolean,
    options: {
        offset?: number;
        margin?: number;
    } = {}
) => {
    const { offset = 4, margin = 8 } = options;
    const [position, setPosition] = useState({ top: -9999, left: -9999 });
    
    const calculatePosition = useCallback(() => {
        if (!targetRange || !isVisible || !popupRef.current) {
            setPosition({ top: -9999, left: -9999 });
            return;
        }

        try {
            const domRange = ReactEditor.toDOMRange(editor, targetRange);
            const rect = domRange.getBoundingClientRect();
            const popup = popupRef.current;
            const popupRect = popup.getBoundingClientRect();
            
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight,
                scrollX: window.pageXOffset,
                scrollY: window.pageYOffset,
            };

            // Default position: below the cursor
            let top = rect.bottom + viewport.scrollY + offset;
            let left = rect.left + viewport.scrollX;

            // Check if popup would overflow bottom
            if (top + popupRect.height > viewport.height + viewport.scrollY) {
                // Try to position above the cursor
                const aboveTop = rect.top + viewport.scrollY - popupRect.height - offset;
                if (aboveTop >= viewport.scrollY) {
                    top = aboveTop;
                } else {
                    // If can't fit above, keep below but adjust to fit
                    top = viewport.height + viewport.scrollY - popupRect.height - margin;
                }
            }

            // Check if popup would overflow right
            if (left + popupRect.width > viewport.width + viewport.scrollX) {
                left = viewport.width + viewport.scrollX - popupRect.width - margin;
            }

            // Check if popup would overflow left
            if (left < viewport.scrollX) {
                left = viewport.scrollX + margin;
            }

            // Ensure popup doesn't go above viewport
            if (top < viewport.scrollY) {
                top = viewport.scrollY + margin;
            }

            setPosition({ top, left });
        } catch (error) {
            console.warn('Failed to calculate smart position:', error);
            setPosition({ top: -9999, left: -9999 });
        }
    }, [targetRange, editor, isVisible, popupRef, offset, margin]);

    // Debounced position calculation
    const debouncedCalculatePosition = useMemo(() => {
        let timeoutId: NodeJS.Timeout;
        return () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(calculatePosition, 16); // ~60fps
        };
    }, [calculatePosition]);

    // Initial position calculation
    useEffect(() => {
        calculatePosition();
    }, [calculatePosition]);

    // Listen for window resize and scroll events
    useEffect(() => {
        if (!isVisible) return;

        const handleResize = debouncedCalculatePosition;
        const handleScroll = debouncedCalculatePosition;

        window.addEventListener('resize', handleResize);
        window.addEventListener('scroll', handleScroll, true);

        return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('scroll', handleScroll, true);
        };
    }, [isVisible, debouncedCalculatePosition]);

    return position;
};

// Variables Management Hook
const useVariablesManagement = (
    options: MentionOption[] = [],
    variables: Variable[] = [],
    selectedNodeId?: string
): Variable[] => {
    const getOutputVariables = useStore(state => state.getOutputVariables);

    return useMemo(() => {
        const result: Variable[] = [];

        // Process options
        if (options?.length) {
            result.push(
                ...options.map(x => ({
                    ...x,
                    name: x.label,
                    id: x.value,
                }))
            );
            
        }

        // Process output variables from selectedNode
        if (selectedNodeId) {
            const nodeVariables = getOutputVariables(selectedNodeId)?.map(x => ({
                ...x,
                name: x.label,
                id: x.value,
            })) || [];
            
            result.push(...nodeVariables);
        }

        // Process variables
        if (variables?.length) {
            const varList = variables.map(x => ({
                ...x,
                id: `<<${CURRENT_NODE_ID}.inputs.${x.name}>>`,
                createVar: {
                    name: x.name,
                },
            }));
            
            result.push(...varList);
        }
        // INSERT_YOUR_CODE
        // Remove duplicates by id
        const uniqueResult: Variable[] = [];
        const seenIds = new Set<string>();
        for (const item of result) {
            if (!seenIds.has(item.id)) {
                uniqueResult.push(item);
                seenIds.add(item.id);
            }
        }
        return uniqueResult;
    
    }, [options, variables, selectedNodeId, getOutputVariables]);
};

// Mention Feature Hook
const useMentionFeature = (
    editor: Editor,
    availableVariables: Variable[]
) => {
    const ref = useRef<HTMLDivElement | null>(null);
    const [target, setTarget] = useState<Range | undefined>();
    const [index, setIndex] = useState(0);
    const [search, setSearch] = useState('');
    const itemRefs = useRef<(HTMLDivElement | null)[]>([]);

    // Reset item refs when variables change
    useEffect(() => {
        itemRefs.current = [];
    }, [availableVariables]);

    // Reset index and scroll when target changes
    useEffect(() => {
        if (target) {
            setIndex(0);
            // Scroll to top when popup opens
            const container = ref.current?.querySelector('.max-h-64.overflow-y-auto') as HTMLElement;
            if (container) {
                container.scrollTop = 0;
            }
        }
    }, [target]);

    // Show mention options
    const showMentionOptions = useCallback(() => {
        const { selection } = editor;

        if (selection && Range.isCollapsed(selection)) {
            const [start] = Range.edges(selection);
            const before = Editor.before(editor, start);
            const beforeRange = before && Editor.range(editor, before, start);
            setTarget(beforeRange);
            setSearch('');
            setIndex(0);
            return;
        }
        setTarget(null);
    }, [editor]);

    // Insert mention
    const insertMention = useCallback((variable: Variable) => {
        if (!target) return;

        const mention: any = {
            type: 'mention',
            id: variable.id || '',
            character: variable.name,
            base: variable,
            children: [{ text: '', bold: true }],
        };

        Transforms.select(editor, target);
        Transforms.insertNodes(editor, mention);
        Transforms.move(editor);
        setTarget(null);
    }, [editor, target]);

    // Scroll to selected item
    const scrollToIndex = useCallback((targetIndex: number) => {
        // Use requestAnimationFrame to ensure DOM is updated
        requestAnimationFrame(() => {
            const container = ref.current?.querySelector('.max-h-64.overflow-y-auto') as HTMLElement;
            const targetItem = itemRefs.current[targetIndex];
            
            if (!container || !targetItem) return;

            const containerTop = container.scrollTop;
            const containerBottom = containerTop + container.clientHeight;
            
            const itemTop = targetItem.offsetTop;
            const itemBottom = itemTop + targetItem.offsetHeight;
            
            // Check if item is above visible area
            if (itemTop < containerTop) {
                container.scrollTo({
                    top: Math.max(0, itemTop - 8), // Add some padding, ensure not negative
                    behavior: 'smooth'
                });
            }
            // Check if item is below visible area
            else if (itemBottom > containerBottom) {
                container.scrollTo({
                    top: itemBottom - container.clientHeight + 8, // Add some padding
                    behavior: 'smooth'
                });
            }
        });
    }, []);

    // Handle keyboard events
    const handleMentionKeyDown = useCallback(
        (event: React.KeyboardEvent) => {
            if (!target || !availableVariables.length) return false;

            switch (event.key) {
                case 'ArrowDown':
                    event.preventDefault();
                    const nextIndex = index >= availableVariables.length - 1 ? 0 : index + 1;
                    setIndex(nextIndex);
                    // Scroll to the newly selected item
                    scrollToIndex(nextIndex);
                    return true;
                case 'ArrowUp':
                    event.preventDefault();
                    const prevIndex = index <= 0 ? availableVariables.length - 1 : index - 1;
                    setIndex(prevIndex);
                    // Scroll to the newly selected item
                    scrollToIndex(prevIndex);
                    return true;
                case 'Tab':
                case 'Enter':
                    event.preventDefault();
                    insertMention(availableVariables[index]);
                    return true;
                case 'Escape':
                    event.preventDefault();
                    setTarget(null);
                    return true;
                default:
                    return false;
            }
        },
        [target, availableVariables, index, insertMention, scrollToIndex]
    );

    // Smart position calculation
    const smartPosition = useSmartPosition(
        target,
        editor,
        ref,
        !!(target && availableVariables.length > 0),
        {
            offset: 6, // Distance from cursor
            margin: 12, // Margin from viewport edges
        }
    );

    // Update mention popup position with smart positioning
    useEffect(() => {
        if (ref.current) {
            const el = ref.current;
            if (smartPosition.top !== -9999) {
                el.style.top = `${smartPosition.top}px`;
                el.style.left = `${smartPosition.left}px`;
                el.classList.add('positioned');
            } else {
                el.style.top = '-9999px';
                el.style.left = '-9999px';
                el.classList.remove('positioned');
            }
        }
    }, [smartPosition]);

    return {
        ref,
        target,
        index,
        search,
        setIndex,
        showMentionOptions,
        insertMention,
        handleMentionKeyDown,
        itemRefs,
        closeMention: () => setTarget(null), // 新增
    };
};

// Editor Value Management Hook
const useEditorValueManagement = (
    editor: Editor,
    value: Descendant[] | undefined,
    onChange: ((value: Descendant[]) => void) | undefined,
    id?: string
) => {
    const [oldPropsValue, setOldPropsValue] = useState<Descendant[] | null>(null);

    // Safe node reset method
    const resetNodes = useCallback(
        (nodes: Descendant[], preserveSelection = true) => {
            const currentSelection = preserveSelection ? editor.selection : null;

            // Clear existing content
            const children = [...editor.children];
            children.forEach(() => 
                editor.apply({ type: 'remove_node', path: [0], node: children[0] })
            );

            // Insert new content
            const validNodes = Array.isArray(nodes) && nodes.length > 0 
                ? nodes 
                : initialValue;

            validNodes.forEach((node, i) =>
                editor.apply({ type: 'insert_node', path: [i], node })
            );

            // Restore cursor position
            let targetPoint: Point | null = null;

            if (preserveSelection && currentSelection && Range.isRange(currentSelection)) {
                try {
                    const { anchor } = currentSelection;
                    if (Editor.hasPath(editor, anchor.path)) {
                        const [node] = Editor.node(editor, anchor.path);
                        if (node && 'text' in node) {
                            const textLength = (node as any).text?.length || 0;
                            targetPoint = {
                                path: anchor.path,
                                offset: Math.min(anchor.offset, textLength)
                            };
                        }
                    }
                } catch (error) {
                    console.warn('Failed to restore cursor position:', error);
                }
            }

            if (!targetPoint) {
                targetPoint = Editor.start(editor, []);
            }

            if (targetPoint) {
                Transforms.select(editor, targetPoint);
            }
        },
        [editor]
    );

    // Update editor value
    const updateValue = useCallback(
        (newValue: Descendant[]) => {
            setOldPropsValue(newValue);
            resetNodes(newValue);
        },
        [resetNodes]
    );

    // Handle value changes
    useUpdateEffect(() => {
        if (isEqual(oldPropsValue, value)) return;

        const validValue = value && Array.isArray(value) && value.length > 0 
            ? value 
            : initialValue;

        updateValue(validValue);
    }, [value, id, updateValue]);

    // Debounced onChange handler
    const debouncedOnChange = useMemo(
        () => {
            let timeoutId: NodeJS.Timeout;
            return (newValue: Descendant[]) => {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    onChange?.(newValue);
                }, 200);
            };
        },
        [onChange]
    );

    return {
        updateValue,
        debouncedOnChange,
    };
};

// ===== Main Component =====
const SlateEditorV3: React.FC<MentionEditorProps> = ({
    value,
    onChange,
    id,
    placeholder,
    options = [],
    variables = [],
}) => {
    const intl = useIntl();
    const selectedNode = useStore(state => state.selectedNode);
    
    // Create editor instance
    const editor = useMemo(
        () => withMentions(withReact(withHistory(createEditor()))),
        []
    );

    // Manage variables
    const availableVariables = useVariablesManagement(
        options,
        variables,
        selectedNode?.id
    );
    
    // Mention functionality
    const {
        ref: mentionRef,
        target,
        index,
        showMentionOptions,
        insertMention,
        handleMentionKeyDown,
        itemRefs,
        closeMention, // 新增
    } = useMentionFeature(editor, availableVariables);

    // Editor value management
    const { updateValue, debouncedOnChange } = useEditorValueManagement(
        editor,
        value,
        onChange,
        id
    );

    // Initialization
    useMount(() => {
        if (value && Array.isArray(value) && value.length > 0) {
            updateValue(value);
        }
    });

    // Keyboard event handling
    const handleKeyDown = useCallback(
        (event: React.KeyboardEvent) => {
            // First handle mention-related keyboard events
            if (handleMentionKeyDown(event)) {
                return;
            }

            // Handle @ symbol
            if (event.key === '@' || event.key === '@') {
                setTimeout(() => showMentionOptions(), 10);
                return;
            }

            // Hide mention popup in other cases
            if (target) {
                setTimeout(() => showMentionOptions(), 10);
            }
        },
        [handleMentionKeyDown, showMentionOptions, target]
    );

    // Render functions
    const renderElement = useCallback((props: any) => <Element {...props} />, []);
    const renderLeaf = useCallback((props: any) => <Leaf {...props} />, []);

    return (
        <Slate
            editor={editor}
            initialValue={initialValue}
            onChange={debouncedOnChange}
        >
            <Editable
                renderElement={renderElement}
                renderLeaf={renderLeaf}
                onKeyDown={handleKeyDown}
                className="!outline-none"
                placeholder={
                    placeholder ??
                    intl.formatMessage({
                        id: 'workflow.placeholder.enterContent',
                        defaultMessage: 'Enter content, use @ to mention variables',
                    })
                }
                onBlur={() => {
                    closeMention();
                }}
            />
            {target && availableVariables.length > 0 && (
                <Portal>
                    <div
                        ref={mentionRef}
                        style={{
                            position: 'absolute',
                            zIndex: 1000,
                        }}
                        className="mention-popup"
                        data-cy="mentions-portal"
                        onMouseDown={e => e.preventDefault()} 
                    >
                        <div className="bg-white rounded-lg shadow-lg border border-gray-200 py-2 min-w-48 max-w-80 max-h-64 overflow-y-auto">
                            <div className="px-3 py-1 text-xs text-gray-500 font-medium border-b border-gray-100 mb-1">
                                {intl.formatMessage({
                                    id: 'workflow.editor.selectVariable',
                                    defaultMessage: 'Select Variable',
                                })}
                            </div>
                            {availableVariables.map((variable, i) => (
                                <div
                                    key={`${variable.name}-${i}`}
                                    ref={(el) => {
                                        itemRefs.current[i] = el;
                                    }}
                                    onClick={() => insertMention(variable)}
                                    className={`
                                        mention-item flex items-center justify-between px-3 py-2 mx-1 rounded-md cursor-pointer
                                        transition-all duration-150 ease-in-out
                                        ${i === index 
                                            ? 'bg-blue-50 border border-blue-200 shadow-sm mention-selected' 
                                            : 'hover:bg-gray-50 border border-transparent'
                                        }
                                    `}
                                    style={{
                                        transform: i === index ? 'translateX(2px)' : 'translateX(0)',
                                    }}
                                >
                                    <div className="flex items-center space-x-2 flex-1 min-w-0">
                                        {/* Variable type icon */}
                                        <div className={`
                                            variable-icon w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium
                                            ${variable.createVar?.name 
                                                ? 'bg-green-100 text-green-600' 
                                                : 'bg-blue-100 text-blue-600'
                                            }
                                        `}>
                                            {variable.createVar?.name ? 'I' : 'V'}
                                        </div>
                                        
                                        {/* Variable information */}
                                        <div className="flex-1 min-w-0">
                                            <div className="text-sm font-medium text-gray-900 truncate">
                                                {variable.title || variable.name}
                                            </div>
                                            {variable.createVar?.name && (
                                                <div className="text-xs text-gray-500 truncate">
                                                    {intl.formatMessage({
                                                        id: 'workflow.editor.inputVariable',
                                                        defaultMessage: 'Input',
                                                    })}: {variable.createVar.name}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    
                                    {/* Selection indicator */}
                                    {i === index && (
                                        <div className="w-2 h-2 bg-blue-500 rounded-full ml-2 flex-shrink-0"></div>
                                    )}
                                </div>
                            ))}
                            
                            {/* Hint information */}
                            <div className="px-3 py-2 mt-2 border-t border-gray-100">
                                <div className="text-xs text-gray-400 flex items-center justify-between">
                                    <span>{intl.formatMessage({
                                        id: 'workflow.editor.navigation.up',
                                        defaultMessage: '↑↓ Navigate',
                                    })}</span>
                                    <span>{intl.formatMessage({
                                        id: 'workflow.editor.navigation.select',
                                        defaultMessage: 'Enter Select',
                                    })}</span>
                                    <span>{intl.formatMessage({
                                        id: 'workflow.editor.navigation.cancel',
                                        defaultMessage: 'Esc Cancel',
                                    })}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </Portal>
            )}
        </Slate>
    );
};

// ===== Render Components =====
const withMentions = (editor: Editor) => {
    const { isInline, isVoid, markableVoid } = editor;

    editor.isInline = (element: any) => {
        return element.type === 'mention' ? true : isInline(element);
    };

    editor.isVoid = (element: any) => {
        return element.type === 'mention' ? true : isVoid(element);
    };

    editor.markableVoid = (element: any) => {
        return element.type === 'mention' || markableVoid(element);
    };

    return editor;
};

const Leaf = ({ attributes, children }: any) => {
    return <span {...attributes}>{children}</span>;
};

const Element = (props: any) => {
    const { attributes, children, element } = props;
    switch (element.type) {
        case 'mention':
            return <Mention {...props} />;
        default:
            return <p {...attributes}>{children}</p>;
    }
};

const Mention = ({ attributes, children, element }: any) => {
    const selected = useSelected();
    const focused = useFocused();
    
    // Determine variable type and corresponding styles
    const isInputVariable = element.base?.createVar?.name;
    const variableType = isInputVariable ? 'input' : 'output';
    
    const baseClasses = `
        mention-tag inline-flex items-center gap-1 px-2 py-1 rounded-md text-sm font-medium
        transition-all duration-200 ease-in-out cursor-default select-none border
        ${variableType === 'input' 
            ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 border-green-200 hover:from-green-100 hover:to-emerald-100' 
            : 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 border-blue-200 hover:from-blue-100 hover:to-indigo-100'
        }
        ${selected && focused 
            ? 'ring-2 ring-offset-1 ' + (variableType === 'input' ? 'ring-green-300' : 'ring-blue-300')
            : ''
        }
    `;

    return (
        <span
            {...attributes}
            className={baseClasses}
            contentEditable={false}
            data-cy={`mention-${element.character?.replace(' ', '-') || 'unknown'}`}
        >
            {IS_MAC ? (
                <Fragment>
                    <span className="mention-prefix">@</span>
                    <span className="mention-name">{element.character}</span>
                    {children}
                </Fragment>
            ) : (
                <Fragment>
                    {/* Hidden original character for data */}
                    <span className="hidden">{element.character}</span>
                    
                    {/* Variable type icon */}
                    <span className={`
                        mention-icon w-3 h-3 rounded-full flex items-center justify-center text-xs font-bold
                        ${variableType === 'input' 
                            ? 'bg-green-500 text-white' 
                            : 'bg-blue-500 text-white'
                        }
                    `}>
                        {variableType === 'input' ? 'I' : 'V'}
                    </span>
                    
                    {/* Variable name */}
                    <span className="mention-name font-medium">
                        {element.base?.title || element.character}
                    </span>
                    
                    {/* Additional information for input variables */}
                    {element.base?.createVar?.name && (
                        <span className="mention-meta text-xs opacity-75">
                            ({element.base.createVar.name})
                        </span>
                    )}
                    
                    {children}
                </Fragment>
            )}
        </span>
    );
};

export default SlateEditorV3; 