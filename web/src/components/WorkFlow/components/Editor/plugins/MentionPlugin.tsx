/*
 * @LastEditors: biz
 */
// MentionPlugin.tsx
import { LexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import { List } from 'antd';
import { $getSelection, $insertNodes } from 'lexical';
import { useCallback, useContext, useEffect, useState } from 'react';
import { $createMentionNode } from './MentionNode';

interface User {
    id: string;
    name: string;
}

export default function MentionPlugin() {
    const [editor] = useContext(LexicalComposerContext);
    const [suggestions, setSuggestions] = useState<User[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [position, setPosition] = useState<{ top: number; left: number } | null>(null);

    useEffect(() => {
        
        const fetchUsers = async () => {
            const users = await fetch('/api/users').then(res => res.json());
            setSuggestions(users);
        };
        fetchUsers();
    }, []);

    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        if (event.key === '@') {
            
            const target = event.target as HTMLElement;
            if (target) {
                const rect = target.getBoundingClientRect();
                setPosition({
                    top: rect.top + window.scrollY + 20,
                    left: rect.left + window.scrollX,
                });
                setShowSuggestions(true);
            }
        }
    }, []);

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [handleKeyDown]);

    const insertMention = useCallback(
        (mention: string) => {
            console.log('Inserting mention:', mention);
            editor.update(() => {
                const selection = $getSelection();
                if (selection !== null) {
                    $insertNodes([$createMentionNode(mention)]);
                    setShowSuggestions(false);
                }
            });
        },
        [editor],
    );

    return (
        <div className="mention-plugin">
            {showSuggestions && position && (
                <List
                    bordered
                    dataSource={suggestions}
                    renderItem={user => (
                        <List.Item onClick={() => insertMention(user.name)}>@{user.name}</List.Item>
                    )}
                    style={{
                        position: 'absolute',
                        // top: position.top,
                        // left: position.left,
                        zIndex: 1000,
                        backgroundColor: '#fff',
                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
                    }}
                />
            )}
        </div>
    );
}
