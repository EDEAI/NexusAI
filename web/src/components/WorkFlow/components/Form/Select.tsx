/*
 * @LastEditors: biz
 */
import { ProFormSelect, ProFormSelectProps } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { FormInstance, Tag, Tooltip } from 'antd';
import useStore from '../../store';
import { AppNode } from '../../types';
import { useMount } from 'ahooks';
import React from 'react';

export type RawValueType = string | number;
export interface LabelInValueType {
    label: React.ReactNode;
    value: RawValueType;
    /** @deprecated `key` is useless since it should always same as `value` */
    key?: React.Key;
}
export const findOption = (value: RawValueType,data) => {
    if (!value || !data?.options) return null;

    for (const group of data.options) {
        if (group.options) {
            const found = group.options.find(option => option.value === value);
            if (found) return found;
        }
    }
    return null;
};
export const SelectModelConfigId = ({ name, form, proComponentProps, fieldProps }) => {
    const intl = useIntl();
    // const { data, loading } = useRequest(
    //     () =>
    //         getModelList().then(res => {
    //             const safeModels = Array.isArray(res?.data?.data) ? res.data.data : [];

    //             const options = safeModels.map(supplier => ({
    //                 label: supplier.supplier_name,
    //                 options: Array.isArray(supplier.model_list) ? supplier.model_list.map(model => ({
    //                     label: model.model_name,
    //                     value: model.model_config_id,
    //                 })) : []
    //             }));

    //             let defaultValue;
    //             for (const supplier of safeModels) {
    //                 if (Array.isArray(supplier.model_list)) {
    //                     const defaultModel = supplier.model_list.find(model => model.model_default_used === 1);
    //                     if (defaultModel) {
    //                         defaultValue = defaultModel.model_config_id;
    //                         break;
    //                     }
    //                 }
    //             }

    //             return {
    //                 options,
    //                 defaultValue
    //             };
    //         }),
    //     {
    //         cacheKey: 'workFlowCacheModelConfigId',
    //         cacheTime: 160 * 1000,
    //     },
    // );
    const data = useStore(state => state.modelOptionsData);
    const imageUnderstandingText = intl.formatMessage({
        id: 'workflow.tag.imageUnderstanding',
        defaultMessage: 'Image Understanding',
    });

    return (
        <div className="min-h-8">
            {
                //  !loading && (
                <ProFormSelect
                    allowClear={false}
                    options={data?.options || []}
                    name={name}
                    initialValue={data?.defaultValue}
                    label={intl.formatMessage({
                        id: 'workflow.label.selectModel',
                        defaultMessage: '',
                    })}
                    fieldProps={{
                        optionRender: option => {
                            return (
                                <div>
                                    {option.label} {' '}
                                    {option?.data?.support_image==1 && (
                                        <Tag color="blue" className="text-xs">
                                            {imageUnderstandingText}
                                        </Tag>
                                    )}
                                    {option?.data?.model_mode==2 && (
                                        <Tag color="default" className="text-xs">
                                            {intl.formatMessage({
                                                id: 'workflow.tag.localModel',
                                                defaultMessage: 'Local Model',
                                            })}
                                        </Tag>
                                    )}
                                </div>
                            );
                        },
                        labelRender: (props: LabelInValueType) => {
                            return (
                                <div>
                                    {props?.label}{' '}
                                    {findOption(props?.value,data)?.support_image==1 && (
                                        <Tag color="blue" className="text-xs">
                                            {imageUnderstandingText}
                                        </Tag>
                                    )}
                                </div>
                            );
                        },
                        ...fieldProps,
                    }}
                    {...proComponentProps}

                ></ProFormSelect>
                // )
            }
        </div>
    );
};

interface SelectVariableProps extends Omit<ProFormSelectProps, 'request'> {
    node?: AppNode | { id: string };
    filterFn?: (item: any) => boolean;
    customRequest?: () => Promise<any[]>;
    formRef?: React.RefObject<FormInstance>;
    options?: any[];
}

export const SelectVariable = ({
    name,
    node,
    filterFn = item => item.createVar.type != 'file',
    customRequest,
    options,
    formRef,
    ...restProps
}: SelectVariableProps) => {
    const intl = useIntl();
    const getVariables = useStore(state => state.getOutputVariables);

    const defaultRequest = async () => {
        if (!node) return [];
        const variables = await getVariables(node.id);
        return variables.filter(filterFn);
    };

    useMount(()=>{
        if(formRef){
            setTimeout(()=>{
                const currentValue = formRef.current?.getFieldsValue(name);
                console.log(currentValue);
            },1000)
        }
    })

    return (
        <ProFormSelect
            placeholder={intl.formatMessage({
                id: 'workflow.placeholder.selectVariable',
                defaultMessage: '',
            })}
            fieldProps={{
                optionRender: e => {
                    return (
                        <Tooltip title={e.label}>
                            <div title="">{e.label}</div>
                        </Tooltip>
                    );
                },
            }}
            colSize={12}
            name={name}
            request={customRequest || defaultRequest}
            {...restProps}
        ></ProFormSelect>
    );
};
