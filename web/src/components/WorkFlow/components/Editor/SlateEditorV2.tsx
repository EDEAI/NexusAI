import { useIntl } from '@umijs/max';
import { useMount, useUpdateEffect } from 'ahooks';
import _ from 'lodash';
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
import { createEditor, Descendant, Editor, Node, Point, Range, Transforms } from 'slate';
import { withHistory } from 'slate-history';
import { Editable, ReactEditor, Slate, useFocused, useSelected, withReact } from 'slate-react';
import { CURRENT_NODE_ID } from '../../config';
import useStore from '../../store';

const Portal = ({ children }: { children?: ReactNode }) => {
    return typeof document === 'object' ? ReactDOM.createPortal(children, document.body) : null;
};

const IS_MAC = typeof navigator !== 'undefined' && /Mac OS X/.test(navigator.userAgent);

export interface MentionEditorProps {
    value?: any;
    onChange?: (value: any) => void;
    id?: string;
    placeholder?: string;
    options?: any;
    variables?: any;
}

const MentionEditor = ({
    value,
    onChange,
    id,
    placeholder,
    options,
    variables,
}: MentionEditorProps) => {
    const intl = useIntl();
    const ref = useRef<HTMLDivElement | null>();
    const [target, setTarget] = useState<Range | undefined>();
    const [index, setIndex] = useState(0);
    const [search, setSearch] = useState('');

    const renderElement = useCallback(props => <Element {...props} />, []);
    const renderLeaf = useCallback(props => <Leaf {...props} />, []);
    const editor = useMemo(() => withMentions(withReact(withHistory(createEditor()))), []);
    const [oldPropsValue, setOldPropsValue] = useState(null);

    const selectedNode = useStore(state => state.selectedNode);
    const getOutputVariables = useStore(state => state.getOutputVariables);
    const getInputVariables = useStore(state => state.getInputVariables);
    const [chars, setChars] = useState([]);
    useMount(() => {
        if (value && value.length > 0) {
            updateValue(value);
        }

        if (options?.length) {
            setChars(
                options.map(x => {
                    return {
                        ...x,
                        name: x.label,
                        id: x.value,
                    };
                }),
            );
        }

        if (selectedNode?.id) {
            let variableOptions = getOutputVariables(selectedNode.id)?.map(x => {
                return {
                    ...x,
                    name: x.label,
                    id: x.value,
                };
            });


            setChars(variableOptions);
        }
    });

    useUpdateEffect(() => {
        console.log(variables);
        if (variables?.length) {
            setChars(prev => {
                const varList = variables.map(x => {
                    return {
                        ...x,
                        id: `<<${CURRENT_NODE_ID}.inputs.${x.name}>>`,
                        createVar: {
                            name: x.name,
                        },
                    };
                });
                return [...prev, ...varList];
            });
        }
    }, [variables]);
    useUpdateEffect(() => {
        // console.log(selectedNode, value);

        const valueChange = _.isEqual(oldPropsValue, value);
        if (valueChange) return;

        if (value && value.length > 0) {
            updateValue(value);
        } else if (value && _.isArray(value) && value.length == 0) {
            updateValue([
                {
                    type: 'paragraph',
                    children: [],
                },
            ]);
        }
    }, [value, id]);

    // useUpdateEffect(() => {
    //     if (options.length) {
    //         setChars(
    //             options.map((x) => {
    //                 return {
    //                     ...x,
    //                     name: x.label,
    //                     id: x.value,
    //                 };
    //             }),
    //         );
    //     }
    // }, [options]);

    const updateValue = value => {
        setOldPropsValue(value);
        // resetNodes(editor, {
        //     nodes: [
        //         {
        //             type: 'paragraph',
        //             children: [],
        //         },
        //     ],
        // });
        resetNodes(editor, {
            nodes: value,
        });
    };

    const onKeyDown = useCallback(
        event => {
            if (target && chars.length > 0) {
                switch (event.key) {
                    case 'ArrowDown':
                        event.preventDefault();
                        const prevIndex = index >= chars.length - 1 ? 0 : index + 1;
                        setIndex(prevIndex);
                        return;
                    case 'ArrowUp':
                        event.preventDefault();
                        const nextIndex = index <= 0 ? chars.length - 1 : index - 1;
                        setIndex(nextIndex);
                        return;
                    case 'Tab':
                    case 'Enter':
                        event.preventDefault();
                        Transforms.select(editor, target);
                        insertMention(editor, chars[index]);
                        setTarget(null);
                        return;
                    case 'Escape':
                        event.preventDefault();
                        setTarget(null);
                        return;
                }
            } else if (event.key == '@' || event.key == '@') {
                setTimeout(() => listenShowOptions(), 10);
                return;
            }
            setTarget(null);
        },
        [chars, editor, index, target],
    );
    const resetNodes = (
        editor: Editor,
        options: {
            nodes?: Node | Node[];
            at?: Location;
        } = {},
    ): void => {
        const children = [...editor.children];

        children.forEach(node => editor.apply({ type: 'remove_node', path: [0], node }));

        if (options.nodes) {
            const nodes = Node.isNode(options.nodes) ? [options.nodes] : options.nodes;

            nodes.forEach((node, i) =>
                editor.apply({ type: 'insert_node', path: [i], node: node }),
            );
        }

        const point = options.at && Point.isPoint(options.at) ? options.at : Editor.end(editor, []);

        if (point) {
            Transforms.select(editor, point);
        }
    };
    useEffect(() => {
        if (target && chars.length > 0) {
            const el = ref.current;
            const domRange = ReactEditor.toDOMRange(editor, target);
            const rect = domRange.getBoundingClientRect();
            el.style.top = `${rect.top + window.pageYOffset + 24}px`;
            el.style.left = `${rect.left + window.pageXOffset}px`;
        }
    }, [chars.length, editor, index, search, target]);

    const listenShowOptions = () => {
        const { selection } = editor;

        if (selection && Range.isCollapsed(selection)) {
            const [start] = Range.edges(selection);
            const before = Editor.before(editor, start);
            const beforeRange = before && Editor.range(editor, before, start);
            const beforeText = beforeRange && Editor.string(editor, beforeRange);
            const after = Editor.after(editor, start);
            const afterRange = Editor.range(editor, start, after);
            const afterText = Editor.string(editor, afterRange);
            setTarget(beforeRange);
            setSearch('');
            setIndex(0);
            return;
        }
        setTarget(null);
    };

    return (
        <Slate
            editor={editor}
            initialValue={initialValue}
            onChange={val => {
                onChange?.(val);
                setTarget(null);
            }}
        >
            <Editable
                renderElement={renderElement}
                renderLeaf={renderLeaf}
                onKeyDown={onKeyDown}
                className="!outline-none"
                placeholder={
                    placeholder ??
                    intl.formatMessage({
                        id: 'workflow.placeholder.enterContent',
                        defaultMessage: '，@',
                    })
                }
            />
            {target && (
                <Portal>
                    <div
                        ref={ref}
                        style={{
                            top: '-9999px',
                            left: '-9999px',
                            position: 'absolute',
                            zIndex: 10,
                            padding: '3px',
                            background: 'white',
                            borderRadius: '4px',
                            boxShadow: '0 1px 5px rgba(0,0,0,.2)',
                        }}
                        className="px-1 pt-1 z-10"
                        data-cy="mentions-portal"
                    >
                        {chars.length ? (
                            chars.map((char, i) => (
                                <div
                                    key={char.name + i}
                                    onClick={() => {
                                        console.log(char);

                                        Transforms.select(editor, target);
                                        insertMention(editor, char);
                                        setTarget(null);
                                    }}
                                    className="hover:bg-blue-100 text-sm mb-1"
                                    style={{
                                        padding: '1px 3px',
                                        borderRadius: '3px',
                                        cursor: 'pointer',
                                        background: i === index ? '#B4D5FF' : '',
                                    }}
                                >
                                    <span>{char.title}</span>{' '}
                                    <span className="text-blue-500 text-xs">
                                        {char?.createVar?.name}
                                    </span>
                                </div>
                            ))
                        ) : (
                            <>
                                {intl.formatMessage({
                                    id: 'workflow.message.noVariablesFound',
                                    defaultMessage: '',
                                })}
                            </>
                        )}
                    </div>
                </Portal>
            )}
        </Slate>
    );
};

const withMentions = editor => {
    const { isInline, isVoid, markableVoid } = editor;

    editor.isInline = element => {
        return element.type === 'mention' ? true : isInline(element);
    };

    editor.isVoid = element => {
        return element.type === 'mention' ? true : isVoid(element);
    };

    editor.markableVoid = element => {
        return element.type === 'mention' || markableVoid(element);
    };

    return editor;
};

const insertMention = (editor, character) => {
    const mention = {
        type: 'mention',
        id: character?.id || '',
        character: character.name,
        base: character,
        children: [{ bold: true, text: '11111' }],
    };
    Transforms.insertNodes(editor, mention);
    Transforms.move(editor);
};

const Leaf = ({ attributes, children, leaf }) => {
    return <span {...attributes}>{children}</span>;
};

const Element = props => {
    const { attributes, children, element } = props;
    switch (element.type) {
        case 'mention':
            return <Mention {...props} />;
        default:
            return <p {...attributes}>{children}</p>;
    }
};

const Mention = ({ attributes, children, element }) => {
    const selected = useSelected();
    const focused = useFocused();
    const style: React.CSSProperties = {
        padding: '3px 3px 2px',
        margin: '0 1px',
        verticalAlign: 'baseline',
        display: 'inline-block',
        borderRadius: '4px',
        backgroundColor: '#eee',
        fontSize: '0.9em',
        boxShadow: selected && focused ? '0 0 0 2px #B4D5FF' : 'none',
    };
    if (element.children[0].bold) {
        style.fontWeight = 'bold';
    }
    if (element.children[0].italic) {
        style.fontStyle = 'italic';
    }

    return (
        <span
            {...attributes}
            className="m-2"
            contentEditable={false}
            data-cy={`mention-${element.character.replace(' ', '-')}`}
            style={style}
        >
            {IS_MAC ? (
                <Fragment>
                    1{children}/{element.character}
                </Fragment>
            ) : (
                <Fragment>
                    <span className="hidden">{element.character}</span>{' '}
                    <span>{element?.base?.title}</span>{' '}
                    <span className="text-blue-500 text-xs">{element.base?.createVar?.name}</span>
                    {children}
                </Fragment>
            )}
        </span>
    );
};

const initialValue: Descendant[] = [
    {
        type: 'paragraph',
        children: [
            {
                text: '',
            },
        ],
    },
];

export default MentionEditor;
