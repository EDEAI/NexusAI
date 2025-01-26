import React, { memo, useEffect, useRef, useState } from 'react';
import useChatroomStore from '@/store/chatroomstate'
import DraggablePanel from '@/components/Panel/DraggablePanel';
import {Spin} from 'antd';
import {MenuUnfoldOutlined,MenuFoldOutlined} from '@ant-design/icons'
import { getMeetingSummaryHistory } from '@/api/plaza';
import RunsMeetingSummary from './components/RunsMeetingSummary'
import RevisionsMeetingSummary from './components/RevisionsMeetingSummary'
import SummaryHistoryDom from './components/SummaryHistoryDom'

const MeetingSummary:React.FC<{id:any}>= params =>{
    const {id} = params;
    const [roomId,setRoomId] = useState('')
    const [contentShow,setContentShow] = useState(false);
    const [summaryHistory,setSummaryHistory] = useState([]);
    const [runboxShow,setRunboxShow] = useState(false);
    const [summaryShow,setSummaryShow] = useState(false);
    const [appRunId,setAppRunId] = useState('');
    const [packUp,setPackUp] = useState(false);
    const [boxLoading,setBoxLoading] = useState(false);
    const [inputShow,setinputShow] = useState(true);
    const scrollDom = useRef(null)
    const historyPage = useRef(1)
    const historyHeight = useRef(false)
    const isUpload = useRef(true);
    const totalPages = useRef(0)
    const [isLoad,setisLoad] = useState(false);

    const summaryParams = useChatroomStore(state=>state.summaryParams);
    const setSummaryParams = useChatroomStore(state=>state.setSummaryParams);

    const getSummaryHistory=async(isScroll=true,init=true)=>{
        if(totalPages.current!=0 && totalPages.current < historyPage.current){
            setisLoad(false)
            return
        }; 
        let resData=await getMeetingSummaryHistory({
            'chatroom_id':id,
            'page':historyPage.current,
            'page_size':10
        })
        if(resData.code == 0){
            if(resData?.data?.list && resData?.data?.list?.length){
                totalPages.current=resData?.data?.total_pages
                setSummaryHistory(pre=>{
                    return init? [...resData.data.list.reverse()] : [...resData.data.list.reverse(),...pre]
                });
                setContentShow(true);
                setisLoad(true)
                setTimeout(()=>{isUpload.current = true},300)
            }
            if(init){
                setTimeout(()=>{
                    scrollDom?.current?.scrollTo({top: 0});
                },200)
            }
            if(!isScroll){
                setRoomId(summaryParams.id)
                setSummaryParams({})
            }
        }
    }

    const historyLoad =async(e)=>{
        if( e.target.scrollHeight + (e.target.scrollTop - e.target.clientHeight) < 10 && isUpload.current){
            isUpload.current = false
            setisLoad(true)
            historyPage.current = historyPage.current+=1
            getSummaryHistory(true,false)
        }

    }
    
    useEffect(()=>{
        historyPage.current = 1
        getSummaryHistory()
    },[id])


    useEffect(()=>{
        if(summaryParams && summaryParams.id){
            setContentShow(true);
            if(!inputShow){
                setinputShow(true);
            }
            if(runboxShow){
                setRunboxShow(false);
            }
            if(packUp){
                setPackUp(false)
            }

            historyPage.current = 1

            setSummaryShow(true);
            
            getSummaryHistory(false);
           
            historyHeight.current = true
            
        }
    },[summaryParams])


    return (
        <>
            
            {
                contentShow ? 
                    <DraggablePanel
                        minWidth={400}
                        className={`relative h-full right-0 border-0 returned-0 px-[0] ${packUp?'translate-x-full flex-[0]':'translate-x-0'}`}
                    >
                        {boxLoading?<div className='h-full w-full absolute top-0 left-0 flex justify-center items-center z-[100] bg-[rgba(255,255,255,0.5)]'><Spin size="large" /></div>:<></>}
                        {
                            <>
                                <div onClick={()=>{ setPackUp(pre=>!pre)}} className={`
                                        ${!packUp?'right-[99%] top-[60px]':'right-[100%] top-[60px]' }
                                        history_packup
                                        hover:text-[#1B64F3]
                                        fixed w-[30px] h-[60px] bg-[rgba(255,255,255,1)] shadow-md flex justify-center items-center cursor-pointer z-[99]
                                    `}>
                                   {!packUp?<MenuUnfoldOutlined className='text-[18px]'/>:<MenuFoldOutlined className='text-[18px]'/>}
                                   
                                </div>
                                <div className={`h-full min-h-full overflow-y-auto flex flex-col-reverse scroll-smooth relative`} onScroll={historyLoad} ref={scrollDom}>
                                    <div>
                                        {summaryHistory.length?<SummaryHistoryDom id={id} runid={appRunId} scrollDom={scrollDom} list={summaryHistory} historyHeight={historyHeight.current}/>:<></>}
                                        <div className={`w-full px-4 h-full`} style={{minHeight:summaryShow?scrollDom?.current?.offsetHeight:''}}>
                                            <RevisionsMeetingSummary 
                                                setShow={setRunboxShow}
                                                inputShow={inputShow}
                                                setBoxLoading={setBoxLoading}
                                                setAppRunId={setAppRunId}
                                                scrollDom={scrollDom}
                                            />
                                            {runboxShow?<RunsMeetingSummary
                                                id={roomId} 
                                                runid={appRunId}
                                                setBoxLoading={setBoxLoading}
                                                scrollDom={scrollDom}
                                                setinputShow={setinputShow}
                                            />:<></>}
                                        </div>
                                    </div>
                                    {isLoad?<div className="text-center justify-center items-center flex"><Spin /></div>:<></>}
                                </div>
                            </>
                        }
                    </DraggablePanel>
                :<></>
            }
            
        </>
    )

}

export default memo(MeetingSummary)