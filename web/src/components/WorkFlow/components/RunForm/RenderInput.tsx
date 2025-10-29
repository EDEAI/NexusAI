/*
 * @LastEditors: biz
 */
import { ProFormDigit, ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Form, Typography } from 'antd';
import _ from 'lodash';
import { useEffect, useMemo, useRef } from 'react';
import CodeEditor from '../Editor/CodeEditor';
import { UploadDragger } from '../Form/Upload';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm';

interface InputVariable {
    name: string;
    type: string;
    required?: boolean;
    sort_order?: number;
    display_name?: string;
    value?: any;
    description?: string;
}

interface RenderInputProps {
    data: Record<string, InputVariable>;
    /** Configure file upload mode - true for multiple files, false for single file */
    fileMultiple?: boolean;
}

export const RenderInput = ({ data, fileMultiple = false }: RenderInputProps) => {
    const intl = useIntl();
    const inputs = data;
    if (!inputs || _.isEmpty(inputs)) return null;

    const renderDescription = (description?: string) => {
        if (!description) return null;
        return (
            <div className="mt-1 text-xs text-gray-600 markdown-body">
                <ReactMarkdown rehypePlugins={[rehypeHighlight]} remarkPlugins={[remarkGfm]}>
                    {description}
                </ReactMarkdown>
            </div>
        );
    };

    const renderLabelBlock = (val: InputVariable) => (
        <>
            <div className="text-sm font-medium text-[#213044] flex items-center gap-1">
                {val.display_name || val.name}
                {val.required && <span className="text-red-500">*</span>}
            </div>
            {renderDescription(val.description)}
        </>
    );

    return (
        <div>
            <Typography.Title level={5}>
                {intl.formatMessage({
                    id: 'workflow.title.inputParameters',
                })}
            </Typography.Title>
            {Object.values(inputs)
                .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
                .map((val: any) => {
                    if (val.type === 'number') {
                        return (
                            <div key={val.name} className="mb-4">
                                {renderLabelBlock(val)}
                                <ProFormDigit
                                    required={false}
                                    rules={[
                                        {
                                            required: val.required,
                                            message: intl.formatMessage({
                                                id: 'workflow.form.parameter.required',
                                            }),
                                        },
                                    ]}
                                    name={val.name}
                                    initialValue={val.value}
                                    label={undefined}
                                />
                            </div>
                        );
                    }
                    if (val.type === 'file') {
                        return (
                            <div key={val.name} className="mb-4">
                                {renderLabelBlock(val)}
                                <UploadDragger
                                    name={val.name}
                                    label={undefined}
                                    required={val.required}
                                    multiple={fileMultiple}
                                />
                            </div>
                        );
                    }
                    if (val.type === 'json') {
                        // Create wrapper component to properly handle Form.Item value synchronization
                        const JSONFormEditor = ({
                            value,
                            onChange,
                        }: {
                            value?: string;
                            onChange?: (value: string) => void;
                        }) => {
                            const valueRef = useRef(value);

                            // Sync external value changes to internal reference
                            useEffect(() => {
                                valueRef.current = value;
                            }, [value]);

                            // Use useMemo to create stable CodeEditor instance
                            const CodeEditorMemo = useMemo(
                                () => (
                                    <div className="h-[300px]">
                                        <CodeEditor
                                            language="json"
                                            height={200}
                                            value={valueRef.current}
                                            onChange={newValue => {
                                                valueRef.current = newValue;
                                                onChange?.(newValue);
                                            }}
                                            showMaximize={true}
                                        />
                                    </div>
                                ),
                                [val.name], // Only depend on field name to keep editor instance stable
                            );

                            return CodeEditorMemo;
                        };

                        return (
                            <div key={val.name} className="mb-4">
                                {renderLabelBlock(val)}
                                <Form.Item
                                    label={false}
                                    required={false}
                                    name={val.name}
                                    rules={[
                                        {
                                            required: val.required,
                                            message: intl.formatMessage({
                                                id: 'workflow.form.parameter.required',
                                            }),
                                        },
                                        {
                                            validator: (_, value) => {
                                                if (!value) return Promise.resolve();
                                                try {
                                                    JSON.parse(value);
                                                    return Promise.resolve();
                                                } catch (e) {
                                                    return Promise.reject(
                                                        new Error(intl.formatMessage({ id: 'workflow.form.parameter.json.invalid' })),
                                                    );
                                                }
                                            },
                                        },
                                    ]}
                                    initialValue={
                                        val.value
                                            ? typeof val.value === 'string'
                                                ? val.value
                                                : JSON.stringify(val.value, null, 2)
                                            : '{}'
                                    }
                                >
                                    <JSONFormEditor />
                                </Form.Item>
                            </div>
                        );
                    }
                    return (
                        <div key={val.name} className="mb-4">
                            {renderLabelBlock(val)}
                            <ProFormTextArea
                                required={false}
                                rules={[
                                    {
                                        required: val.required,
                                        message: intl.formatMessage({
                                            id: 'workflow.form.parameter.required',
                                        }),
                                    },
                                ]}
                                name={val.name}
                                initialValue={val.value}
                                label={undefined}
                            />
                        </div>
                    );
                })}
        </div>
    );
};

export default RenderInput;
