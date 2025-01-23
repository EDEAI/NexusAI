import Graphic from '@/components/Graphic';
import useChatroomStore from '@/store/chatroomstate';
import useUserStore from '@/store/user';
import { RedoOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button } from 'antd';
import React, { memo, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
// Progress bar subtitle
const ProgressContainer: React.FC<{ progressObj: any }> = memo(parmas => {
    let { progressObj } = parmas;
    console.log(progressObj);

    const setEntime = () => {
        return parseFloat(progressObj.elapsed_time).toFixed(6);
    };
    const setCurrentTime = (time: any) => {
        let date = new Date(time);
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        return <>{`${year}.${month}.${day} ${hours}:${minutes}:${seconds}`}</>;
    };
    return (
        <div className="inline-flex gap-x-4 justify-end max-w-[100%]">
            <div className="inline-flex gap-x-[20px] max-w-[100%]">
                <div className="truncate min-w-[70px]">
                    {progressObj.created_time && setCurrentTime(progressObj.created_time)}
                </div>
                <div className="truncate">{progressObj.apps_name || progressObj.app_name}</div>
                <div className="flex items-center gap-x-[7px] truncate min-w-[50px]">
                    <div
                        className={`shrink-0 rounded-full ${
                            progressObj.status == 1
                                ? 'bg-blue-600'
                                : progressObj.status == 2
                                ? 'bg-green-500'
                                : 'bg-red-500'
                        }`}
                        style={{ width: '3px', height: '3px' }}
                    ></div>
                    <div className="truncate">{setEntime()}S</div>
                </div>
            </div>
        </div>
    );
});

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

const SummaryHistoryDom: React.FC<{
    list: any;
    scrollDom: any;
    historyHeight: any;
    id: any;
    runid:any
}> = parmas => {
    let { list, scrollDom, historyHeight, id , runid} = parmas;
    let intl = useIntl();
    const [summaryHistory, setSummaryHistory] = useState([]);
    const domHeight = useRef('100%');
    const [appRunId,setAppRunId] = useState(0)
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const timeConversion = time => {
        let newTime = new Date(time);
        let month = newTime.getMonth() + 1;
        let day = newTime.getDate();
        let hour = newTime.getHours();
        let minute = newTime.getMinutes();
        let second = newTime.getSeconds();
        return (
            newTime.getFullYear() +
            '-' +
            (month < 10 ? '0' + month : month) +
            '-' +
            (day < 10 ? '0' + day : day) +
            ' ' +
            (hour < 10 ? '0' + hour : hour) +
            ':' +
            (minute < 10 ? '0' + minute : minute) +
            ':' +
            (second < 10 ? '0' + second : second)
        );
    };
    const getProperties = properties => {
        let keys = Object.keys(properties);
        let array = [];
        keys.forEach(k => {
            array.push(properties[k]);
        });
        return array;
    };

    useEffect(() => {
        if (scrollDom) {
            domHeight.current = scrollDom?.current?.offsetHeight;
        }
    }, [scrollDom]);

    useEffect(() => {
        if (historyHeight) {
            domHeight.current = 'auto';
        }
    }, [historyHeight]);

    useEffect(() => {
        setSummaryHistory([...list]);
    }, [list]);

    useEffect(()=>{
        console.log(runid);
        
        setAppRunId(runid)
    },[runid])

    return (
        <>
            <div className="px-4" style={{ minHeight: domHeight.current }}>
                {summaryHistory && summaryHistory.length ? (
                    summaryHistory.map(item =>
                        item?.source_run && item?.source_run.summary && (!appRunId ||  appRunId!=item?.source_run?.id)? (
                            
                            <div
                                className="pt-[16px] border-b-[1px] border-color-[#eee] "
                                key={item.source_run.id}
                            >
                                <div className="pb-[60px]">
                                    <div className="text-[16px] font-[600] pb-[8px] flex items-center">
                                        <span className="flex-1">
                                            {intl.formatMessage({ id: 'app.summary.title' })}
                                        </span>
                                    </div>
                                    <p className="text-[12px] color-[#eee] mb-[8px]">
                                        {timeConversion(item?.source_run?.created_time)}
                                    </p>
                                    <div>
                                        <div
                                            className={`p-[12px]  leading-[22px] ${
                                                item?.source_corrections &&
                                                item?.source_corrections.length > 0
                                                    ? 'bg-[#F7F7F7]'
                                                    : 'bg-blue-100 rounded-[4px]'
                                            }`}
                                        >
                                            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                                {item?.source_run?.summary}
                                            </ReactMarkdown>
                                        </div>
                                        <Redirect id={id} message={item?.source_run?.summary} />
                                    </div>
                                    {item?.source_corrections &&
                                    item?.source_corrections.length > 0 ? (
                                        <div>
                                            <div className="text-[16px] font-[600] py-[8px]">
                                                {intl.formatMessage({
                                                    id: 'app.summaryhistory.orientation',
                                                })}
                                                :
                                            </div>
                                            {item?.source_corrections.map((citem,index) => (
                                                <div
                                                    key={citem.created_time}
                                                    className="mb-[16px] last-of-type:mb-0"
                                                >
                                                    <div className={`rounded-[4px]  ${(item?.source_corrections.length-1)!=index? 'bg-[#F7F7F7]':'bg-blue-100'}`}>
                                                        <div className="p-[12px]   leading-[22px]">
                                                            <div className="tetx-[14px] font-[600] pb-[12px]">
                                                                {intl.formatMessage({
                                                                    id: 'app.summaryhistory.userPrompt',
                                                                })}
                                                                : {citem.user_prompt}
                                                            </div>
                                                            <div className="tetx-[14px] font-[600] pb-[12px]">
                                                                {intl.formatMessage({
                                                                    id: 'app.summaryhistory.time',
                                                                })}
                                                                :{' '}
                                                                {timeConversion(citem.created_time)}
                                                            </div>
                                                            <ReactMarkdown
                                                                rehypePlugins={[rehypeHighlight]}
                                                            >
                                                                {citem?.corrected_summary}
                                                            </ReactMarkdown>
                                                        </div>
                                                    </div>
                                                    <Redirect
                                                        id={id}
                                                        message={citem?.corrected_summary}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <></>
                                    )}

                                    {item?.target_run ? (
                                        <div className="py-[12px]">
                                            <div className="text-[16px] font-[600] py-[8px]">
                                                {intl.formatMessage({
                                                    id: 'app.summaryhistory.runapp',
                                                })}
                                                :
                                            </div>
                                            <div>
                                                <div className="text-[14px] py-[6px]">
                                                    <span className="font-[500] ">
                                                        {item?.target_run?.agent_id
                                                            ? 'agent'
                                                            : 'workflow'}
                                                    </span>
                                                    <span className="px-[6px]">:</span>
                                                    <span>{item?.target_run?.app?.name}</span>
                                                </div>
                                            </div>
                                            <div>
                                                {item?.target_run?.inputs?.properties ? (
                                                    <div>
                                                        <div className="text-[16px] color-[#000] font-[600] py-[12px]">
                                                            {intl.formatMessage({
                                                                id: 'app.summaryhistory.input',
                                                            })}
                                                            :
                                                        </div>
                                                        {getProperties(
                                                            item?.target_run?.inputs?.properties,
                                                        ).map(i => (
                                                            <div className='pb-[10px]'>
                                                                <div className="pb-[8px] font-[600]">
                                                                    {i.display_name || i.name}
                                                                </div>
                                                                {/* <Input.TextArea variant='borderless' className='text-[14px]' value={item.value}  rows={6}/> */}
                                                                <div className="py-[4px] px-[11px] text-[14px] leading-[1.5] h-[]">
                                                                    {i.value}
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                ) : (
                                                    <></>
                                                )}
                                            </div>
                                            <div>
                                                {item?.target_run?.raw_user_prompt ? (
                                                    <div>
                                                        <div className="text-[16px] color-[#000] font-[600] py-[12px] pb-[6px]">
                                                            {intl.formatMessage({
                                                                id: 'app.summaryhistory.prompt',
                                                            })}
                                                            :
                                                        </div>
                                                        <div className="py-[4px] px-[11px] text-[14px] leading-[1.5] ">
                                                            {item?.target_run?.raw_user_prompt}
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <></>
                                                )}
                                            </div>
                                            <div>
                                                <div className="text-[16px] font-[600] py-[8px]">
                                                    {intl.formatMessage({
                                                        id: 'app.summaryhistory.results',
                                                    })}
                                                    :
                                                </div>
                                                <div className="p-[12px]  bg-[#F7F7F7]">
                                                    {item?.target_run?.agent_id != 0 ? (
                                                        <div className="p-[12px]  bg-[#F7F7F7] leading-[22px]">
                                                            <ReactMarkdown
                                                                rehypePlugins={[rehypeHighlight]}
                                                            >
                                                                {item?.target_run?.outputs?.value}
                                                            </ReactMarkdown>
                                                        </div>
                                                    ) : (
                                                        <Graphic
                                                            status={item?.target_run?.status}
                                                            icon={item?.target_run?.icon}
                                                            title={item?.target_run?.name}
                                                            textDetails={
                                                                <ProgressContainer
                                                                    progressObj={{
                                                                        created_time:
                                                                            item?.target_run
                                                                                ?.created_time,
                                                                        elapsed_time:
                                                                            item?.target_run
                                                                                ?.elapsed_time,
                                                                        app_name:
                                                                            item?.target_run?.app
                                                                                .name,
                                                                        status: item?.target_run
                                                                            ?.status,
                                                                    }}
                                                                ></ProgressContainer>
                                                            }
                                                            handleClick={() => {
                                                                setRunPanelLogRecord({
                                                                    app_id: item?.target_run?.app
                                                                        ?.id,
                                                                    app_name:
                                                                        item?.target_run?.app?.name,
                                                                    icon: item?.target_run?.icon,
                                                                    workflow_id:
                                                                        item?.target_run
                                                                            ?.workflow_id,
                                                                    type: 2,
                                                                    app_run_id:
                                                                        item?.target_run?.id,
                                                                    run_name:
                                                                        item?.target_run?.name,
                                                                    status: item?.target_run
                                                                        ?.status,
                                                                    created_time:
                                                                        item?.target_run
                                                                            ?.created_time,
                                                                    elapsed_time:
                                                                        item?.target_run
                                                                            ?.elapsed_time,
                                                                    completed_progress: `${item?.target_run?.percentage}%`,
                                                                });
                                                            }}
                                                            progress={
                                                                0 || item?.target_run?.percentage
                                                            }
                                                        ></Graphic>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <></>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <></>
                        ),
                    )
                ) : (
                    <></>
                )}
            </div>
        </>
    );
};

export default memo(SummaryHistoryDom);
