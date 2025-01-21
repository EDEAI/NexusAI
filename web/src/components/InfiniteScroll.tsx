/*
 * @LastEditors: biz
 */
import InfiniteScroll from 'react-infinite-scroll-component';
// import { LoadingOutlined} from '@ant-design/icons';
import Footer from '@/components/Footer/index';
import { Spin } from 'antd';


interface scrollObject {
    dataLength?: number;
    elid?: string;
    children?: any;
    ishasMore?: any;
    upSlide?: any;
    isFooter?: any;
    pageNumber?: any;

}

const Scroll: React.FC<scrollObject> = (props: scrollObject) => {
    const { children, elid, dataLength, ishasMore, upSlide, isFooter, pageNumber = 2 } = props;
    return (
        <div className="w-full h-full flex flex-col">
            <InfiniteScroll
                dataLength={dataLength}
                scrollableTarget={elid}
                next={upSlide}
                hasMore={ishasMore}
                loader={
                    <div className="flex justify-center h-[60px] items-center">
                        {pageNumber > 1 ? <Spin /> : <></>}
                    </div>
                }
            >
                {children}
            </InfiniteScroll>
            {isFooter && (
                <div className="mt-[30px] flex-1 flex " style={{ alignItems: 'flex-end' }}>
                    <Footer className="relative"></Footer>
                </div>
            )}
        </div>
    );
};

export default Scroll;
