/*
 * @LastEditors: biz
 */
import React, { memo } from 'react';
import { Button, Radio, Typography } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
const { Paragraph } = Typography;

interface EditableCardProps {
    /** Card title */
    title: string;
    /** Card description */
    description: string;
    /** Icon source */
    icon?: string;
    /** Output format value */
    outputFormat?: number;
    /** Callback when any field changes */
    onChange?: (changes: { title?: string; description?: string; outputFormat?: number }) => void;
    /** Callback when delete button is clicked */
    onDelete?: () => void;
    /** Whether the card is read-only */
    readOnly?: boolean;
}

export const EditableCard = memo(({
    title,
    description,
    icon = '/icons/agent_skill.svg',
    outputFormat = 1,
    onChange,
    onDelete,
    readOnly = false,
}: EditableCardProps) => {
    return (
        <div 
            className={`p-4 bg-white rounded-md relative ${!readOnly ? 'group' : ''}`}
            style={{ boxShadow: '0px 0px 4px 0px rgba(0,0,0,0.1)' }}
        >
            <Button
                type="text"
                icon={<DeleteOutlined className="text-red-500" />}
                onClick={onDelete}
                style={{ display: readOnly ? 'none' : undefined }}
                className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity"
            />
            <div className="px-2 py-1">
                <Paragraph
                    editable={!readOnly ? {
                        onChange: (value) => onChange?.({ title: value }),
                        text: title,
                        triggerType: ['text'],
                        autoSize: true,
                    } : false}
                    className={`rounded-lg !mb-0 text-[14px] flex items-center ${!readOnly ? 'hover:bg-blue-100' : ''}`}
                >
                    <img src={icon} className="size-5 mr-1" />
                    {title}
                </Paragraph>
            </div>
            <div className="pl-2 py-1 mt-2">
                <Paragraph
                    editable={!readOnly ? {
                        onChange: (value) => onChange?.({ description: value }),
                        text: description,
                        triggerType: ['text'],
                        autoSize: true,
                    } : false}
                    className={`rounded-lg !mb-0 text-[#999999] text-[12px] flex items-center ${!readOnly ? 'hover:bg-blue-100' : ''}`}
                >
                    {description}
                </Paragraph>
            </div>
            <div className="pl-2 py-1 mt-2">
                <Radio.Group 
                    size="small" 
                    onChange={e => onChange?.({ outputFormat: e.target.value })} 
                    value={outputFormat}
                    disabled={readOnly}
                >
                    <Radio value={1}>text</Radio>
                    <Radio value={2}>json</Radio>
                    <Radio value={3}>code</Radio>
                </Radio.Group>
            </div>
        </div>
    );
}); 