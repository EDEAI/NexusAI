import { headportrait } from '@/utils/useUser';
import { Popover } from 'antd';
import React, { useEffect } from 'react';
interface ChildProps {
    CardData: any;
    setCardData: any;
}

const profilephoto: React.FC<ChildProps> = ({ CardData, setCardData }) => {
   
    useEffect(() => {}, []);
    const contentPhone = () => {
        return (
            <div className="flex justify-start items-center flex-wrap w-40">
                {headportrait('all').map((item: any) => {
                    return (
                        <div
                            className="w-8 h-8 bg-[#F4F8F1] rounded-lg mr-1.5 flex items-center justify-center m-0.5 cursor-pointer"
                            onClick={() => {
                                pitchphone(item);
                            }}
                        >
                            <img src={item.image} alt="" />
                        </div>
                    );
                })}
            </div>
        );
    };
   
    const pitchphone = (data: any) => {
        setCardData({ ...CardData, icon: data.image, id: data.id });
    };
    return (
        <Popover content={contentPhone} trigger="click" placement="bottomLeft">
            <div className="w-8 h-8 bg-[#F4F8F1] rounded-lg mr-1.5 flex items-center justify-center m-0.5 cursor-pointer">
                <img
                    src={headportrait('single', CardData.id ? CardData.id : CardData.icon)}
                    alt=""
                />
            </div>
        </Popover>
    );
};
export default profilephoto;
