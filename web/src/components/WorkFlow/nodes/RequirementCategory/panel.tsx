/*
 * @LastEditors: biz
 */
import Callword from '@/components/callword';
import { ProForm, ProFormList, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useMount } from 'ahooks';
import { memo, useRef } from 'react';
import { SelectModelConfigId } from '../../components/Form/Select';
import useStore from '../../store';
import { AppNode } from '../../types';
import { Tooltip } from 'antd';
import { resetFormNodes } from '../../utils/resetFormNodes';

type PromptItem = {
    serializedContent: string;
    value: object;
};
interface Prompt {
    system: PromptItem;
    user: PromptItem;
    assistant: PromptItem;
}


export default memo(({ node }: { node: AppNode }) => {
    const formRef = useRef(null);
    const intl = useIntl();
    const updateNodeData = useStore(state => state.updateNodeData);
    const getVariables = useStore(state => state.getOutputVariables);
    const getModelData = useStore(state => state.getModelData);
    useMount(() => {
        // const fieldNames = Object.keys(formRef.current.getFieldsValue());
        // fieldNames.forEach(e => {
        //     formRef.current.setFieldsValue({ [e]: node.data[e] });
        // });
        const reset = resetFormNodes(formRef, node);
        setTimeout(() => {
            reset();
        }, 200);
    });

    

    const setNodeChange = (addItem: { [key: string]: any }, allValues) => {
        console.log(addItem);

        updateNodeData(node.id, allValues);
    };
    //
    return (
        <>
            <div className="pt-4">
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    formRef={formRef}
                    omitNil={false}
                    autoFocusFirstInput={false}
                    onValuesChange={setNodeChange}
                >
                    <ProFormSelect
                        name="variable"
                        label={intl.formatMessage({
                            id: 'workflow.label.selectVariable',
                            defaultMessage: '',
                        })}
                        fieldProps={{
                            optionRender:(e) => {
                                return <Tooltip title={e.label}>
                                    <div title=''>{e.label}</div>
                                </Tooltip>
                            }
                        }}
                        showSearch
                        allowClear={false}
                        request={async () => getVariables(node.id)}
                    ></ProFormSelect>
                    <SelectModelConfigId form={formRef} name={`model`}></SelectModelConfigId>
                    {/* <ProFormSelect
                        name="model"
                        label={intl.formatMessage({
                            id: 'workflow.label.selectModel',
                            defaultMessage: '',
                        })}
                        showSearch
                        allowClear={false}
                        request={async () => {
                            const res = (await getModelData()) || [];
                            console.log(res);
                            return res;
                        }}
                    ></ProFormSelect> */}
                    <ProFormList
                        name="wrap_list"
                        label={intl.formatMessage({
                            id: 'workflow.label.category',
                            defaultMessage: '',
                        })}
                        min={1}
                        tooltip={intl.formatMessage({
                            id: 'workflow.tooltip.category',
                            defaultMessage:
                                '，',
                        })}
                        alwaysShowItemLabel
                        itemRender={({ listDom, action }, listProps) => {
                            return (
                                <div className="flex" key={listProps.index}>
                                    <div className="flex-1 pt-2 border-stone-300 border rounded-md my-2">
                                        <div className="px-2 flex justify-between cursor-default">
                                            <div>
                                                <div className="text-sm text-gray-500 font-bold pb-1">
                                                    {intl.formatMessage({
                                                        id: 'workflow.label.categoryNumber',
                                                        defaultMessage: '',
                                                    })}
                                                    {listProps.index + 1}
                                                </div>
                                            </div>
                                            <div> {action}</div>
                                        </div>
                                        <div className="-mt-7 overflow-y-auto">{listDom}</div>
                                    </div>
                                </div>
                            );
                        }}
                        creatorButtonProps={{
                            creatorButtonText: intl.formatMessage({
                                id: 'workflow.button.addCategory',
                                defaultMessage: '',
                            }),
                            type: 'primary',
                        }}
                        copyIconProps={{
                            tooltipText: null,
                        }}
                        deleteIconProps={{
                            tooltipText: null,
                        }}
                    >
                        <ProFormTextArea
                            fieldProps={{
                                variant: 'borderless',
                                placeholder: intl.formatMessage({
                                    id: 'workflow.placeholder.enterCategoryContent',
                                    defaultMessage: '',
                                }),
                                autoSize: { minRows: 1, maxRows: 40 },
                                count: {
                                    show: ({ value, count, maxLength }) => {
                                        return <div className="pr-2 text-blue-400">{count}</div>;
                                    },
                                },
                            }}
                            name="que"
                        />
                    </ProFormList>
                    <div className="flex">
                        <div className="flex-1 pt-2 border-stone-300 border rounded-md my-2">
                            <div className="px-2 flex justify-between cursor-default">
                                <div>
                                    <div className="text-sm text-gray-500 font-bold pb-1">
                                        <Callword
                                            name={intl.formatMessage({
                                                id: 'workflow.label.instruction',
                                                defaultMessage: '',
                                            })}
                                            title={intl.formatMessage({
                                                id: 'workflow.tooltip.instruction',
                                                defaultMessage:
                                                    '，',
                                            })}
                                        ></Callword>
                                    </div>
                                </div>
                                <div></div>
                            </div>
                            <div className="overflow-y-auto">
                                <ProFormTextArea
                                    name="prompt"
                                    fieldProps={{
                                        variant: 'borderless',
                                        placeholder: intl.formatMessage({
                                            id: 'workflow.placeholder.enterInstruction',
                                            defaultMessage: '',
                                        }),
                                        autoSize: { minRows: 1, maxRows: 40 },
                                        count: {
                                            show: ({ value, count, maxLength }) => {
                                                return (
                                                    <div className="pr-2 text-blue-400">
                                                        {count}
                                                    </div>
                                                );
                                            },
                                        },
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                </ProForm>
            </div>
        </>
    );
});
