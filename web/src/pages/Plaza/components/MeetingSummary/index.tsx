import React, { memo, useEffect, useRef, useState } from 'react';
import useChatroomStore from '@/store/chatroomstate'
import DraggablePanel from '@/components/Panel/DraggablePanel';
import {Spin} from 'antd';
import {VerticalLeftOutlined,VerticalRightOutlined,} from '@ant-design/icons'
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
    const historyHeight = useRef(false)

    const getSummaryHistory=async(isScroll=true)=>{
        let resData=await getMeetingSummaryHistory({
            'chatroom_id':id,
            'page':1,
            'page_size':9999
        })
        if(resData.code == 0){
            if(resData?.data?.list && resData?.data?.list?.length){
                setSummaryHistory(resData.data.list);
                setContentShow(true);
            }
            if(!isScroll){
                setTimeout(()=>{
                    scrollDom?.current?.scrollTo({top: scrollDom.current.scrollHeight});

                },200)
                setRoomId(summaryParams.id)
                setSummaryParams({})
            }
        }
    }
    
    useEffect(()=>{
        getSummaryHistory()
    },[id])

    const summaryParams = useChatroomStore(state=>state.summaryParams);
    const setSummaryParams = useChatroomStore(state=>state.setSummaryParams);
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

            setSummaryShow(true);
            
            getSummaryHistory(false);
           
            historyHeight.current = true
            
        }
    },[summaryParams])

    useEffect(()=>{
        console.log(boxLoading);
        
    },[boxLoading])

    return (
        <>
            
            {
                contentShow ? 
                    <DraggablePanel
                        minWidth={400}
                        className={`relative h-full right-0 border-0 returned-0 px-[0] ${packUp?'translate-x-full flex-[0]':''}`}
                    >
                        {boxLoading?<div className='h-full w-full absolute top-0 left-0 flex justify-center items-center z-[100] bg-[rgba(255,255,255,0.5)]'><Spin size="large" /></div>:<></>}
                        {
                            <>
                                <div onClick={()=>{ setPackUp(pre=>!pre)}} className={`
                                        ${!packUp?'right-[6px] top-[60px]':'right-[100%] top-[4px]' }
                                        fixed w-[40px] h-[40px]  flex justify-center items-center cursor-pointer z-[99]
                                    `}>
                                   {!packUp?<VerticalLeftOutlined className='text-[20px]'/>:<VerticalRightOutlined className='text-[20px]'/>}
                                </div>
                                <div className={`h-full min-h-full overflow-y-auto flex flex-col-reverse scroll-smooth`}  ref={scrollDom}>
                                    <div>
                                        {summaryHistory.length?<SummaryHistoryDom scrollDom={scrollDom} list={summaryHistory} historyHeight={historyHeight.current}/>:<></>}
                                        <div className={`w-full px-4 h-full`} style={{minHeight:summaryShow?scrollDom?.current?.offsetHeight:''}}>
                                            <RevisionsMeetingSummary 
                                                setShow={setRunboxShow}
                                                inputShow={inputShow}
                                                setBoxLoading={setBoxLoading}
                                                setAppRunId={setAppRunId}
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