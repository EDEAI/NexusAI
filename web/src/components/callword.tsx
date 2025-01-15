/*
 * @LastEditors: wnagchi 1305bcd@gmail.com
 */
/*
 * @LastEditors: biz
 */
import { QuestionCircleOutlined } from '@ant-design/icons';
import { Tooltip } from 'antd';
import React, { useEffect } from 'react';

interface ChildProps {
    title: any;
    name: any;
    className?: any;
    required?: any;
}
const callword: React.FC<ChildProps> = ({ title, name, className, required }) => {


    useEffect(() => {}, []);
    return (
        <div className={className}>
            <span className="mr-2">
                <span className="text-[#E80000]">{required ? '*' : ''}</span> {name}
            </span>
            <Tooltip title={title}>
                <QuestionCircleOutlined className="cursor-pointer" />
            </Tooltip>
        </div>
    );
};
export default callword;
