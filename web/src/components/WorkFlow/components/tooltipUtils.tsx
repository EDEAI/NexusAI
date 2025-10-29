import React from 'react';
import type { CSSProperties, ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export const workflowTooltipOverlayStyle: CSSProperties = {
    maxHeight: 'min(60vh, 420px)',
    overflowY: 'auto',
    overflowX: 'hidden',
    maxWidth: 400,
};

export const renderWorkflowTooltip = (content?: string): ReactNode => {
    if (!content) return null;

    return (
        <div className="workflow-tooltip-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
    );
};

