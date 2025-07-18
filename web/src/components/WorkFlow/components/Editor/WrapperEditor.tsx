/*
 * @LastEditors: biz
 */
import { memo, useState } from 'react';
import SlateEditorV2, { MentionEditorProps } from './SlateEditorV2';
import { getCharacterCount } from './components/slateEditorUtils';
import SlateEditorV3Test from './SlateEditorV3Test';

interface WrapperEditorProps {
    title?: string;
}

export default memo((props: WrapperEditorProps & MentionEditorProps) => {
    const { title, onChange, ...restProps } = props;
    const [len, setLen] = useState(0);
    const handleChange = e => {
        onChange?.(e);
        setLen(getCharacterCount(e || []));
    };
    return (
        <div className="p-2 border-stone-300 border rounded-md my-2">
            <div className="flex justify-between cursor-default">
                <div>
                    {title && <div className="text-sm text-gray-500 font-bold pb-2">{title}</div>}
                </div>
                <div className="text-blue-400">{len}</div>
            </div>
            <div className="max-h-48 min-h-24 overflow-y-auto">
                {/* <SlateEditorV2 onChange={handleChange} {...restProps}></SlateEditorV2> */}
                <SlateEditorV3Test onChange={handleChange} {...restProps}></SlateEditorV3Test>

            </div>
        </div>
    );
});
