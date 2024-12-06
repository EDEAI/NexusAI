/*
 * @LastEditors: biz
 */
import { $applyNodeReplacement, TextNode } from 'lexical';

export class MentionNode extends TextNode {
    static getType() {
        return 'mention';
    }

    static clone(node) {
        return new MentionNode(node.__text, node.__key);
    }

    static importJSON(serializedNode) {
        const node = $createMentionNode(serializedNode.text);
        node.setFormat(serializedNode.format);
        node.setDetail(serializedNode.detail);
        node.setMode(serializedNode.mode);
        node.setStyle(serializedNode.style);
        return node;
    }

    exportJSON() {
        return {
            ...super.exportJSON(),
            type: 'mention',
        };
    }

    createDOM(config) {
        const dom = super.createDOM(config);
        dom.className = 'mention';
        return dom;
    }

    isTextEntity() {
        return true;
    }
}

export function $createMentionNode(text) {
    const mentionNode = new MentionNode(text);
    $applyNodeReplacement(mentionNode);
    return mentionNode;
}
