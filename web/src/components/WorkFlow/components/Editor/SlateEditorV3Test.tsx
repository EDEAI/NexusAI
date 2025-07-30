/*
 * @LastEditors: biz
 */
import { Card, Space, Switch, Typography } from 'antd';
import React, { useState } from 'react';
import type { Descendant } from 'slate';
import SlateEditorV2 from './SlateEditorV2';
import SlateEditorV3 from './SlateEditorV3';

const { Title, Text } = Typography;

interface TestProps {
    value?: Descendant[];
    onChange?: (value: Descendant[]) => void;
    placeholder?: string;
    options?: any[];
    variables?: any[];
    id?: string;
}

const SlateEditorV3Test: React.FC<TestProps> = props => {
    const [useV3, setUseV3] = useState(false);
    const [testValue, setTestValue] = useState<Descendant[]>([]);

    const handleChange = (value: Descendant[]) => {
        setTestValue(value);
        props.onChange?.(value);
    };
    return <SlateEditorV3 {...props} value={props.value || testValue} onChange={handleChange} />;
    return (
        <div className="space-y-4">
            <Card size="small">
                <Space align="center">
                    <Text>使用版本:</Text>
                    <Switch
                        checked={useV3}
                        onChange={setUseV3}
                        checkedChildren="V3"
                        unCheckedChildren="V2"
                    />
                    <Text type="secondary">
                        当前: {useV3 ? 'SlateEditorV3 (新版本)' : 'SlateEditorV2 (原版本)'}
                    </Text>
                </Space>
            </Card>

            <Card
                title={
                    <Title level={5} style={{ margin: 0 }}>
                        编辑器测试 - {useV3 ? 'V3版本' : 'V2版本'}
                    </Title>
                }
                size="small"
            >
                {useV3 ? (
                    <SlateEditorV3
                        {...props}
                        value={props.value || testValue}
                        onChange={handleChange}
                    />
                ) : (
                    <SlateEditorV2
                        {...props}
                        value={props.value || testValue}
                        onChange={handleChange}
                    />
                )}
            </Card>

            {/* 调试信息 */}
            <Card title="调试信息" size="small" style={{ fontSize: '12px' }}>
                <pre style={{ fontSize: '10px', maxHeight: '200px', overflow: 'auto' }}>
                    {JSON.stringify(testValue, null, 2)}
                </pre>
            </Card>
        </div>
    );
};

export default SlateEditorV3Test;
