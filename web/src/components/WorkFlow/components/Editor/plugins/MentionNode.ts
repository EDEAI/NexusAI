// MentionNode.ts
import { EditorConfig, NodeKey, TextNode } from 'lexical';


export class MentionNode extends TextNode {
    __mention: string;

    static getType(): string {
        return 'mention';
    }

    constructor(mention: string, key?: NodeKey) {
        super(`@${mention}`, key);
        this.__mention = mention;
    }

  
    createDOM(config: EditorConfig): HTMLElement {
        const dom = document.createElement('span');
        dom.className = 'mention';
        dom.style.userSelect = 'none';
        dom.contentEditable = 'false'; 
        dom.textContent = `@${this.__mention}`;
        return dom;
    }

   
    updateDOM(prevNode: MentionNode, dom: HTMLElement, config: EditorConfig): boolean {
        const updated = super.updateDOM(prevNode, dom, config);
        if (updated) {
            dom.textContent = `@${this.__mention}`;
        }
        return updated;
    }

  
    getTextContent(): string {
        return `@${this.__mention}`;
    }
}


export function $createMentionNode(mention: string): MentionNode {
    return new MentionNode(mention);
}
