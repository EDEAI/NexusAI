/*
 * @LastEditors: biz
 */
import { DeleteOutlined } from '@ant-design/icons';
import { useReactive } from 'ahooks';
import { Button } from 'antd';
import React, { useEffect, useState } from 'react';
import SlateEditorV2 from './SlateEditorV2';


export default ({ value: propsValue, onChange }) => {
    const [value, setValue] = useState([
        {
            key: {
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
        setValue([...value, { key: { content: [] } }]);
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
        if (type == 'value' && index == value.length - 1) {
            addLine();
        }

        if (reacSaveValue.saveValue[index] == undefined) {
            reacSaveValue.saveValue[index] = { key: { content: [] }, value: { content: [] } };
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
                {value.map((x, i) => (
                    <div
                        key={i}
                        className={`group grid grid-cols-2 relative border-b last-of-type:!border-none  border-slate-300`}
                    >
                        <div className="user-p-none-mb px-2 py-1">
                            <SlateEditorV2
                                id={`key${i}`}
                                value={x?.key?.content}
                                onChange={e => handleChange(e, 'key', i)}
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
