/*
 * @LastEditors: biz
 */
import { getWorkFlowProcessList } from '@/api/workflow';
import FileDownloadList from '@/components/common/FileDownloadList';
import Headportrait from '@/components/headportrait';
import ChatRoomLog from '@/components/LogPanel/ChatRoomLog';
import LogDetail from '@/components/LogPanel/LogDetail';
import useUserStore from '@/store/user';
import { headportrait } from '@/utils/useUser';
import {
    CheckOutlined,
    ClockCircleOutlined,
    FileDoneOutlined,
    WarningOutlined,
} from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useHover, usePagination } from 'ahooks';
import { Empty, Popover, Progress, Select, Tag } from 'antd';
import { memo, useRef, useState } from 'react';
import { Title } from './TableTitle';

export default memo(() => {
    const setDealtWithData = useUserStore(state => state.setDealtWithData);
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
    const intl = useIntl();
    const [showStatus, setShowStatus] = useState(0);
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

    const getDetail = async ({ current, pageSize, showStatus = 0 }) => {
        const res = await getWorkFlowProcessList({
            current,
            pageSize,
            showStatus,
        });

        return {
            list: res.data.list,
            success: true,
            total: res.data.total_count,
        };
    };

    const { data, loading, pagination, run } = usePagination(
        ({ current, pageSize }) => getDetail({ current, pageSize, showStatus }),
        {
            defaultPageSize: 10,
            refreshDeps: [showStatus],
        },
    );

    const [showLogDetail, setShowLogDetail] = useState(false);
    const [logDetail, setLogDetail] = useState<any>(null);
    const [showChatRoomLog, setShowChatRoomLog] = useState(false);
    const handleCloseLogDetail = () => {
        setShowLogDetail(false);
        setShowChatRoomLog(false);
    };

    const handleClickRow = item => {
        switch (item.show_status) {
            case 1:
                setLogDetail(item);
                setShowLogDetail(false);
                setShowChatRoomLog(true);
                break;
            case 2:
                setLogDetail(item);
                setShowChatRoomLog(false);
                setShowLogDetail(true);
                break;
            case 3:
                setRunPanelLogRecord(item);
                setDealtWithData(null);
                break;
            default:
                break;
        }
    };

    const RenderLogType = ({ type }) => {
        switch (type) {
            case 1:
                return (
                    <Tag color="blue">
                        {intl.formatMessage({ id: 'app.workflow.log.type.roundtable' })}
                    </Tag>
                );
            case 2:
                return (
                    <Tag color="green">
                        {intl.formatMessage({ id: 'app.workflow.log.type.agent' })}
                    </Tag>
                );
            case 3:
                return (
                    <Tag color="purple">
                        {intl.formatMessage({ id: 'app.workflow.log.type.workflow' })}
                    </Tag>
                );
        }
    };

    const ListItem = memo(({ item }) => {
        const statusColor = item.status == 1 ? '#1B64F3' : item.status == 2 ? '#22C55F' : '#F04444';
        const statusBgColor =
            item.status == 1 ? '#f9fafe' : item.status == 2 ? '#f6fcf3' : '#fafafa';

        const ref = useRef(null);
        const isHovering = useHover(ref);

        const RenderTitle = () => {
            if (item.show_status == 1) {
                return item.chat_room_name;
            } else if (item.show_status == 2) {
                return item.app_runs_name;
            } else if (item.show_status == 3) {
                if (item.associated_chat_room_name!="") {
                    return intl.formatMessage(
                        { id: 'app.workflow.log.roundtable.guidance' },
                        { name: item.associated_chat_room_name },
                    );
                } 
                return item.app_runs_name;
            }
            return item.apps_name;
        };

        const RenderSubTitle = () => {
            if (item.show_status == 1 && item.apps_name) {
                return intl.formatMessage(
                    { id: 'app.workflow.log.guidance.execution' },
                    {
                        type:
                            item.model == 1
                                ? intl.formatMessage({ id: 'app.workflow.log.type.agent.simple' })
                                : intl.formatMessage({
                                      id: 'app.workflow.log.type.workflow.simple',
                                  }),
                        name: item.apps_name,
                    },
                );
            }
            return item.apps_name;
        };
        return (
            <div
                key={item.app_run_id}
                onClick={() => {
                    handleClickRow(item);
                    // setRunPanelLogRecord(item);
                    // setDealtWithData(null);
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

                <div className="ml-5">
                    <Headportrait
                        Image={headportrait('single', item.icon)}
                        avatar={item.avatar}
                        // icon={`/icons/creation/${WORKFLOW_ICON.WorkFlow}.svg`}
                    ></Headportrait>
                </div>
                <div className="flex flex-col gap-1 truncate flex-1  z-10">
                    <div>
                        <span>
                            <RenderLogType type={item.show_status} />
                            <RenderTitle />
                        </span>
                    </div>
                    <div className="text-[#999999] text-xs truncate  max-w-7/8">
                        <div className="flex items-center truncate">
                            <span> {item.created_time} </span>
                            <span
                                style={{ maxWidth: `calc(100% - 200px)` }}
                                className="truncate ml-2 "
                            >
                                <RenderSubTitle></RenderSubTitle>
                            </span>
                            {(item.show_status == 3 || item.show_status == 2) && (
                                <span className="inline-flex items-center ml-2 gap-2">
                                    <span
                                        style={{
                                            backgroundColor: statusColor,
                                        }}
                                        className="inline-block w-1 h-1 rounded-sm"
                                    ></span>
                                    {item.elapsed_time?.toFixed(6)}S
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                {/* {item.total_steps != item.completed_steps && ( */}
                {item.total_steps != item.completed_steps && (
                    <div className="flex items-center justify-center">
                        <Progress
                            type="circle"
                            size={30}
                            percent={parseInt((item.completed_steps / item.total_steps) * 100)}
                        />
                    </div>
                )}
                {item.show_status == 3 && item?.file_list?.length > 0 && (
                    <div className="flex items-center justify-center z-20">
                        <Popover
                            content={<FileDownloadList files={item?.file_list}></FileDownloadList>}
                            placement="leftTop"
                            title={intl.formatMessage({ id: 'app.workflow.log.output.files' })}
                        >
                            <FileDoneOutlined className="text-[22px] text-green-600" />
                        </Popover>
                    </div>
                )}
            </div>
        );
    });
    return (
        <div className="min-h-[300px]" style={{ height: 'calc(100vh - 596px)' }}>
            <Title
                iconSrc="/icons/workflows.svg"
                titleText={intl.formatMessage({ id: 'app.workflow.log.title' })}
                pagination={pagination}
                showTotal={false}
                titleAfter={
                    <div className="flex-1 flex justify-end">
                        <Select
                            defaultValue={0}
                            className="w-full max-w-[120px]"
                            allowClear
                            style={{
                                maxWidth: '120px',
                            }}
                            onChange={value => {
                                setShowStatus(value);
                                // 重置到第一页
                                pagination.onChange?.(1, pagination.pageSize);
                            }}
                            size="small"
                            options={[
                                {
                                    label: intl.formatMessage({
                                        id: 'app.workflow.log.filter.all',
                                    }),
                                    value: 0,
                                },
                                {
                                    label: intl.formatMessage({
                                        id: 'app.workflow.log.filter.roundtable',
                                    }),
                                    value: 1,
                                },
                                {
                                    label: intl.formatMessage({
                                        id: 'app.workflow.log.filter.agent',
                                    }),
                                    value: 2,
                                },
                                {
                                    label: intl.formatMessage({
                                        id: 'app.workflow.log.filter.workflow',
                                    }),
                                    value: 3,
                                },
                            ]}
                        ></Select>
                    </div>
                }
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

            {showLogDetail && logDetail?.app_run_id && (
                <LogDetail data={logDetail} onClose={handleCloseLogDetail} />
            )}
            {showChatRoomLog && (
                <ChatRoomLog
                    data={{
                        chatroom_id: logDetail?.chatroom_id,
                        app_run_id: logDetail?.app_run_id,
                    }}
                    onClose={handleCloseLogDetail}
                />
            )}
        </div>
    );
});
