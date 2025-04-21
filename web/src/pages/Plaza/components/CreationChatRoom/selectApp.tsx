
import Scroll from '@/components/InfiniteScroll';
import { headportrait } from '@/utils/useUser';
import Avatar from '@/components/ChatAvatar';
import { CloseOutlined,DeleteOutlined  } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Col, Empty, Input, Row ,Radio,Spin} from 'antd';
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
    const checkItems = useRef([]);
    // check current
    const [checkCurrent,setCheckCurrent] = useState([]) 
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
    const getSelectNumber = (type)=>{return checkItems.current.filter(v=>v.type==type).length}
    // Number of selected agents
    const selectNumber = { [`my_${nodetype}`]:getSelectNumber(`my_${nodetype}`),[`more_${nodetype}`]:getSelectNumber(`more_${nodetype}`)};
    
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
            } else {
                updateList(moreList, setMoreList);
                setMoreIshasMore(res.data.total_pages > parameters.current.page);
            }
        }
    };
    const setSeachInput = (e: any) => {
        parameters.current.apps_name = e.target.value;
        parameters.current.page = 1;
        getList(parameters.current, true);
    };
    const radiocheckMyItem = (type, item) => {
        const isTypeThree = type == 3;
        item.type = isTypeThree ? `my_${nodetype}` : `more_${nodetype}`;
        checkItems.current = [item]
        const updateList = (list, shouldCheck) => 
            list.map(i => ({ ...i, check: shouldCheck(i.app_id) }));
    
        setMyList(pre => updateList(pre, id => id == item.app_id && isTypeThree));
        setMoreList(pre => updateList(pre, id => id == item.app_id && !isTypeThree));
    };
    const addcheckMyItem = (type, item) => {
        item.type = type == 3 ? `my_${nodetype}` : `more_${nodetype}`;
        const currentCheckList = checkItems.current;
        const res = currentCheckList.find(currItem => currItem.app_id == item.app_id);
        if (!res) {
            currentCheckList.push(item);
        } else {
            currentCheckList.splice(currentCheckList.findIndex(items=>items.app_id == item.app_id), 1);
        }
        const updateList = (list, id) => list.map(i => ({ ...i, check: i.app_id == id ? !i.check : i.check }));
        type == 3 ? setMyList(pre => updateList(pre, item.app_id)) : setMoreList(pre => updateList(pre, item.app_id));
    };
    const isCheckAagent = (item: any,type) => {
        const currentCheckList = checkItems.current;
        if(radio && currentCheckList.length>1){
            return 0
        }
        return currentCheckList.some(i => i.app_id == item.app_id)?1:0;
    };
    const Cancel = () => {
        popupClose();
        checkItems.current = [];
        setCheckCurrent([])
        setMoreList([]);
        setSelectType(3);
    };
   // Save popup
    const Save = () => {
        popupSave({
            checkItem: [...checkItems.current],
        });
        Cancel();
    };
    const checkAll=()=>{
        const isTypeThree = parameters.current.search_type == 3;
        const list = isTypeThree ? myList : moreList;
        const typePrefix = isTypeThree ? 'my' : 'more';
        let addArray = list.map(item => ({
            ...item,
            type: `${typePrefix}_${nodetype}`
        }))
        let addCheck = checkItems.current.filter(v=>v.type != `${typePrefix}_${nodetype}`)
        checkItems.current = [...addCheck,...addArray]
        const updateList = list.map(item => ({
            ...item,
            check: 1
        }));
        isTypeThree?setMyList(() => updateList):setMoreList(() => updateList);
    }
    useEffect(() => {
        if (show) {
            // showPopup()
            parameters.current.search_type = 3
            parameters.current.apps_name = '';
            // setCheckCurrent([])
            if (checkList.length) {
                checkItems.current = [...checkList];
                setCheckCurrent([...checkList])
            }
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

    useEffect(()=>{
        setCheckCurrent([...checkItems.current])
    },[myList,moreList]) 

    const checkCurrentUpdata=useRef(false)
    useEffect(()=>{
        if(checkItems.current.length !== checkCurrent.length && checkCurrentUpdata.current){
            const updateListChecks = (list, checkItems) => {
                return list.map(item => ({
                    ...item,
                    check: checkItems.some(e => item.app_id === e.app_id) ? 1 : 0
                }));
            };
            
            checkItems.current = [...checkCurrent];
            const mylist = checkCurrent.filter(item => item.type === "my_agent");
            const morelist = checkCurrent.filter(item => item.type === "more_agent");
            
            setMyList(pre => updateListChecks(pre, mylist));
            setMoreList(pre => updateListChecks(pre, morelist));

            checkCurrentUpdata.current = false
        }
    },[checkCurrent])
    

   const delContrast = (delarr:any) =>{
        checkCurrentUpdata.current = true
        setCheckCurrent(pre=>{
            return pre.filter(item => delarr.some(e=>item.app_id!=e.app_id));
        })
        
   }
    return (
        show?<div
            ref={contentDom}
            style={zIndex ? { zIndex: zIndex } : { zIndex: 30 }}
            className='transition  w-full h-full fixed top-[0] left-[0] bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-30"'
        >
            <div className="w-[980px] h-[646px] bg-[#fff] rounded-[6px] transition">
                <div className="flex flex-col h-full w-full">
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
                    <div className='flex flex-1 overflow-x-hidden w-full min-w-0'>
                        <div className="pt-[20px] h-full flex-1 min-w-0">
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
                                    className="w-[320px] text-[14px] flex-1"
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
                                    className='min-w-[240px] flex-1'
                                    listStyle="horizontal"
                                ></TagSearch>
                            </div>
                            <div
                                className="overflow-y-auto  px-[20px]"
                                id="agentScroll"
                                style={{ height: 'calc(100% - 100px)' }}
                            >
                                {myList.length || moreList.length?<></>:<div className='h-full w-full absolute top-0 left-0 flex justify-center items-center z-[100] bg-[rgba(255,255,255,0.5)]'>
                                    <Spin size="large" />
                                </div>}
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
                                                    <Col span={checkCurrent.length && !radio?8:6} key={item.app_id}>
                                                        <div
                                                            className={`bg-[#fff] flex gap-x-[20px] p-[10px] cursor-pointer border-solid border-[1px] rounded-[4px] ${
                                                                !item.check
                                                                    ? 'border-[#eee]'
                                                                    : radio?'border-[#1b64f3]':'border-gray-100'
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
                                                            {/* <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] relative flex items-center justify-center shrink-0">
                                                                <img
                                                                    src={headportrait(
                                                                        'single',
                                                                        item.icon,
                                                                    )}
                                                                    alt=""
                                                                    className="w-[20px]  h-[20px]"
                                                                />
                                                            </div> */}
                                                            <Avatar data={item} imgWidth={'20px'}/>
                                                            <div className="flex flex-col gap-y-[5px] justify-center flex-1 min-w-[0]">
                                                                <div className={`text-[12px] font-[500] w-full truncate ${
                                                                !item.check
                                                                    ? 'text-[#213044]'
                                                                    : radio?'text-[#213044]':'text-gray-300'
                                                            }`}>
                                                                    {item.name}
                                                                </div>
                                                                <div className={`text-[12px] w-full truncate ${!item.check
                                                                    ? 'text-[#999]'
                                                                    : radio?'text-[#999]':'text-gray-300'}`}>
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
                        {!radio && (myList.length || moreList.length) && checkCurrent && checkCurrent.length ? 
                        <div className='h-full flex flex-col'  style={{boxShadow:'rgba(0, 0, 0, 0.1) 0px 0px 3px 0px'}}>
                            <div className='py-[10px] px-[10px] text-[14px]'>{intl.formatMessage({id:'app.check_popup.add'})}{intl.formatMessage({id:`app.check_${nodetype}_popup.name`})}</div>
                            <div className='w-[260px]  overflow-y-auto flex-1 min-w-0 min-h-0'>
                                <div className='flex gap-[6px] p-4 pt-[6px] flex-wrap w-full'>
                                    { checkCurrent.map(item=>(
                                        <div className='w-full cursor-pointer relative' key={item.app_id}>
                                            <div
                                                className="flex items-center gap-x-[5px] bg-[#FAFAFA] transition p-[10px] slider_agent_box"
                                            >
                                                <div className="flex gap-x-[15px] flex-1 min-w-[0]">
                                                    {/* <div className="w-[40px] h-[40px] bg-[#F4F8F1] rounded-[6px] flex items-center justify-center shrink-0">
                                                        <img
                                                            src={headportrait(
                                                                'single',
                                                                item.icon,
                                                            )}
                                                            alt=""
                                                            className="w-[18px]  h-[18px]"
                                                        />
                                                    </div> */}
                                                     <Avatar data={item}/>
                                                    <div className="flex flex-col gap-y-[5px] justify-center flex-1 min-w-[0]">
                                                        <span className="text-[#213044] text-[12px] font-[500] truncate w-full">
                                                            {item.name}
                                                        </span>
                                                        <span className="text-[#999999] text-[12px] truncate">
                                                            {item.description}
                                                        </span>
                                                    </div>
                                                </div> 
                                            </div> 
                                            <div className='text-[#f73131] transition text-[14px] absolute top-[6px] right-[6px]'><DeleteOutlined  /></div>
                                            <div className='hover:opacity-100 opacity-0 transition absolute w-full h-full flex items-center justify-center top-0 left-0 bg-[rgba(255,255,255,0.8)]'onClick={()=>{
                                                delContrast([item])
                                            }}>
                                                <div className='text-[#1b64f3] transition text-[24px]'><DeleteOutlined  /></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                        :<></>}
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
