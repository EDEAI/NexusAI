import { getAgentLogList } from '@/api/agents';
import useUserStore from '@/store/user';
import type { ProColumns } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { useIntl, useSearchParams } from '@umijs/max';
import { useRef, useState } from 'react';
import LogDetail from '../../../components/LogPanel/LogDetail';
export const waitTimePromise = async (time: number = 100) => {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(true);
        }, time);
    });
};

export const waitTime = async (time: number = 100) => {
    await waitTimePromise(time);
};

type GithubIssueItem = {
    url: string;
    id: number;
    number: number;
    title: string;
    labels: {
        name: string;
        color: string;
    }[];
    state: string;
    comments: number;
    created_at: string;
    updated_at: string;
    closed_at?: string;
    agent_id?: number;
    status?: number;
    nickname?: string;
    elapsed_time?: string;
    total_tokens?: number;
    created_time?: string;
};

export default ({agent_id}:{agent_id:number}) => {
    const intl = useIntl();
    const [searchParams] = useSearchParams();
    const formRef = useRef(null);
    const [logDetail, setLogDetail] = useState<any>(null);
    const [showLogDetail, setShowLogDetail] = useState(false);
    const appId = searchParams.get('app_id');
    const handleCloseLogDetail = () => {
        setShowLogDetail(false);
    };

    const handleViewLogDetail = (record: GithubIssueItem) => {
        setLogDetail({
            app_id: appId,
            app_run_id: record.id,
        });
        setShowLogDetail(true);
    };

    const columns: ProColumns<GithubIssueItem>[] = [
        {
            dataIndex: 'index',
            valueType: 'indexBorder',
            width: 48,
        },
        {
            disable: true,
            title: intl.formatMessage({ id: 'workflow.status', defaultMessage: '' }),
            dataIndex: 'status',
            // filters: true,
            // onFilter: true,
            ellipsis: true,
            // valueType: 'select',
            search: false,

            valueEnum: {
                1: {
                    text: intl.formatMessage({ id: 'workflow.running', defaultMessage: '' }),
                    status: 'Processing',
                },
                2: {
                    text: intl.formatMessage({ id: 'workflow.runSc', defaultMessage: '' }),
                    status: 'Success',
                },
                3: {
                    text: intl.formatMessage({ id: 'workflow.runF', defaultMessage: '' }),
                    status: 'Error',
                },
            },
        },

        {
            title: intl.formatMessage({ id: 'workflow.created_time', defaultMessage: '' }),
            dataIndex: 'created_time',
            ellipsis: true,
            tooltip: intl.formatMessage({
                id: 'workflow.created_time_des',
                defaultMessage: intl.formatMessage({
                    id: 'workflow.created_time_des',
                    defaultMessage: '',
                }),
            }),
            search: false,
        },

        {
            title: `${intl.formatMessage({
                id: 'workflow.elapsed_time',
                defaultMessage: '',
            })}S`,
            dataIndex: 'elapsed_time',
            ellipsis: true,
            tooltip: intl.formatMessage({
                id: 'workflow.run_time',
            }),
            search: false,
        },

        {
            title: 'Tokens',
            key: 'showTime',
            dataIndex: 'total_tokens',

            hideInSearch: true,
        },
        {
            title: intl.formatMessage({ id: 'workflow.user' }),
            dataIndex: 'nickname',
            search: false,
            ellipsis: true,
            key: 'user',
        },
    ];

    // const actionRef = useRef<ActionType>();
    const setRunPanelLogRecord = useUserStore(state => state.setRunPanelLogRecord);
   
    return (
        <div className='h-full'>
            <ProTable
                columns={columns}
                formRef={formRef}
                // actionRef={actionRef}
                form={{
                    submitter: false,
                }}
                cardBordered
                style={{ height: 'calc(100% - 20px)' }}
                scroll={{ y: 'calc(100vh - 230px)' }}
                request={async (params, sort, filter) => {
                    console.log(params, sort, filter);

                    const res = await getAgentLogList(appId, {
                        page: params.current,
                        page_size: params.pageSize,
                        // app_id: appId,
                    });
                    console.log(res);
                    // const uniqueData = _.uniqBy(res.data.list, 'app_runs_id');
                    return {
                        data: res.data.list,
                        success: true,
                        total: res.data.total_count,
                    };
                }}
                onRow={record => {
                    return {
                        onClick: () => {
                            handleViewLogDetail(record);
                        },
                        className: logDetail?.app_run_id === record.id ? 'bg-blue-50' : '',
                    };
                }}
                editable={{
                    type: 'multiple',
                }}
                rowKey="app_runs_id"
                search={false}
                options={{
                    search: false,
                    setting: {
                        listsHeight: 600,
                    },
                }}
                pagination={{
                    pageSize: 20,
                    showSizeChanger: false,
                }}
                dateFormatter="string"
                headerTitle={intl.formatMessage({ id: 'agent.log.list' })}
            />
            {
                showLogDetail && logDetail?.app_id && logDetail?.app_run_id && (
                    <LogDetail 
                        data={logDetail} 
                        onClose={handleCloseLogDetail} 
                    />
                )
            }
        </div>
    );
};
