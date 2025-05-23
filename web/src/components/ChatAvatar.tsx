/*
 * @LastEditors: biz
 */
import { headportrait } from '@/utils/useUser';
import React, { memo } from 'react';

interface params {
    width?: string;
    bg?: string;
    rounded?: string;
    data?: any;
    imgWidth?: string;
    background?: string;
}

const AvatarContent: React.FC<params> = param => {
    let { width = "40px", bg = "#F4F8F1", rounded = "6px", data, imgWidth = '18px', background } = param;
    if (data?.avatar) {
        imgWidth = width;
    }
    
    const bgColor = background || bg;
    
    return (
        <div className="relative flex items-center justify-center shrink-0" style={{
            width: width,
            height: width,
            backgroundColor: bgColor,
            borderRadius: rounded
        }}>
            <img
                src={data?.avatar ? data.avatar : headportrait('single', data?.icon)}
                style={{
                    width: imgWidth,
                    height: imgWidth,
                    borderRadius: rounded
                }}
                alt=""
            />
        </div>
    );
};

export default memo(AvatarContent);
