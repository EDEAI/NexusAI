import { FC, useState } from 'react';
import { CaretRightOutlined, CaretDownOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm';
import { createRenderers } from '../MarkdownRenderer';

interface ThinkingBlockProps {
    content: string;
    isComplete: boolean;
    index: number;
    intl: any;
    isCurrentMessage?: boolean;
}

export const ThinkingBlock: FC<ThinkingBlockProps> = props => {
    const { content, isComplete, index, intl, isCurrentMessage = false } = props;
    const [isExpanded, setIsExpanded] = useState(false);

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    const label = isComplete
        ? intl.formatMessage({ id: 'app.chatroom.thinking.content' })
        : intl.formatMessage({ id: 'app.chatroom.thinking.inProgress' });

    return (
        <div className={`my-2 ${!isComplete ? 'mb-6' : ''}`}>
            <div
                className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-600 rounded cursor-pointer hover:bg-blue-100 transition-colors text-sm font-medium"
                onClick={toggleExpand}
            >
                {isExpanded ? <CaretDownOutlined /> : <CaretRightOutlined />}
                <span>{label}</span>
            </div>
            {isExpanded && (
                <div className="mt-2 p-3 bg-gray-50 rounded border border-gray-200 text-sm text-gray-500">
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                        components={createRenderers(index, intl, isCurrentMessage)}
                    >
                        {content}
                    </ReactMarkdown>
                </div>
            )}
        </div>
    );
};
