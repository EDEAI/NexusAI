import { getMeetingSinglesummary, getMeetingsummary } from '@/api/plaza';
import useChatroomStore from '@/store/chatroomstate';
import useSocketStore from '@/store/websocket';
import { useIntl } from '@umijs/max';
import { Button, Input, Spin } from 'antd';
import React, { memo, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';

interface params {
    setShow: any;
    inputShow: any;
    setBoxLoading: any;
    setAppRunId: any;
}

const RevisionsMeetingSummary: React.FC<params> = params => {
    let { setShow, inputShow, setBoxLoading, setAppRunId} = params;
    const intl = useIntl();
    const [pageShow, setPageShow] = useState(false);
    const [summaryContent, setSummaryContent] = useState('');
    const [revisions, setRevisions] = useState('');
    const roomId = useRef('');
    const runId = useRef('');
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
            }
            // setTimeout(() => {
            //     scrollDom.current.scrollTo({ top: scrollDom.current.scrollHeight });
            // }, 200);
        }
    };

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
                setSummaryContent(outputs);
                setShow(true);
                setSummaryClick(true)
                setBoxLoading(false);
            }
        }
    }, [meetingSummary]);

    const summaryParams = useChatroomStore(state => state.summaryParams);
    useEffect(() => {
        if (summaryParams && summaryParams.id) {
            roomId.current = summaryParams.id;
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
                            <div
                                className={` ${
                                    inputShow ? 'max-h-[400px]' : 'max-h-[400px]'
                                } p-[12px]  bg-[#F7F7F7]  relative overflow-y-auto`}
                            >
                                <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                    {summaryContent}
                                </ReactMarkdown>
                            </div>
                        ) : (
                            <div className="min-h-[120px] flex items-center justify-center">
                                <Spin size="large" />
                            </div>
                        )}
                    </div>
                    {inputShow ? (
                        <>
                            <div className="pt-[12px]">
                                <Input.TextArea
                                    onChange={e => {
                                        setRevisions(e.target.value);
                                    }}
                                    value={revisions}
                                    disabled={!summaryContent}
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
                                    className="bg-[#1B64F3] rounded-[4px] w-[88px] h-[40px] flex-1"
                                    onClick={() => {
                                        getMeetingsummaryfn(roomId.current, {
                                            app_run_id: String(runId.current),
                                            corrected_parameter: revisions,
                                        });
                                        setBoxLoading(true);
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
