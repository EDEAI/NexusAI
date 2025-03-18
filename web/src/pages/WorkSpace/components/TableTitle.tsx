/*
 * @LastEditors: biz
 */
import Headportrait from '@/components/headportrait';
import { WORKFLOW_ICON } from '@/components/WorkFlow/config';
import { headportrait } from '@/utils/useUser';
import { useIntl } from '@umijs/max';
import { Pagination, Typography } from 'antd';

export const Title = ({ iconSrc, titleText, pagination,showTotal=true, titleAfter=null }) => {
    const intl = useIntl();
    return (
        <div className="flex items-center gap-4">
            <img src={iconSrc} alt="" />
            <div>{titleText}</div>
            
            <div>
                <Pagination
                    size="small"
                    simple
                    showTotal={(total, range) =>
                        showTotal?`${intl.formatMessage({ id: 'app.workflow.title.1' })}${range[0]}-${
                            range[1]
                        }${intl.formatMessage({
                            id: 'app.workflow.title.2',
                        })} / ${intl.formatMessage({
                            id: 'app.workflow.title.3',
                        })}${total} ${intl.formatMessage({ id: 'app.workflow.title.2' })}`:null
                    }
                    current={pagination.current}
                    pageSize={pagination.pageSize}
                    onShowSizeChange={null}
                    total={pagination.total}
                    onChange={pagination.onChange}
                ></Pagination>
            </div>
            {titleAfter}
        </div>
    );
};

export const ItemHeader = ({ item }) => {
    console.log(item);
    const intl = useIntl();
    let root = `/icons/creation/`;
    let type = '';
    let title=''
    switch (item.type) {
        case 1:
            title =intl.formatMessage({ id: 'app.itemHeader.agent' });
            type='Agent';
            break;
        case 2:
            title = intl.formatMessage({ id: 'app.itemHeader.chatRoom' });
            type='ChatRoom';
            break;
        case 3:
            title = intl.formatMessage({ id: 'app.itemHeader.workFlow' });
            type='WorkFlow';
            break;
        default:
            break;
    }
    root += WORKFLOW_ICON[type];

    return (
        <div className="flex gap-5 shrink-0">
            {/* <div className="relative size-10 p-2 bg-[#F4F8F1] rounded">
                <img src="/logo.svg" />
                <div  style={{boxShadow: `0px 0px 4px 0px rgba(0,0,0,0.1)`}} className="size-4 p-0.5 bg-white  absolute -right-2 -bottom-2">
                    <img className="size-full" src={`${root}.svg`} alt="" />
                </div>
            </div> */}
            <div className="shrink-0">
                <Headportrait
                    Image={
                        item.type == 2 ? `/icons/chat_room.svg` : headportrait('single', item.icon)
                    }
                    icon={`${root}.svg`}
                ></Headportrait>
            </div>
            <div className="flex flex-col justify-center">
                <div className="text-sm text-[#213044]">
                    <Typography.Paragraph
                        ellipsis={{
                            rows: 2,
                            tooltip: item.name,
                        }}
                        className="!mb-0"
                    >
                        {item.name}
                    </Typography.Paragraph>
                </div>
                <div className="text-xs text-[#999999]">{title}</div>
            </div>
        </div>
    );
};
