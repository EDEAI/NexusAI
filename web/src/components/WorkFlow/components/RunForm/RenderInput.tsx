/*
 * @LastEditors: biz
 */
import { ProFormDigit, ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Typography } from 'antd';
import _ from 'lodash';

export const RenderInput = ({ data }) => {
    const intl = useIntl();
    const inputs = data;
    if (!inputs || _.isEmpty(inputs)) return null;

    return (
        <div>
            <Typography.Title level={5}>
                {intl.formatMessage({
                    id: 'workflow.title.inputParameters',
                })}
            </Typography.Title>
            {Object.values(inputs)
                .sort((a, b) => a.sort_order - b.sort_order)
                .map((val: any) => {
                    if (val.type === 'number') {
                        return (
                            <ProFormDigit
                                key={val.name}
                                required={val.required}
                                rules={[
                                    {
                                        required: val.required,
                                        message: intl.formatMessage({
                                            id: 'workflow.form.parameter.required',
                                        }),
                                    },
                                ]}
                                name={val.name}
                                initialValue={val.value}
                                label={val.display_name || val.name}
                            />
                        );
                    }
                    return (
                        <ProFormTextArea
                            key={val.name}
                            required={val.required}
                            rules={[
                                {
                                    required: val.required,
                                    message: intl.formatMessage({
                                        id: 'workflow.form.parameter.required',
                                    }),
                                },
                            ]}
                            name={val.name}
                            initialValue={val.value}
                            label={val.display_name || val.name}
                        />
                    );
                })}
        </div>
    );
};

export default RenderInput;
