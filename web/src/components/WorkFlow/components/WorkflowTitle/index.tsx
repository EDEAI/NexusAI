/*
 * @LastEditors: biz
 */
import { Typography } from 'antd';
import { useIntl } from '@umijs/max';
import { memo } from 'react';

interface WorkflowTitleProps {
    name?: string;
    description?: string;
    publishStatus?: boolean;
}

export default memo(({ name, description, publishStatus }: WorkflowTitleProps) => {
    const intl = useIntl();

    return (
        <div className="flex flex-col gap-2 min-w-[300px] max-w-[400px] pointer-events-none">
            <Typography.Title className="!m-0 !text-base whitespace-normal" level={5}>
                {name}
            </Typography.Title>
            {publishStatus && (
                <Typography.Text className="whitespace-normal">
                    ({intl.formatMessage({ id: 'workflow.nodeRunOtherMessage' })})
                </Typography.Text>
            )}
            <Typography.Text className="whitespace-normal text-gray-500">
                {description}
            </Typography.Text>
        </div>
    );
}); 