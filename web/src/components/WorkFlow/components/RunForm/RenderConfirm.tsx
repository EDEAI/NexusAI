/*
 * @LastEditors: biz
 */
import { getNodeConfirmUserList } from '@/api/workflow';
import { ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Typography } from 'antd';

export const RenderConfirm = ({ data }) => {
    const intl = useIntl();
    const inputs = data;
    if (!inputs || !inputs.length) return null;

    return (
        <div>
            <Typography.Title level={5}>
                {intl.formatMessage({
                    id: 'workflow.label.human',
                })}
            </Typography.Title>
            {inputs.map((val: any) => (
                <ProFormSelect
                    key={val.node_id}
                    label={val.node_name}
                    name={val.node_id}
                    mode="multiple"
                    required={true}
                    rules={[
                        {
                            required: true,
                            message: intl.formatMessage({
                                id: 'workflow.form.confirmer.required',
                            }),
                        },
                    ]}
                    request={async () => {
                        const res = await getNodeConfirmUserList();
                        return res.data.team_member_list
                            .filter((item: any) => item.user_id && item.nickname)
                            .map((item: any) => ({
                                label: item.nickname,
                                value: item.user_id,
                            }));
                    }}
                />
            ))}
        </div>
    );
};

export default RenderConfirm;
