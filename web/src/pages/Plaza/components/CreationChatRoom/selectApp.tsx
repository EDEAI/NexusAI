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
    const checkMyItem = useRef([]);
    const checkMoreItem = useRef([]);
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
        page_size: 999999,
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
    const getList = async (data, isInit = false) => {
        if (isInit) {
            parameters.current.page = 1;
        }
        const res = await getAppListByMode(nodetype, data);
        if (res?.code == 0) {
            const newList = res.data.list.map(item => ({
                ...item,
                check: isCheckAagent(item,data.search_type)
            }));
    
            const updateList = (list, setList) => {
                setList(isInit ? [...newList] : [...list, ...newList]);
            };
            if (data.search_type == 3) {
                updateList(myList, setMyList);
                setIshasMore(res.data.total_pages > parameters.current.page);
                selectMobNumber(`my_${nodetype}`, data.search_type);
            } else {
                updateList(moreList, setMoreList);
                setMoreIshasMore(res.data.total_pages > parameters.current.page);
                selectMobNumber(`more_${nodetype}`, data.search_type);
            }
        }
    };
    const setSeachInput = (e: any) => {
        parameters.current.apps_name = e.target.value;
        parameters.current.page = 1;
        getList(parameters.current, true);
    };
    const selectMobNumber = (key: any,type) => {
        let myCheckNumber = 0;
        if(type == 3){
            if(checkMyItem.current.length){
                myCheckNumber = checkMyItem.current.length;
            }
        }else{
            if(checkMoreItem.current.length){
                myCheckNumber = checkMoreItem.current.length;
            }
        }
        setSelectNumeber(pre => {
            pre[key] = myCheckNumber;
            return pre;
        });
    };
    const radiocheckMyItem = (type, item) => {
        const isTypeThree = type == 3;
        item.type = isTypeThree ? `my_${nodetype}` : `more_${nodetype}`;
        checkMyItem.current = isTypeThree ? [item] : [];
        checkMoreItem.current = isTypeThree ? [] : [item];
    
        const updateList = (list, shouldCheck) => 
            list.map(i => ({ ...i, check: shouldCheck(i.app_id) }));
    
        setMyList(pre => updateList(pre, id => id == item.app_id && isTypeThree));
        setMoreList(pre => updateList(pre, id => id == item.app_id && !isTypeThree));
    
        selectMobNumber(`my_${nodetype}`,3);
        selectMobNumber(`more_${nodetype}`,2);
    };
    const addcheckMyItem = (type, item) => {
        item.type = type == 3 ? `my_${nodetype}` : `more_${nodetype}`;
        const currentCheckList = type == 3 ? checkMyItem.current : checkMoreItem.current;
        const res = currentCheckList.filter(currItem => currItem.app_id !== item.app_id);
        if (res.length == currentCheckList.length) {
            currentCheckList.push(item);
        } else {
            currentCheckList.splice(currentCheckList.indexOf(item), 1);
        }
    
        const updateList = (list, id) => list.map(i => ({ ...i, check: i.app_id == id ? !i.check : i.check }));
        type == 3 ? setMyList(pre => updateList(pre, item.app_id)) : setMoreList(pre => updateList(pre, item.app_id));
    
        selectMobNumber(type == 3 ? `my_${nodetype}` : `more_${nodetype}`,type);
    };
    const isCheckAagent = (item: any,type) => {
        const currentCheckList = type == 3 ? checkMyItem.current : checkMoreItem.current;
        if(radio && currentCheckList.length>1){
            return 0
        }
        return currentCheckList.filter(i => i.app_id == item.app_id).length;
    };
    const Cancel = () => {
        popupClose();
        checkMyItem.current = [];
        checkMoreItem.current = [];
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
            checkItem: [...checkMyItem.current,...checkMoreItem.current],
        });
        Cancel();
    };
    const checkAll=()=>{
        const isTypeThree = parameters.current.search_type == 3;
        const list = isTypeThree ? myList : moreList;
        const typePrefix = isTypeThree ? 'my' : 'more';
        const currentItem = isTypeThree ? checkMyItem : checkMoreItem
        currentItem.current = list.map(item => ({
            ...item,
            type: `${typePrefix}_${nodetype}`
        }));
    
        const updateList = list.map(item => ({
            ...item,
            check: 1
        }));
    
        if (isTypeThree) {
            setMyList(() => updateList);
        } else {
            setMoreList(() => updateList);
        }
        selectMobNumber(`${typePrefix}_${nodetype}`, parameters.current.search_type);
    }
    useEffect(() => {
        if (show) {
            // showPopup()
            parameters.current.search_type = 3
            if (checkList.length) {
                let checkarr = checkList.filter(item=>item.type==`my_${nodetype}`);
                let checMorekarr = checkList.filter(item=>item.type==`more_${nodetype}`);
                checkMyItem.current = [...checkarr];
                checkMoreItem.current = [...checMorekarr]
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
                                                            radio?radiocheckMyItem(
                                                                    selectType,
                                                                    item,
                                                                ): addcheckMyItem(
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
                       { 
                        !radio?<div className='flex-1'>
                            <Button
                                // type="text"
                                // className="bg-[#1B64F3] rounded-[4px]"
                                htmlType="submit"
                                onClick={checkAll}
                                // size='small'
                            >
                                {intl.formatMessage({id:'app.check_popup.check'})}
                            </Button>
                        </div>:<></>
                        }
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
