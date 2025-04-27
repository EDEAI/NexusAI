/*
 * @LastEditors: biz
 */
import { headportrait } from '@/utils/useUser';
import { memo } from 'react';

interface ChildProps {
    agentList: any;
    size?: 'sm' | 'md' | 'lg';
    rounded?: boolean;
}

export default memo(({ agentList, size = 'sm', rounded = false }: ChildProps) => {
    const imgList = agentList?.map((item: any) => {
        if (item.avatar) {
            return item.avatar;
        } else {
            return headportrait(
                'single',
                item.icon,
            );
        }
    });

    
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-12 h-12',
        lg: 'w-16 h-16'
    };

    
    const avatarSizeClasses = {
        sm: 'w-[47%] h-[47%]',
        md: 'w-[47%] h-[47%]',
        lg: 'w-[47%] h-[47%]'
    };

   
    const renderAvatars = () => {
        const count = imgList?.length || 0;
        
        if (!count || !imgList) {
            return <div className={`bg-gray-200 w-full h-full ${rounded ? 'rounded-full' : ''}`}></div>;
        }

        if (count === 1) {
            return (
                <div className={`w-full h-full overflow-hidden ${rounded ? 'rounded-full' : ''}`}>
                    <img src={imgList[0]} alt="头像" className="w-full h-full object-cover" />
                </div>
            );
        }

        if (count === 2) {
            return (
                <div className="w-full h-full flex flex-wrap">
                    <div className="w-1/2 h-full pr-[2%]">
                        <img 
                            src={imgList[0]} 
                            alt="头像" 
                            className={`w-full h-full object-cover ${rounded ? 'rounded-l-full' : ''}`} 
                        />
                    </div>
                    <div className="w-1/2 h-full pl-[2%]">
                        <img 
                            src={imgList[1]} 
                            alt="头像" 
                            className={`w-full h-full object-cover ${rounded ? 'rounded-r-full' : ''}`} 
                        />
                    </div>
                </div>
            );
        }

        if (count === 3) {
            return (
                <div className="w-full h-full flex flex-wrap">
                    <div className="w-1/2 h-full pr-[2%] flex items-center justify-center">
                        <img 
                            src={imgList[0]} 
                            alt="头像" 
                            className={`w-full h-full object-cover ${rounded ? 'rounded-l-full' : ''}`} 
                        />
                    </div>
                    <div className="w-1/2 h-full pl-[2%] flex flex-col">
                        <div className="h-1/2 pb-[2%]">
                            <img 
                                src={imgList[1]} 
                                alt="头像" 
                                className={`w-full h-full object-cover ${rounded ? 'rounded-tr-full' : ''}`} 
                            />
                        </div>
                        <div className="h-1/2 pt-[2%]">
                            <img 
                                src={imgList[2]} 
                                alt="头像" 
                                className={`w-full h-full object-cover ${rounded ? 'rounded-br-full' : ''}`} 
                            />
                        </div>
                    </div>
                </div>
            );
        }

        if (count === 4) {
            return (
                <div className="w-full h-full flex flex-wrap">
                    {imgList.slice(0, 4).map((img: string, index: number) => (
                        <div 
                            key={index} 
                            className={`${avatarSizeClasses[size]} p-[3%] ${
                                index === 0 ? 'pl-0 pt-0' : 
                                index === 1 ? 'pr-0 pt-0' : 
                                index === 2 ? 'pl-0 pb-0' : 'pr-0 pb-0'
                            }`}
                        >
                            <img 
                                src={img} 
                                alt="头像" 
                                className={`w-full h-full object-cover ${
                                    rounded ? (
                                        index === 0 ? 'rounded-tl-full' : 
                                        index === 1 ? 'rounded-tr-full' : 
                                        index === 2 ? 'rounded-bl-full' : 'rounded-br-full'
                                    ) : ''
                                }`}
                            />
                        </div>
                    ))}
                </div>
            );
        }

        // 5个或更多头像 (最多显示9个)
        const displayImages = imgList.slice(0, 9);
        const gridItems = [];
        
        for (let i = 0; i < Math.min(9, displayImages.length); i++) {
            gridItems.push(
                <div 
                    key={i} 
                    className="w-1/3 h-1/3"
                    style={{ padding: '1.5%' }}
                >
                    <img 
                        src={displayImages[i]} 
                        alt="头像" 
                        className="w-full h-full object-cover"
                    />
                </div>
            );
        }
        
        return (
            <div className="w-full h-full flex flex-wrap">
                {gridItems}
            </div>
        );
    };

    return (
        <div className={`${sizeClasses[size]} overflow-hidden bg-white ${rounded ? 'rounded-full' : ''}`}>
            {renderAvatars()}
        </div>
    );
});
