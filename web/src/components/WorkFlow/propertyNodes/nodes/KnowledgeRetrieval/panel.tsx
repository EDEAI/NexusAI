/*
 * @LastEditors: biz
 */
import React from 'react';
import { Form, Input, Select } from 'antd';
import { useIntl } from 'umi';

interface Props {
    data: {
        title: string;
        entitle: string;
        desc: string;
    };
    onChange: (data: any) => void;
}

const KnowledgeRetrievalPanel: React.FC<Props> = ({ data, onChange }) => {
    const intl = useIntl();
    const isEn = intl.locale === 'en-US';

    const handleChange = (values: any) => {
        onChange({
            ...data,
            ...values,
        });
    };

    return (
        <Form
            layout="vertical"
            initialValues={data}
            onValuesChange={handleChange}
        >
            <Form.Item
                label={isEn ? 'Title' : '标题'}
                name={isEn ? 'entitle' : 'title'}
            >
                <Input />
            </Form.Item>
            <Form.Item
                label={isEn ? 'Description' : '描述'}
                name="desc"
            >
                <Input.TextArea rows={4} />
            </Form.Item>
            <Form.Item
                label={isEn ? 'Knowledge Base' : '知识库'}
                name="knowledgeBase"
            >
                <Select
                    mode="multiple"
                    placeholder={isEn ? 'Select knowledge bases' : '选择知识库'}
                    options={[
                        // TODO: Add knowledge base options
                    ]}
                />
            </Form.Item>
            <Form.Item
                label={isEn ? 'Top K' : '检索数量'}
                name="topK"
            >
                <Input type="number" min={1} max={20} />
            </Form.Item>
        </Form>
    );
};

export default KnowledgeRetrievalPanel; 