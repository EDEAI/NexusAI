/*
 * @LastEditors: biz
 */
import { getWorkFlowProcessList } from '@/api/workflow';
import Headportrait from '@/components/headportrait';
import useUserStore from '@/store/user';
import { headportrait } from '@/utils/useUser';
import { CheckOutlined, ClockCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useHover, usePagination } from 'ahooks';
import { Empty, Progress } from 'antd';
import { memo, useRef } from 'react';
import { Title } from './TableTitle';

export default memo(() => {
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const intl = useIntl();
    const StatusRender = ({ text }) => {
        switch (text) {
            case 1:
                return <ClockCircleOutlined className="text-blue-500"></ClockCircleOutlined>;
            case 2:
                return <CheckOutlined className="text-green-500"></CheckOutlined>;
            case 3:
                return <WarningOutlined className="text-red-500"></WarningOutlined>;
        }
        return <span>{text}</span>;
    };

    const getDetail = async ({ current, pageSize }) => {
        const res = await getWorkFlowProcessList({
            current,
            pageSize,
        });

        return {
            list: res.data.list,
            success: true,
            total: res.data.total_count,
        };
    };
    const { data, loading, pagination } = usePagination(getDetail, {
        defaultPageSize: 10,
    });

    const ListItem = memo(({ item }) => {
        const statusColor = item.status == 1 ? '#1B64F3' : item.status == 2 ? '#22C55F' : '#F04444';
        const statusBgColor =
            item.status == 1 ? '#f9fafe' : item.status == 2 ? '#f6fcf3' : '#fafafa';

        const ref = useRef(null);
        const isHovering = useHover(ref);
        return (
            <div
                key={item.app_run_id}
                onClick={() => {
                    setRunPanelLogRecord(item);
                    setDealtWithData(null);
                }}
                ref={ref}
                className="flex relative rounded truncate gap-5  items-center shrink-0 cursor-pointer duration-200  box-border py-2.5 pr-5 "
            >
                <div
                    style={{
                        backgroundColor: isHovering ? statusBgColor : '',
                        width: isHovering
                            ? `${(item.completed_steps / item.total_steps) * 100}%`
                            : `0%`,
                        transition: isHovering ? '0.5s' : '0.5s',
                    }}
                    className="w-full h-full absolute left-0 duration-500"
                ></div>

                <div
                    style={{
                        backgroundColor: statusColor,
                    }}
                    className={`w-[4px] h-full z-10 mr-[10px] absolute`}
                ></div>
                {/* <div className="relative size-10 p-2 bg-[#F4F8F1] rounded mr-5">
                                <img
                                    src="/icons/creation/pitchgongzuoliu.svg"
                                    className="size-full"
                                />
                                <div
                                    style={{ boxShadow: `0px 0px 4px 0px rgba(0,0,0,0.1)` }}
                                    className="size-4 p-0.5 bg-white  absolute -right-2 -bottom-1"
                                >
                                    <img
                                        className="size-full"
                                        src={`/icons/creation/${WORKFLOW_ICON.WorkFlow}.svg`}
                                        alt=""
                                    />
                                </div>
                            </div> */}
                <div className="ml-5">
                    <Headportrait
                        Image={headportrait('single', item.icon)}
                        // icon={`/icons/creation/${WORKFLOW_ICON.WorkFlow}.svg`}
                    ></Headportrait>
                </div>
                <div className="flex flex-col gap-1 truncate flex-1  z-10">
                    <div>
                        <span>{item.app_runs_name}</span>
                    </div>
                    <div className="text-[#999999] text-xs truncate  max-w-7/8">
                        <div className="flex items-center truncate">
                            <span> {item.created_time} </span>
                            <span
                                style={{ maxWidth: `calc(100% - 200px)` }}
                                className="truncate ml-2 "
                            >
                                {item.apps_name}
                            </span>
                            <span className="inline-flex items-center ml-2 gap-2">
                                <span
                                    style={{
                                        backgroundColor: statusColor,
                                    }}
                                    className="inline-block w-1 h-1 rounded-sm"
                                ></span>
                                {item.elapsed_time?.toFixed(6)}S
                            </span>
                        </div>
                    </div>
                </div>
                {/* {item.total_steps != item.completed_steps && ( */}
                <div className="flex items-center justify-center">
                    <Progress
                        type="circle"
                        size={30}
                        percent={parseInt((item.completed_steps / item.total_steps) * 100)}
                    />
                </div>
                {/* )} */}
            </div>
        );
    });
    return (
        <div style={{ height: 'calc(100vh - 596px)' }}>
            <Title
                iconSrc="/icons/workflows.svg"
                titleText={intl.formatMessage({ id: 'app.workflow.log.title' })}
                pagination={pagination}
            ></Title>

            <div
                className="bg-white rounded-lg p-4 h-full mt-4 overflow-y-auto box-border relative flex flex-col gap-5"
                style={{ boxShadow: ` 0px 2px 4px 0px rgba(0,0,0,0.05)` }}
            >
                {data?.list?.map((item, index) => {
                    return <ListItem item={item}></ListItem>;
                })}
                {!loading && data?.list?.length === 0 && (
                    <div className="h-full flex items-center justify-center">
                        <Empty
                            image="/images/empty.svg"
                            description={intl.formatMessage({ id: 'app.workflow.log.empty' })}
                        ></Empty>
                    </div>
                )}
            </div>


        </div>
    );
});
