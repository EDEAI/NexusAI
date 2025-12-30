import { ReactNode } from 'react';

export interface ThinkingBlock {
    content: string;
    isComplete: boolean;
    startIndex: number;
    endIndex: number;
}

export interface ParsedContentWithThinking {
    parts: Array<{
        type: 'text' | 'thinking';
        content: string;
        isComplete?: boolean;
    }>;
}

const THINKING_START = '<<<thinking-start>>>';
const THINKING_END = '<<<thinking-end>>>';

/**
 * Parse content to extract thinking blocks
 * Handles both complete and incomplete thinking blocks
 * @param content - The content string to parse
 * @returns Parsed content with thinking blocks separated
 */
export const parseThinkingBlocks = (content: string): ParsedContentWithThinking => {
    if (!content || typeof content !== 'string') {
        return { parts: [{ type: 'text', content: content || '' }] };
    }

    const parts: ParsedContentWithThinking['parts'] = [];
    let currentIndex = 0;
    let nestingLevel = 0;

    while (currentIndex < content.length) {
        const startIndex = content.indexOf(THINKING_START, currentIndex);

        if (startIndex === -1) {
            parts.push({
                type: 'text',
                content: content.slice(currentIndex),
            });
            break;
        }

        parts.push({
            type: 'text',
            content: content.slice(currentIndex, startIndex),
        });

        const afterStart = startIndex + THINKING_START.length;
        const endIndex = content.indexOf(THINKING_END, afterStart);

        if (endIndex === -1) {
            parts.push({
                type: 'thinking',
                content: content.slice(afterStart),
                isComplete: false,
            });
            break;
        }

        const thinkingContent = content.slice(afterStart, endIndex);
        const hasNestedThinking = thinkingContent.includes(THINKING_START);

        if (hasNestedThinking) {
            parts.push({
                type: 'text',
                content: content.slice(startIndex, endIndex + THINKING_END.length),
            });
            currentIndex = endIndex + THINKING_END.length;
        } else {
            parts.push({
                type: 'thinking',
                content: thinkingContent,
                isComplete: true,
            });
            currentIndex = endIndex + THINKING_END.length;
        }
    }

    return { parts };
};

/**
 * Check if content contains thinking tags
 * @param content - The content string to check
 * @returns true if content contains thinking tags
 */
export const hasThinkingTags = (content: string): boolean => {
    if (!content || typeof content !== 'string') {
        return false;
    }
    return content.includes(THINKING_START);
};

/**
 * Check if content has incomplete thinking block
 * @param content - The content string to check
 * @returns true if content has incomplete thinking block
 */
export const hasIncompleteThinking = (content: string): boolean => {
    if (!content || typeof content !== 'string') {
        return false;
    }
    const startCount = (content.match(new RegExp(THINKING_START.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
    const endCount = (content.match(new RegExp(THINKING_END.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
    return startCount > endCount;
};
