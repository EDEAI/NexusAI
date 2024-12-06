import { flip, offset, shift, useFloating } from '@floating-ui/react';
import { useCallback, useState } from 'react';
import { BaseEditor, createEditor, Editor, Path, Range, Transforms } from 'slate';
import { Editable, ReactEditor, Slate, withReact } from 'slate-react';
import VariableSelect from './components/VariableSelect';

type CustomElement = { type: 'paragraph'; children: CustomText[] };
type CustomText = { text: string };

declare module 'slate' {
    interface CustomTypes {
        Editor: BaseEditor & ReactEditor;
        Element: CustomElement;
        Text: CustomText;
    }
}

const initialValue: CustomElement[] = [
    {
        type: 'paragraph',
        children: [{ text: '' }],
    },
];

const Leaf = props => {
    return (
        <span
            {...props.attributes}
            style={{ fontWeight: props.leaf.bold ? 'bold' : 'normal', color: 'red' }}
        >
            {props.children}
        </span>
    );
};

const DefaultElement = props => {
    switch (props.element.type) {
        case 'button':
            return (
                <button {...props.attributes} onClick={() => alert('Button clicked!')}>
                    <span>{props.children}</span>
                </button>
            );
        default:
            return <span {...props.attributes}>{props.children}</span>;
    }
};

const FloatingComponent = () => {
    const [editor] = useState(() => withReact(createEditor()));
    const [isOpen, setIsOpen] = useState(false);

    const { refs, floatingStyles, update } = useFloating({
        placement: 'bottom-start',
        middleware: [offset(5), shift({ padding: 8 }), flip()],
    });

    const renderElement = useCallback(props => {
        return <DefaultElement {...props} />;
    }, []);

    const renderLeaf = useCallback(props => {
        return <Leaf {...props} />;
    }, []);

    const handleKeyDown = event => {
        if (event.key === '/') {
            event.preventDefault();
            setIsOpen(true);
            setTimeout(() => {

                const { selection } = editor;
                if (selection) {

                    const domRange = ReactEditor.toDOMRange(editor, selection);
                    const rect = domRange.getBoundingClientRect();


                    refs.setReference({
                        getBoundingClientRect: () => rect,
                    });
                    update();
                }
            }, 0);
        }

        if (!event.ctrlKey && event.key === 'Backspace') {
            const { selection } = editor;
            if (!selection || !Range.isCollapsed(selection)) return;

            try {

                const ancestorNode = Editor.above(editor, {
                    match: n => Editor.isBlock(editor, n),
                });
                console.log(ancestorNode);

                if (ancestorNode) {
                    const [node, path] = ancestorNode;

                    if (node.type === 'button') {
                        event.preventDefault();
                        Transforms.removeNodes(editor, { at: path });
                        return;
                    }
                }


                const previousNode = Editor.previous(editor, {
                    at: selection.focus,
                    match: n => Editor.isBlock(editor, n),
                });
                if (previousNode) {
                    const [node, path] = previousNode;
                    if (node.type === 'button') {
                        event.preventDefault();
                        Transforms.removeNodes(editor, { at: path });
                        return;
                    }
                }
            } catch (error) {
                console.error('Error processing backspace:', error);
            }
        }
    };

    const handleBlur = () => {
        setTimeout(() => {
            setIsOpen(false);
        }, 200);
    };

    const handleSelect = () => {
        if (isOpen) {
            setTimeout(() => {
                setIsOpen(false);
            }, 200);
        }
    };
    const handleChange = (item, index) => {
        console.log('Selected item:', item, 'at index:', index);


        const { selection } = editor;
        if (selection) {
            const buttonNode: CustomElement = {
                type: 'button',
                children: [{ text: '' }],
            };


            Transforms.insertNodes(editor, buttonNode, { at: selection.anchor });
            Transforms.insertNodes(
                editor,
                {
                    type: 'paragraph',
                    children: [{ text: '' }],
                },
                { at: Path.next(selection.anchor.path) },
            );

        }
    };

    return (
        <div>
            <Slate editor={editor} initialValue={initialValue}>
                <Editable
                    className="!border-transparent !outline-none"
                    renderElement={renderElement}
                    renderLeaf={renderLeaf}
                    onKeyDown={handleKeyDown}
                    onBlur={handleBlur}
                    onSelect={handleSelect}
                />
                {isOpen && (
                    <VariableSelect
                        ref={refs.setFloating}
                        list={[
                            {
                                name: '1',
                            },
                            {
                                name: '2',
                            },
                            {
                                name: '3',
                            },
                            {
                                name: '4',
                            },
                        ]}
                        style={floatingStyles}
                        onChange={handleChange}
                    />
                )}
            </Slate>
        </div>
    );
};

export default FloatingComponent;
