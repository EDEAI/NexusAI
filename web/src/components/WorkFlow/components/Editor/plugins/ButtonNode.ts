/*
 * @LastEditors: biz
 */
// ButtonNode.js
import { $applyNodeReplacement, ElementNode, NodeKey } from 'lexical';

export class ButtonNode extends ElementNode {
    __text: string;

    static getType() {
        return 'button';
    }

    static clone(node: ButtonNode) {
        return new ButtonNode(node.__text, node.__key);
    }

    constructor(text: string, key?: NodeKey) {
        super(key);
        this.__text = text;
    }

    createDOM(config) {
        const button = document.createElement('button');
        button.textContent = this.__text;
        button.className = 'my-custom-button';
        button.contentEditable = 'false'; 
        return button;
    }

    updateDOM(prevNode, dom) {
        if (prevNode.__text !== this.__text) {
            dom.textContent = this.__text;
        }
        return false;
    }

    static importJSON(serializedNode) {
        return $createButtonNode(serializedNode.__text);
    }

    exportJSON() {
        return {
            ...super.exportJSON(),
            type: 'button',
            __text: this.__text,
        };
    }
}

export function $createButtonNode(text: string) {
    return $applyNodeReplacement(new ButtonNode(text));
}

export function $isButtonNode(node) {
    return node instanceof ButtonNode;
}
