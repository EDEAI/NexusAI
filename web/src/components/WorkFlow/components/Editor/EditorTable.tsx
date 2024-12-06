/*
 * @LastEditors: biz
 */
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useReactive } from 'ahooks';
import { Button, Input } from 'antd';
import React, { useEffect, useState } from 'react';
import SlateEditorV2 from './SlateEditorV2';

type DataSourceType = {
    id: React.Key;
    title?: string;
    decs?: string;
    state?: string;
    created_at?: number;
    children?: DataSourceType[];
};
const initialValue = [
    {
        type: 'paragraph',
        children: [
            {
                text: '',
            },
        ],
    },
];
export default ({ value: propsValue, onChange }) => {
    const [hoveredIndex, setHoveredIndex] = useState(null);
    const intl = useIntl();
    const [value, setValue] = useState([
        {
            key: {
                content: '',
            },
            value: {
                content: [],
            },
        },
    ]);
    useEffect(() => {
        if (propsValue?.length) {

            reacSaveValue.saveValue = propsValue;
            setValue(propsValue);
        }
    }, [propsValue]);
    const reacSaveValue = useReactive({
        saveValue: [],
    });
    const addLine = () => {
        setValue([...value, { key: { content: '' }, value: { content: [] } }]);
        // reacSaveValue.saveValue.push({ key: { content: [] }, value: { content: [] } });
    };
    const delLine = delIndex => {
        try {
            console.log(reacSaveValue.saveValue);
            const newVal = reacSaveValue.saveValue.filter((x, i) => i != delIndex);
            console.log(newVal, value);

            reacSaveValue.saveValue = newVal;
            setValue(newVal);
            onChange?.(reacSaveValue.saveValue);
        } catch (error) {
            console.log(error);
        }
    };

    const editorChange = (e, type, index) => {
        console.log(e, type, index);
    };
    const handleChange = (e, type, index) => {
        if (type == 'key') {
            e = e.target.value;
        }
        console.log(e, type, index);
        if (type == 'value' && index == value.length - 1) {
            addLine();
        }

        if (reacSaveValue.saveValue[index] == undefined) {
            reacSaveValue.saveValue[index] = { key: { content: '' }, value: { content: [] } };
        }
        const saveData = {
            ...reacSaveValue.saveValue[index],
            [type]: {
                content: e,
            },
        };
        reacSaveValue.saveValue[index] = saveData;
        onChange?.(reacSaveValue.saveValue);
    };

    return (
        <>
            <div className="border border-slate-300 rounded-md">
                <div className="grid grid-cols-2 h-10 border-b border-slate-300">
                    <div className="px-2 flex items-center justify-between">
                        {intl.formatMessage({ id: 'workflow.label.key', defaultMessage: '' })}
                        <Button
                            type="text"
                            onClick={addLine}
                            className="ml-2"
                            icon={<PlusOutlined></PlusOutlined>}
                        ></Button>
                    </div>
                    <div className="px-2 flex items-center border-l border-slate-300">
                        {intl.formatMessage({ id: 'workflow.label.value', defaultMessage: '' })}
                    </div>
                </div>

                {value.map((x, i) => (
                    <div
                        key={i}
                        className={`group grid grid-cols-2 relative border-b last-of-type:!border-none  border-slate-300`}
                    >
                        <div className="user-p-none-mb px-2 py-1">
                            <Input
                                value={x?.key?.content}
                                placeholder={intl.formatMessage({
                                    id: 'workflow.placeholder.enterKeyName',
                                    defaultMessage: '',
                                })}
                                variant="borderless"
                                allowClear
                                onChange={e => {
                                    handleChange(e, 'key', i);
                                    setValue(prev => {
                                        return prev.map((item, index) => {
                                            if (index == i) {
                                                return {
                                                    ...item,
                                                    key: {
                                                        content: e.target.value,
                                                    },
                                                };
                                            } else {
                                                return item;
                                            }
                                        });
                                    });
                                }}
                            ></Input>
                        </div>
                        <div className="user-p-none-mb px-2  py-1 border-l border-slate-300">
                            <SlateEditorV2
                                id={`value${i}`}
                                value={x?.value?.content}
                                onChange={e => handleChange(e, 'value', i)}
                            />
                        </div>

                        <Button
                            type="text"
                            icon={<DeleteOutlined />}
                            className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                            onClick={() => delLine(i)}
                        ></Button>
                    </div>
                ))}
            </div>
        </>
    );
};
