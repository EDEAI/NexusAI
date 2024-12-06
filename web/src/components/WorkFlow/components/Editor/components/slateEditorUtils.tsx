import { css } from '@emotion/css';
import { useSelected } from 'slate-react';
const serialize = nodes => {
    return nodes
        .map(node => {
            if (node.type === 'mention') {
                return node.id;
            } else if (node.children) {
                return serialize(node.children);
            } else {
                return node.text;
            }
        })
        .join('');
};

export const getCharacterCount = nodes => {
    return nodes.reduce((count, node) => {
        if (typeof node.text === 'string') {
            count += node.text.length;
        }
        if (node.children) {
            count += getCharacterCount(node.children);
        }
        return count;
    }, 0);
};
export const withInlines = editor => {
    const { isInline, isElementReadOnly, isSelectable } = editor;

    editor.isInline = element => ['badge'].includes(element.type) || isInline(element);

    editor.isElementReadOnly = element => element.type === 'badge' || isElementReadOnly(element);

    editor.isSelectable = element => element.type !== 'badge' && isSelectable(element);

    // editor.insertText = (text) => {
    //     insertText(text);
    // };

    // editor.insertData = (data) => {
    //     insertData(data);
    // };

    return editor;
};
export const InlineChromiumBugfix = () => (
    <span
        contentEditable={false}
        className={css`
            font-size: 0;
        `}
    >
        {String.fromCodePoint(160) /* Non-breaking space */}
    </span>
);
export const BadgeComponent = ({ attributes, children, element }) => {
    const selected = useSelected();

    return (
        <span
            {...attributes}
            contentEditable={false}
            className={css`
                display: inline;
                background-color: green;
                color: white;
                padding: 2px 6px;
                margin: 0 4px !important;
                border-radius: 2px;
                font-size: 0.9em;
                ${selected && 'box-shadow: 0 0 0 3px #ddd;'}
            `}
            data-playwright-selected={selected}
        >
            <InlineChromiumBugfix />
            {children}
            <InlineChromiumBugfix />
        </span>
    );
};
export const Element = props => {
    const { attributes, children, element } = props;
    switch (element.type) {
        case 'badge':
            return <BadgeComponent {...props} />;
        default:
            return <p {...attributes}>{children}</p>;
    }
};

export const Text = props => {
    const { attributes, children, leaf } = props;
    return (
        <span
            className={
                leaf.text === ''
                    ? css`
                          padding-left: 1px;
                      `
                    : null
            }
            {...attributes}
        >
            {children}
        </span>
    );
};
