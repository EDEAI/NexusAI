import React, { useEffect } from 'react';

interface ChildProps {
    Image: any;
    icon?: any;
}
const headportrait: React.FC<ChildProps> = ({ Image, icon }) => {
    useEffect(() => {}, []);
    return (
        <div className="w-[42px] h-[42px] bg-[#F4F8F1] rounded-md flex items-center justify-center relative">
            <div>
                <img src={Image} alt="" />
            </div>
            {icon ? (
                <div className="absolute bottom-[-3px] right-[-3px] w-4 h-4 bg-white rounded-sm flex items-center justify-center shadow-[0_0_4px_-0_rgba(0,0,0,0.2)]">
                    <img className=" w-[12px] h-[12px]" src={icon} alt="" />
                </div>
            ) : null}
        </div>
    );
};
export default headportrait;
