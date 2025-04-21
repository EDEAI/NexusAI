import { headportrait } from '@/utils/useUser';
import { Progress } from 'antd';
import React, { useState } from 'react';

interface GraphicProps {
    subtitle?: any;
    handleClick?: any;
    lineClamp?: number;
    textDetails?: any;
    title?: any;
    icon?: any;
    iconType?: any;
    operation?: any;
    progress?: any;
    status?: any;
    backlogTips?:any;
    avatar?:any;
}

const Graphic: React.FC<GraphicProps> = (props: GraphicProps) => {
    const {
        subtitle,
        handleClick,
        lineClamp = 2,
        textDetails,
        title,
        icon,
        iconType = '',
        operation = '',
        progress,
        status,
        backlogTips,
        avatar
    } = props;
    const [progressVal, setProgressVal] = useState(0);
    // const [progressEase,setProgressEase] = useState('')
    const bgMouseOver = () => {
        // setProgressEase('')
        setProgressVal(progress);
    };
    const bgMouseLeave = () => {
        setProgressVal(0);
    };
    const borderStatus = (status: any) => {
        return `rounded-[4px] border-l-[4px] ${
            status == 1 ? 'border-[#1B64F3]' : status == 2 ? 'border-[#52C41C]' : 'border-[#F04444]'
        } `;
    };
    // useEffect(()=>{
    //     setProgressVal(progress)
    //     // setProgressEase('width 0.5s ease-in')
    // },[])
    return (
        <div
            className={`flex  p-[10px] cursor-pointer overflow-hidden relative bg-[#fff] ${
                status !== undefined ? borderStatus(status) : 'graphicbox'
            }`}
            onClick={handleClick}
            onMouseEnter={() => {
                progress != undefined ? bgMouseOver() : '';
            }}
            onMouseLeave={() => {
                progress != undefined ? bgMouseLeave() : '';
            }}
        >
            {status !== undefined && (
                <div
                    style={{ width: `${progressVal}%`, transition: 'width 0.5s ' }}
                    className={`absolute bottom-0 left-0 top-0 bottom-0 h-full ${
                        status == 1
                            ? 'bg-[#1B64F3]/[.03]'
                            : status == 2
                            ? 'bg-[#52c41c]/[.05]'
                            : 'bg-[#FAFAFA]'
                    } `}
                ></div>
            )}
            <div className="flex gap-x-[20px] w-full relative z-20">
                <div className="shrink-0 flex gap-x-[7px] items-center" style={{ fontSize: 0 }}>
                    {/* <Avatar size={40} className='w-[40px] h-[40px] rounded-[6px]' style={{background:'#eee',}} icon={<div className='text-[22px]'>{icon?icon:<UserOutlined />}</div>} /> */}
                    {/* {status!==undefined&&<div className={`${status==1?'bg-[#1B64F3]':status==2?'bg-[#52C41C]':'bg-[#F04444]'} w-[4px] h-[62px] absolute top-0 left-0`}></div>} */}
                    <div className="w-[40px] h-[40px] rounded-[6px] flex items-center justify-center bg-[#F4F8F1] relative">
                        {
                            avatar?<img src={avatar} className='w-[40px] h-[40px] rounded-[6px]'  />:<img src={headportrait('single', icon)} className="w-[22px] h-[22px]" />
                        }
                        {iconType && (
                            <div
                                className="w-[16px] h-[16px] absolute top-[28px] left-[28px] flex items-center justify-center bg-[#fff] rounded-[3px]"
                                style={{ boxShadow: '0px 0px 4px 0px rgba(0,0,0,0.1)' }}
                            >
                                <img
                                    src={`/icons/${iconType}.svg`}
                                    alt=""
                                    className="w-[12px] h-[12px]"
                                />
                            </div>
                        )}
                    </div>
                </div>
                <div className="flex flex-1 min-w-0">
                    <div className="flex justify-center flex-col gap-y-[5px] flex-1 min-w-0">
                        <span
                            className="text-[12px] flex items-center"
                            style={{ color: '#213044' }}
                        >
                            <span className="truncate">{title}</span>
                            <span className="flex items-center flex-1">{subtitle}</span>
                        </span>
                        {/* WebkitLineClamp:lineClamp overflow-hidden text-ellipsis  line-clamp-1 break-all flex-1*/}
                        <span
                            className="text-[12px] max-w-full truncate"
                            style={{ color: '#999999' }}
                        >
                            {textDetails}
                        </span>
                    </div>
                </div>
                {backlogTips?backlogTips:<></>}
                {operation && (
                    <div className="flex items-center w-[24px]">
                        <span className="operation">{operation}</span>
                    </div>
                )}
                {progress != undefined && (
                    <div className="graphic_progress flex items-center pl-[30px]">
                        <Progress type="circle" percent={progress} size={29}></Progress>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Graphic;
