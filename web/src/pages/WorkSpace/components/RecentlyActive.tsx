/*
 * @LastEditors: biz
 */
import { getRecentlyActiveList } from '@/api/workflow';
import { ProCard, ProList } from '@ant-design/pro-components';
import { history, useIntl } from '@umijs/max';
import { usePagination } from 'ahooks';
import { Card, Empty, Spin, Tag, Typography } from 'antd';
import { ItemHeader, Title } from './TableTitle';

const { Meta } = Card;
export default () => {

    const intl = useIntl();
    const toDetail = item => {
      
        const id = item.app_id || item.apps_id;
        switch (item.type) {
            case 1:
                history.push(`/Agents?app_id=${id}`);
                break;
            case 2:
                history.push(`/chat_room/${item.chatroom_id}`);
                // history.push(`/chat_room?id=${item.chatroom_id}`)
                break;
            case 3:
                history.push(`/workspace/workflow?app_id=${id}`);
                break;
            default:
                break;
        }
    };
    const getDetail = async ({ current, pageSize }) => {
        const res = await getRecentlyActiveList({
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
        defaultPageSize: 8,
    });


    return (
        <div className="flex-grow-0">
            <Title
                iconSrc="/icons/recently_active.svg"
                titleText={intl.formatMessage({ id: 'app.workflow.ra.title' })}
                pagination={pagination}
            ></Title>
            <div className={`grid grid-cols-4  gap-4 mt-4`}>
                {data?.list?.map((item, index) => {
                    const description = item.type == 3 ? item.process_name : item.last_agent_name;
                    return (
                        <ProCard
                            className="h-[160px] cursor-pointer transition shadow-lg shadow-gray-100 hover:shadow-gray-200"
                            title={<ItemHeader item={item}></ItemHeader>}
                            onClick={() => toDetail(item)}
                            key={item.app_id}
                            bodyStyle={{ padding: '15px 20px' }}
                        >
                            <Typography.Paragraph
                                ellipsis={{
                                    rows: 2,
                                    tooltip: description,
                                }}
                            >
                                {description}
                            </Typography.Paragraph>
                        </ProCard>
                    );
                })}
            </div>
            {!data?.list?.length && (
                <div className="h-[400px] w-full flex items-center justify-center">
                    {!loading && (
                        <Empty
                            imageStyle={{ display: 'flex', justifyContent: 'center' }}
                            image="/images/empty.svg"
                            description={intl.formatMessage({ id: 'app.workflow.ra.empty' })}
                        ></Empty>
                    )}
                    <Spin spinning={loading} />
                </div>
            )}
        </div>
    );

};
