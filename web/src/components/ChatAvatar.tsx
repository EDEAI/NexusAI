import { headportrait } from '@/utils/useUser';
import React,{memo} from 'react';

interface params {
    width?: any;
    bg?: any;
    rounded?: any;
    data?: any;
    imgWidth?:any;
}
const AvatarContent: React.FC<params> = param => {
    let { width="40px", bg="#F4F8F1", rounded="6px", data, imgWidth='18px'} = param;
    if(data.avatar){
      imgWidth=width
    }
    return(
        <div className={`w-[${width}] h-[${width}] bg-[${bg}] rounded-[${rounded}] relative flex items-center justify-center shrink-0`}>
            <img
                src={data.avatar?data.avatar:headportrait(
                    'single',
                    data.icon,
                )}
                className={`w-[${imgWidth}]  h-[${imgWidth}]`}
            />
        </div>
    )
}
export default memo(AvatarContent);
