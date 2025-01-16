import React, { useEffect, useRef, useState } from 'react';

/**
 * Props interface for EditableItem component
 * @interface EditableItemProps
 */
interface EditableItemProps {
    /** Child content */
    children: React.ReactNode;
    /** Callback function when content is updated */
    onUpdate: (value: string) => void;
    /** Maximum character length limit */
    maxLength?: number;
    /** Border color when focused */
    focusBorderColor?: string;
    /** Placeholder text */
    placeholder?: string;
    /** Whether editing is disabled */
    disabled?: boolean;
    /** Custom class name */
    className?: string;
    /** Base style */
    style?: React.CSSProperties;
    /** Style when hovering */
    hoverStyle?: React.CSSProperties;
    /** Style when focused */
    focusStyle?: React.CSSProperties;
    /** Callback function when content changes */
    onChange?: (value: string) => void;
    /** Callback function when editing is cancelled */
    onCancel?: () => void;
    /** Callback function when editing starts */
    onStart?: () => void;
    /** Callback function when focused */
    onFocus?: (e: React.FocusEvent) => void;
    /** Callback function when blurred */
    onBlur?: (e: React.FocusEvent) => void;
}

/**
 * An editable content component
 * @component
 * @param {EditableItemProps} props - Component properties
 * @returns {TSX.Element} Returns an editable content component
 * @example
 * ```tsx
 * <EditableItem
 *   onUpdate={(value) => console.log(value)}
 *   maxLength={100}
 *   placeholder="Enter content"
 * >
 *   Initial content
 * </EditableItem>
 * ```
 */
export const EditableItem = ({
    children,
    onUpdate,
    maxLength,
    focusBorderColor = 'blue-500',
    placeholder = '请输入内容',
    disabled = false,
    className = '',
    style = {},
    hoverStyle = {},
    focusStyle = {},
    onChange,
    onCancel,
    onStart,
    onFocus,
    onBlur,
}: EditableItemProps) => {
    const [isEditing, setIsEditing] = useState(false);
    const [isFocused, setIsFocused] = useState(false);
    const [history, setHistory] = useState<string[]>([children as string]);
    const [historyIndex, setHistoryIndex] = useState(0);
    const contentRef = useRef<HTMLDivElement>(null);
    const initialValue = useRef(children as string);

    useEffect(() => {
        if (contentRef.current) {
            autoResize();
        }
    }, [children]);

    const autoResize = () => {
        const element = contentRef.current;
        if (element) {
            element.style.height = 'auto';
            element.style.height = `${element.scrollHeight}px`;
        }
    };

    const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
        const content = e.currentTarget.textContent || '';
        if (maxLength && content.length > maxLength) {
            e.currentTarget.textContent = content.substring(0, maxLength);
        }
        onChange?.(content);
        autoResize();
    };

    const handleFocus = (e: React.FocusEvent<HTMLDivElement>) => {
        if (disabled) return;
        setIsEditing(true);
        setIsFocused(true);
        onStart?.();
        onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLDivElement>) => {
        setIsEditing(false);
        setIsFocused(false);
        const newValue = e.currentTarget.textContent || '';
        
        if (newValue !== initialValue.current) {
            setHistory(prev => [...prev, newValue]);
            setHistoryIndex(prev => prev + 1);
            onUpdate(newValue);
        }
        
        onBlur?.(e);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            (e.target as HTMLDivElement).blur();
        }
        if (e.key === 'Escape') {
            e.currentTarget.textContent = initialValue.current;
            onCancel?.();
            (e.target as HTMLDivElement).blur();
        }
        // Undo
        if (e.key === 'z' && (e.ctrlKey || e.metaKey) && historyIndex > 0) {
            e.preventDefault();
            const previousValue = history[historyIndex - 1];
            setHistoryIndex(prev => prev - 1);
            e.currentTarget.textContent = previousValue;
            onChange?.(previousValue);
        }
        // Redo
        if (e.key === 'y' && (e.ctrlKey || e.metaKey) && historyIndex < history.length - 1) {
            e.preventDefault();
            const nextValue = history[historyIndex + 1];
            setHistoryIndex(prev => prev + 1);
            e.currentTarget.textContent = nextValue;
            onChange?.(nextValue);
        }
    };

    return (
        <div
            ref={contentRef}
            contentEditable={!disabled}
            onInput={handleInput}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            suppressContentEditableWarning={true}
            className={`
                outline-none transition-all duration-300
                ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-text'}
                ${!children && !isEditing ? 'text-gray-400' : ''}
                ${isFocused ? `focus:border-${focusBorderColor} focus:ring-1 focus:ring-${focusBorderColor}` : ''}
                ${className}
            `}
            style={{
                ...style,
                ...(isFocused ? focusStyle : {}),
                ...(!isFocused && !disabled ? hoverStyle : {}),
            }}
        >
            {children || (!isEditing && placeholder)}
        </div>
    );
};