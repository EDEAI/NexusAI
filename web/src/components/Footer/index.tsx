/*
 * @LastEditors: biz
 */
import React from 'react';

interface FooterProps {
    className?: any;
}

const Footer: React.FC<FooterProps> = props => {
    let { className = '' } = props;
    //  news
    return (
        <div
            className={`w-full  text-xs text-[#9B9B9B]  flex items-center pl-[30px] py-[10px] fixed left-0 bottom-0 box-border ${className}`}
            style={{ borderTop: '1px solid #EEEEEE' }}
        >
            <div>version 0.0.1-alpha.1 </div>
        </div>
    );
};

export default Footer;
