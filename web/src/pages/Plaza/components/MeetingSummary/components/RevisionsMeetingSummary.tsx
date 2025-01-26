import { getMeetingSinglesummary, getMeetingsummary,getMeetingSummaryHistorySingle } from '@/api/plaza';
import useChatroomStore from '@/store/chatroomstate';
import useSocketStore from '@/store/websocket';
import { useIntl } from '@umijs/max';
import { Button, Input, Spin } from 'antd';
import { RedoOutlined } from '@ant-design/icons';
import React, { memo, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';

interface params {
    setShow: any;
    inputShow: any;
    setBoxLoading: any;
    setAppRunId: any;
    scrollDom:any;
}

const Redirect: React.FC<{ id: any; message: any }> = memo(parmas => {
    let { id, message } = parmas;
    let intl = useIntl();
    const setSummaryClick = useChatroomStore(state => state.setSummaryClick);
    const [disabled, setDisabled] = useState(true);
    const summaryClick = useChatroomStore(state => state.summaryClick);
    const setSummaryParams = useChatroomStore(state => state.setSummaryParams);
    useEffect(() => {
        setDisabled(summaryClick);
    }, [summaryClick]);
    return (
        <div className="flex flex-row-reverse">
            <Button
                type="primary"
                className="bg-[#1B64F3] rounded-[4px] my-3 h-[30px] w-[110px] gap-[6px]"
                onClick={(e: any) => {
                    if (disabled) {
                        setSummaryParams({ id: id, message: message });
                        setSummaryClick(false);
                    }
                }}
            >
                <span className="text-[12px]">
                    {intl.formatMessage({ id: `app.summaryhistory.submitText` })}
                </span>
                <RedoOutlined className="text-[14px]" />
            </Button>
        </div>
    );
});

const RevisionsMeetingSummary: React.FC<params> = params => {
    let { setShow, inputShow, setBoxLoading, setAppRunId,scrollDom} = params;
    const intl = useIntl();
    const [pageShow, setPageShow] = useState(false);
    const [summaryContent, setSummaryContent] = useState('');
    const [revisions, setRevisions] = useState('');
    const roomId = useRef('');
    const runId = useRef('');
    const isModified = useRef(false);
    const [buttonLoading,setButtonLoading] = useState(false)
    const [currentHistory,setCurrentHistory] = useState(null)
    const setSummaryClick = useChatroomStore(state=>state.setSummaryClick);
    const getMeetingsummaryfn = async (
        id: any,
        data: any = {
            app_run_id: '',
            corrected_parameter: '',
        },
    ) => {
        let resData = await getMeetingsummary(id, data);
        if (resData?.code == 0) {
            setAppRunId(resData?.data?.app_run_id);
            runId.current = resData?.data?.app_run_id;
            if(data.app_run_id){
                isModified.current = true
            }
            // scrollDom.current.scrollTo({top: 1});
        }
    };

    const getMeetingSinglesummaryfn = async (id: any, message: any) => {
        let resData = await getMeetingSinglesummary(id, { message: message });
       
        if (resData?.code == 0) {
            runId.current = resData?.data?.app_run_id;
            setAppRunId(resData?.data?.app_run_id);
            if (resData?.data?.outputs?.value) {
                setSummaryContent(resData?.data?.outputs?.value);
                setShow(true);
                setBoxLoading(false);
                setSummaryClick(true)
                scrollDom.current.scrollTo({top: 0});
            }
        }
    };
    const getMeetingSummaryHistorySinglefn = async()=>{
        let res = await getMeetingSummaryHistorySingle({chatroom_id:roomId.current,app_run_id:runId.current});
        if(res &&  res?.data){
            setCurrentHistory(res.data)
        }
    }
    const timeConversion=time=>{
        let newTime = new Date(time);
        let month = newTime.getMonth()+1;
        let day = newTime.getDate();
        let hour = newTime.getHours();
        let minute =newTime.getMinutes();
        let second = newTime.getSeconds();
        return newTime.getFullYear()+'-'+(month<10?'0'+month:month)+'-'+(day<10?'0'+day:day)+' '+(hour<10?'0'+hour:hour)+':'+(minute<10?'0'+minute:minute)+':'+(second<10?'0'+second:second);
    }
    const meetingSummary = useSocketStore(state => state.flowMessage);
    useEffect(() => {
        let mettingSummary = meetingSummary.filter(
            item =>
                item.data.app_run_id == runId.current &&
                item.type.indexOf('generate_meeting_summary') !== -1,
        );
        if (mettingSummary.length != 0) {
            const outputs =
                mettingSummary[mettingSummary.length - 1]?.data?.exec_data?.outputs?.value;
            if (outputs) {
                if(isModified.current){
                    getMeetingSummaryHistorySinglefn()
                }
                setSummaryContent(outputs);
                setButtonLoading(false)
                setShow(true);
                setSummaryClick(true)
                setBoxLoading(false);
                scrollDom.current.scrollTo({top: 0});
            }
        }
    }, [meetingSummary]);

    const summaryParams = useChatroomStore(state => state.summaryParams);
    useEffect(() => {
        if (summaryParams && summaryParams.id) {
            roomId.current = summaryParams.id;
            if(currentHistory){
                setCurrentHistory(null);
            }

            if(buttonLoading){
                setButtonLoading(false)
            }
            
            if(summaryContent){
                setSummaryContent('');
            }            
            setPageShow(true)
            if (summaryParams.message) {
                setBoxLoading(true);
                getMeetingSinglesummaryfn(summaryParams.id, summaryParams.message);
            } else {
                getMeetingsummaryfn(summaryParams.id);
            }
        }
    }, [summaryParams]);

    return (
        <>
            {pageShow ? (
                <div className="pb-[16px]">
                    <div className="text-[16px] font-[600] pt-[12px]">
                        {intl.formatMessage({ id: `app.summary.title` })}
                    </div>
                    <div className="text-[14px] pt-[12px] leading-[23px] px-[8px]">
                        {summaryContent ? (
                           <>
                                <div
                                    className={` ${
                                        inputShow ? 'max-h-[400px]' : 'max-h-[400px]'
                                    } p-[12px]  bg-[#F7F7F7]  relative overflow-y-auto`}
                                >
                                    <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                        {currentHistory?currentHistory?.source_run?.summary:summaryContent}
                                    </ReactMarkdown>
                                </div>
                                {currentHistory && currentHistory?.source_corrections?.length>0 || !inputShow ? <Redirect id={roomId.current} message={currentHistory?currentHistory?.source_run?.summary:summaryContent}/> : <></>}  
                           </>

                        ) : (
                            <div className="min-h-[120px] flex items-center justify-center">
                                <Spin size="large" />
                            </div>
                        )}
                    </div>
                    {
                        currentHistory && currentHistory?.source_corrections?.length>0 ? 
                            <div> 
                                <div className='text-[16px] font-[600] py-[8px]'>{intl.formatMessage({id:'app.summaryhistory.orientation'})}:</div>
                                {
                                    currentHistory.source_corrections.map((item,index)=>(
                                        <div key={item.created_time} className='mb-[16px]'>
                                            <div key={item.created_time} className={`rounded-[4px]  ${currentHistory.source_corrections.length-1  == index?'bg-blue-100':'bg-[#F7F7F7]'}`}>
                                                <div className='p-[12px]   leading-[22px]'>
                                                    <div className='tetx-[14px] font-[600] pb-[12px]'>
                                                        {intl.formatMessage({id:'app.summaryhistory.userPrompt'})}: {item.user_prompt}
                                                    </div>
                                                    <div className='tetx-[14px] font-[600] pb-[12px]'>
                                                        {intl.formatMessage({id:'app.summaryhistory.time'})}: {timeConversion(item.created_time)}
                                                    </div>
                                                    <ReactMarkdown  rehypePlugins={[rehypeHighlight]}>
                                                        {item?.corrected_summary}
                                                    </ReactMarkdown>
                                                </div>
                                            </div>
                                            { !inputShow || currentHistory.source_corrections.length-1 != index ? <Redirect id={roomId.current} message={item?.corrected_summary}/> : <></>}  
                                        </div>
                                    ))
                                }
                            </div>
                        :<></>
                    }
                    {inputShow ? (
                        <>
                            <div className="pt-[12px]">
                                <Input.TextArea
                                    onChange={e => {
                                        setRevisions(e.target.value);
                                    }}
                                    value={revisions}
                                    disabled={!summaryContent || buttonLoading}
                                    rows={4}
                                    placeholder={intl.formatMessage({
                                        id: 'app.summary.placeholder',
                                    })}
                                
                                ></Input.TextArea>
                            </div>
                            <div className="flex pt-[12px] gap-x-[4px]">
                                <Button
                                    type="primary"
                                    disabled={!summaryContent || !revisions}
                                    loading={buttonLoading}
                                    className="bg-[#1B64F3] rounded-[4px] w-[88px] h-[40px] flex-1"
                                    onClick={() => {
                                        getMeetingsummaryfn(roomId.current, {
                                            app_run_id: String(runId.current),
                                            corrected_parameter: revisions,
                                        });
                                        // setBoxLoading(true);
                                        setButtonLoading(true)
                                        setRevisions('');
                                        setShow('');
                                    }}
                                >
                                    {intl.formatMessage({ id: `app.summary.submitText` })}
                                </Button>
                            </div>
                        </>
                    ) : (
                        <></>
                    )}
                </div>
            ) : (
                <></>
            )}
        </>
    );
};

export default memo(RevisionsMeetingSummary);
