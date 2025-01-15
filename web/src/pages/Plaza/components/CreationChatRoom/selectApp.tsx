import { getList } from '@/api/plaza';
import Scroll from '@/components/InfiniteScroll';
import { headportrait } from '@/utils/useUser';
import { CloseOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Col, Empty, Input, Row ,Radio } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import {getAppListByMode} from '@/api/workflow'
import TagSearch from '@/components/TagSearch';
interface params {
    show?: any;
    popupClose?: any;
    popupSave?: any;
    checkList?: any;
    zIndex?: any;
    nodetype?:any;
    radio?:any
}
const Content: React.FC<params> = param => {
    let { show, popupClose, popupSave, checkList, zIndex = '',nodetype='agent',radio} = param;
    const intl = useIntl();
    // Selected agent
    const checkItem = useRef([]);
    // Number of selected agents
    const [selectNumber, setSelectNumeber] = useState({ [`my_${nodetype}`]: 0,[`more_${nodetype}`]: 0,});

    const [selectType, setSelectType] = useState(3);
    // Whether more can be loaded
    const [ishasMore, setIshasMore] = useState(true);
    // Agent list
    const [myList, setMyList] = useState([]);
    // MyAgent list
    const [moreList, setMoreList] = useState([]);
    // Whether more can be loaded
    const [moreishasMore, setMoreIshasMore] = useState(true);
    // content
    const contentDom = useRef(null);
    //input value
    const [inputval,setInputVal] = useState('')
    //  parameters
    const parameters = useRef({
        page: 1,
        page_size: 40,
        search_type: 3,
        apps_name:'',
        tag_ids:''
    });

    const isMyList = () => {
        if (selectType == 3) {
            return myList && myList.length > 0 ? myList : [];
        } else {
            return moreList && moreList.length > 0 ? moreList : [];
        }
    };
    const handleChange = (e:any) => {
        setSelectType(e.target.value);
        // setInputVal('');
        parameters.current.search_type = e.target.value;
        // parameters.current.apps_name='';
        // parameters.current.tag_ids='';
        getList(parameters.current,true)
    };
    const getList = async (data: any, isInit = false) => {
        if(isInit){
            parameters.current.page=1;
        }
        const res = await getAppListByMode(nodetype, data);
        if (res?.code == 0) {
            res?.data?.list.forEach((item: any) => {
                item.check = isCheckAagent(item);
            });
            if (data.search_type == 3) {
                isInit
                    ? setMyList([...res?.data?.list])
                    : setMyList([...myList, ...res?.data?.list]);
                setIshasMore(res?.data?.total_pages > parameters?.current?.page);
                selectMobNumber(`my_${nodetype}`);
            } else {
                isInit
                    ? setMoreList([...res?.data?.list])
                    : setMoreList([...moreList, ...res?.data?.list]);
                setMoreIshasMore(res?.data?.total_pages > parameters?.current?.page);
                selectMobNumber(`more_${nodetype}`);
            }
        }
    };
    const setSeachInput = (e: any) => {
        parameters.current.apps_name = e.target.value;
        parameters.current.page = 1;
        getList(parameters.current, true);
    };
    const selectMobNumber = (key: any) => {
        let myCheckNumber = 0
        if(checkItem.current.length){
            myCheckNumber = checkItem.current.filter(items => items.type == key).length;
        }
        setSelectNumeber(pre => {
            pre[key] = myCheckNumber;
            return pre;
        });
    };
    const radioCheckItem=(type: any, item: any)=>{
        item.type = type==3?`my_${nodetype}`:`more_${nodetype}`;
        checkItem.current = [item];
        if (type == 3) {
            setMyList(pre =>  pre.map(i => ({...i,check: i.app_id === item.app_id})));
            setMoreList(pre => pre.map(i=>({...i,check:false})))
        } else {
            setMoreList(pre => pre.map(i => ({...i,check: i.app_id === item.app_id})));
            setMyList(pre => pre.map(i=>({...i,check:false})))
        }
        selectMobNumber(`my_${nodetype}`);
        selectMobNumber(`more_${nodetype}`);
    }
    const addCheckItem = (type: any, item: any) => {
        item.type = type==3?`my_${nodetype}`:`more_${nodetype}`;
        let res = checkItem.current.filter(items => items.app_id == item.app_id);
        checkItem.current.forEach((item, index) => {
            if (item.app_id == res[0]?.app_id) {
                checkItem.current.splice(index, 1);
            }
        });
        checkItem.current = res.length ? [...checkItem.current] : [...checkItem.current, item];
        if (type == 3) {
            setMyList(pre=>{
                return pre.map(i => {
                    if (i.app_id === item.app_id) {
                        return { ...i, check: !i.check };
                    }
                    return i;
                });
            });
            selectMobNumber(`my_${nodetype}`);
        } else {
            setMoreList(pre=>{
                return pre.map(i => {
                    if (i.app_id === item.app_id) {
                        return { ...i, check: !i.check };
                    }
                    return i;
                });
            });
            selectMobNumber(`more_${nodetype}`);
        }
    };
    const isCheckAagent = (item: any) => {
        if(radio && checkItem.current.length>1){
            return 0
        }
        return checkItem.current.filter(i => i.app_id == item.app_id).length;
    };
    const Cancel = () => {
        popupClose();
        checkItem.current = [];
        setMoreList([]);
        setSelectType(3);
        setSelectNumeber({
            my_agent: 0,
            more_agent: 0,
        });
    };
   // Save popup
    const Save = () => {
        popupSave({
            checkItem: checkItem.current,
        });
        Cancel();
    };
    useEffect(() => {
        if (show) {
            // showPopup()
            if (checkList.length) {
                checkItem.current = [...checkList];
            }
            parameters.current.apps_name = '';
            getList({
                ...parameters.current,
                search_type:3
            }, true);
            getList({
                ...parameters.current,
                search_type:2
            }, true);
        }
    }, [show]);

    return (
        show?<div
            ref={contentDom}
            style={zIndex ? { zIndex: zIndex } : { zIndex: 30 }}
            className='transition  w-full h-full fixed top-[0] left-[0] bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-30"'
        >
            <div className="w-[980px] h-[646px] bg-[#fff] rounded-[6px] transition">
                <div className="flex flex-col h-full">
                    <div
                        className="text-[16px] flex items-center p-[20px]"
                        style={{ borderBottom: '1px solid #ebebeb' }}
                    >
                        <span className="flex-1 text-[14px] font-[500] text-[#213044]">
                            {intl.formatMessage({ id: `app.check_${nodetype}_popup.title` })}
                        </span>
                        <CloseOutlined
                            className="text-[16px] cursor-pointer"
                            onClick={Cancel}
                        />
                    </div>
                    <div className="pt-[20px] flex-1 min-h-[0]">
                        <div className="flex items-center pt-[0] p-[20px]">
                            <span className="text-[#999]">
                                {intl.formatMessage({ id: `app.check_${nodetype}_popup.chenck_text` })}：
                            </span>
                            <div className="flex items-center gap-x-[12px]">
                                <span className="text-[#213044] text-[14px]">
                                    {intl.formatMessage({ id: `app.check_${nodetype}_popup.select_1` })}:{' '}
                                    {selectNumber[`my_${nodetype}`]}
                                </span>
                                <span className="text-[#213044] text-[14px]">
                                    {intl.formatMessage({ id: `app.check_${nodetype}_popup.select_2` })}:{' '}
                                    {selectNumber[`more_${nodetype}`]}
                                </span>
                            </div>
                        </div>
                        <div className="flex gap-x-[20px] pt-[0] p-[20px]">
                            <Radio.Group
                                    onChange={ handleChange }
                                    defaultValue={'3'}
                                    size='large'
                                >
                                <Radio.Button value="3" >
                                    <span className='text-[14px]'>{intl.formatMessage({ id: `app.check_${nodetype}_popup.select_1` })}</span>
                                </Radio.Button>
                                <Radio.Button value="2" >
                                    <span className='text-[14px]'>{intl.formatMessage({ id: `app.check_${nodetype}_popup.select_2` })}</span>
                                </Radio.Button>
                            </Radio.Group>
                            <Input
                                className="w-[320px] text-[14px]"
                                style={{fontSize:'14px !important'}}
                                onPressEnter={setSeachInput}
                                size="large"
                                placeholder={intl.formatMessage({
                                    id: `app.check_${nodetype}_popup.search`,
                                })}
                                onChange={(e) => setInputVal(e.target.value)}
                                value={inputval}
                                prefix={
                                    <img
                                        src="/icons/search_icon.svg"
                                        className="w-[16px] h-[16px] mr-[10px]"
                                    />
                                }
                            />
                            <TagSearch
                                allowClear
                                onChange={(e)=>{
                                    parameters.current.tag_ids = e?e.join(','):'';
                                    parameters.current.page = 1;
                                    getList(parameters.current,true)
                                }}
                                showAddButton={false}
                                size='large'
                                className='w-[260px]'
                                listStyle="horizontal"
                            ></TagSearch>
                        </div>
                        <div
                            className="overflow-y-auto  px-[20px]"
                            id="agentScroll"
                            style={{ height: 'calc(100% - 100px)' }}
                        >
                            <Scroll
                                dataLength={
                                    selectType == 3
                                        ? myList.length
                                        : moreList.length
                                }
                                elid={'agentScroll'}
                                ishasMore={
                                    selectType == 3 ? ishasMore : moreishasMore
                                }
                                upSlide={() => {
                                    parameters.current.page+=1;
                                    getList(parameters.current);
                                }}
                            >
                                <div className="w-full overflow-x-hidden">
                                    <Row gutter={[15, 15]}>
                                        {isMyList() && isMyList().length ? (
                                            isMyList().map((item: any, index: any) => (
                                                <Col span={6} key={item.app_id}>
                                                    <div
                                                        className={`bg-[#fff] flex gap-x-[20px] p-[10px] cursor-pointer border-solid border-[1px] rounded-[4px] ${
                                                            !item.check
                                                                ? 'border-[#eee]'
                                                                : 'border-[#1B64F3]'
                                                        }`}
                                                        onClick={() => {
                                                            radio?radioCheckItem(
                                                                    selectType,
                                                                    item,
                                                                ): addCheckItem(
                                                                selectType,
                                                                item,
                                                            );
                                                        }}
                                                    >
                                                        <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] relative flex items-center justify-center shrink-0">
                                                            <img
                                                                src={headportrait(
                                                                    'single',
                                                                    item.icon,
                                                                )}
                                                                alt=""
                                                                className="w-[20px]  h-[20px]"
                                                            />
                                                            {/* <div className='w-[16px]  h-[16px] bg-[#fff] absolute bottom-[-2px] right-[-2px]'>
                                                                    <img src="/icons/robot_icon.svg" alt="" className='w-[12px]  h-[12px]'/>
                                                                </div> */}
                                                        </div>
                                                        <div className="flex flex-col gap-y-[5px] justify-center flex-1 min-w-[0]">
                                                            <div className="text-[#213044] text-[12px] font-[500] w-full truncate">
                                                                {item.name}
                                                            </div>
                                                            <div className="text-[#999] text-[12px] w-full truncate">
                                                                {item.description}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </Col>
                                            ))
                                        ) : (
                                            <div className="w-full h-[380px] flex justify-center items-center">
                                                <Empty
                                                    style={{ margin: '0px', fontSize: '16px' }}
                                                    imageStyle={{
                                                        width: '60px',
                                                        margin: '0 auto',
                                                        marginBottom: '2px',
                                                    }}
                                                    description={intl.formatMessage({
                                                        id: 'app.dashboard.None',
                                                    })}
                                                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                                                ></Empty>
                                            </div>
                                        )}
                                    </Row>
                                </div>
                                {/* Empty */}
                            </Scroll>
                        </div>
                    </div>
                    <div
                        className="p-[20px] flex gap-x-[20px] justify-end"
                        style={{ borderTop: '1px solid #e8e8e8' }}
                    >
                        <Button
                            className="text-[14px] text-[#213044] w-[88px] h-[40px]"
                            style={{ border: '1px solid #D8D8D8' }}
                            onClick={Cancel}
                        >
                            {intl.formatMessage({ id: `app.check_${nodetype}_popup.cancel` })}
                        </Button>
                        <Button
                            type="primary"
                            className="bg-[#1B64F3] rounded-[4px] w-[88px] h-[40px]"
                            htmlType="submit"
                            onClick={Save}
                        >
                            {intl.formatMessage({ id: `app.check_${nodetype}_popup.save` })}
                        </Button>
                    </div>
                </div>
            </div>
        </div>:<></>
    );
};

export default Content;
