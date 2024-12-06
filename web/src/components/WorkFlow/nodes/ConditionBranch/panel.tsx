// /*
//  * @LastEditors: biz
//  */

/*
 * @LastEditors: biz
 */
import { CopyOutlined, DeleteOutlined, RedoOutlined } from '@ant-design/icons';
import {
    ProCard,
    ProForm,
    ProFormDependency,
    ProFormGroup,
    ProFormInstance,
    ProFormList,
    ProFormSelect,
    ProFormText,
} from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Button, Tag, Tooltip } from 'antd';
import { memo, useCallback, useRef, useState } from 'react';
import useNodeIdUpdate from '../../hooks/useNodeIdUpdate';
import useStore from '../../store';
import { resetFormNodes } from '../../utils/resetFormNodes';

type CountType = {
    [key: string]: { label: string; value: string; name: string };
};
interface Option {
    label: string;
    value: string;
}
const transformEnumToOptions = (enumObj: CountType): Option[] => {
    return Object.entries(enumObj).map(([key, value]) => ({
        label: `${value.label}`,
        value: value.value as string,
    }));
};


type SelectOption = {
    label: string;
    value: string;
    options?: SelectOption[];
};
type GroupedSelectOption = {
    label: JSX.Element;
    title: string;
    options: {
        label: JSX.Element;
        value: string;
    }[];
};
const transformSelectOptions = (options: SelectOption[]): GroupedSelectOption[] => {
    return options.map(group => {
        return {
            label: <span>{group.label}</span>,
            title: group.value,
            options:
                group.options?.map(item => ({
                    label: <span>{item.label}</span>,
                    value: item.value,
                })) || [],
        };
    });
};

const ConditionBranch = memo(
    () => {
        const intl = useIntl();
        const Conditions = {
            Equals: {
                label: intl.formatMessage({ id: 'condition.equals', defaultMessage: '' }),
                value: '=',
                name: intl.formatMessage({ id: 'condition.equals', defaultMessage: '' }),
            },
            NotEqual: {
                label: intl.formatMessage({ id: 'condition.notEqual', defaultMessage: '' }),
                value: '!=',
                name: intl.formatMessage({ id: 'condition.notEqual', defaultMessage: '' }),
            },
            Contains: {
                label: intl.formatMessage({ id: 'condition.contains', defaultMessage: '' }),
                value: 'in',
                name: intl.formatMessage({ id: 'condition.contains', defaultMessage: '' }),
            },
            DoesNotContain: {
                label: intl.formatMessage({
                    id: 'condition.doesNotContain',
                    defaultMessage: '',
                }),
                value: 'not in',
                name: intl.formatMessage({
                    id: 'condition.doesNotContain',
                    defaultMessage: '',
                }),
            },
            StartsWith: {
                label: intl.formatMessage({ id: 'condition.startsWith', defaultMessage: '' }),
                value: 'startswith',
                name: intl.formatMessage({ id: 'condition.startsWith', defaultMessage: '' }),
            },
            EndsWith: {
                label: intl.formatMessage({ id: 'condition.endsWith', defaultMessage: '' }),
                value: 'endswith',
                name: intl.formatMessage({ id: 'condition.endsWith', defaultMessage: '' }),
            },
            IsEmpty: {
                label: intl.formatMessage({ id: 'condition.isEmpty', defaultMessage: '' }),
                value: 'is None',
                name: intl.formatMessage({ id: 'condition.isEmpty', defaultMessage: '' }),
            },
            IsNotEmpty: {
                label: intl.formatMessage({ id: 'condition.isNotEmpty', defaultMessage: '' }),
                value: 'is not None',
                name: intl.formatMessage({ id: 'condition.isNotEmpty', defaultMessage: '' }),
            },
        };
        const Count = {
            Equals: {
                label: '=',
                value: '=',
                name: intl.formatMessage({ id: 'count.equals', defaultMessage: '' }),
            },
            NotEqual: {
                label: '≠',
                value: '!=',
                name: intl.formatMessage({ id: 'count.notEqual', defaultMessage: '' }),
            },
            GreaterThan: {
                label: '>',
                value: '>',
                name: intl.formatMessage({ id: 'count.greaterThan', defaultMessage: '' }),
            },
            LessThan: {
                label: '<',
                value: '<',
                name: intl.formatMessage({ id: 'count.lessThan', defaultMessage: '' }),
            },
            GreaterThanOrEqualTo: {
                label: '≥',
                value: '>=',
                name: intl.formatMessage({
                    id: 'count.greaterThanOrEqualTo',
                    defaultMessage: '',
                }),
            },
            LessThanOrEqualTo: {
                label: '≤',
                value: '<=',
                name: intl.formatMessage({
                    id: 'count.lessThanOrEqualTo',
                    defaultMessage: '',
                }),
            },
            IsNull: {
                label: intl.formatMessage({ id: 'count.isNull', defaultMessage: '' }),
                value: 'is None',
                name: intl.formatMessage({ id: 'count.isNull', defaultMessage: '' }),
            },
            IsNotNull: {
                label: intl.formatMessage({ id: 'count.isNotNull', defaultMessage: '' }),
                value: 'is not None',
                name: intl.formatMessage({ id: 'count.isNotNull', defaultMessage: '' }),
            },
        };
        const transformCountOptions = (type: string) => {
            return transformEnumToOptions(type == 'string' ? Conditions : Count);
        };
        const formRef = useRef<ProFormInstance>(null);
        const cardRef = useRef(null);
        const [labelType, setLabelType] = useState([]);
        const [formVal, setFormVal] = useState(null);
        const [editorOptions, setEditorOptions] = useState([]);
        const [nodeId, setNodeId] = useState('');
        const getVariables = useStore(state => state.getOutputVariables);
        let a = '';
        const updateNodeDate = useStore(state => state.updateNodeData);
        console.log('ConditionBranch panel ');

        const handleNodeIdUpdate = useCallback((id, node) => {

            if (!id || !node) return;
            // if (node.data?.count) {
            //     formRef.current.setFieldsValue({ count: node.data.count });
            // }
            // const fieldNames = Object.keys(formRef.current.getFieldsValue());
            // fieldNames.forEach(e => {
            //     formRef.current.setFieldsValue({ [e]: node?.data[e] });
            // });

            const reset = resetFormNodes(formRef, node);
            setTimeout(() => {
                reset();
            }, 200);
            setNodeId(id);
            const vars = getVariables(node.id);
            setEditorOptions(vars);
        }, []);

        useNodeIdUpdate(handleNodeIdUpdate);

        const handleFormChange = (changedValues, allValues) => {
            console.log(changedValues);

            updateNodeDate(nodeId, allValues);
        };

        const onFinishForm = values => {
            console.log(values);
        };

        const generateId = (() => {
            let count = 0;
            return () => count++;
        })();

        const andOrClick = async (index: number, old: string) => {
            const getFormVal = await formRef.current.validateFieldsReturnFormatValue();
            console.log(getFormVal);
            getFormVal.count[index].type = !old;
            formRef.current.setFieldsValue(getFormVal);
            updateNodeDate(nodeId, getFormVal);
        };

        // return 3333
        const renderForm = useCallback(() => {}, []);

        return (
            <ProForm
                formRef={formRef}
                submitter={{
                    render: () => null,
                }}
                layout="horizontal"
                omitNil={false}
                autoFocusFirstInput={false}
                // onBlurCapture={(e)=>handleFormChange(e)}
                onValuesChange={handleFormChange}
                onFinish={onFinishForm}
            >
                {/* <div className="user-form">
                    <ProFormSwitch
                        name="wait_for_all_predecessors"
                        label=""
                    ></ProFormSwitch>

                    <ProFormSwitch name="manual_confirmation" label=""></ProFormSwitch>
                </div> */}
                <ProFormList
                    name="count"
                    initialValue={[
                        {
                            name: 'IF',
                            type: true,
                        },
                    ]}
                    min={1}
                    copyIconProps={{
                        tooltipText: intl.formatMessage({
                            id: 'workflow.tooltip.copy',
                            defaultMessage: '',
                        }),
                        Icon: e => <Button onClick={e.onClick} icon={<CopyOutlined />}></Button>,
                    }}
                    deleteIconProps={{
                        Icon: (e, m) => {
                            return (
                                <Button
                                    className="ml-2"
                                    onClick={e.onClick}
                                    icon={<DeleteOutlined />}
                                ></Button>
                            );
                        },
                    }}
                    itemRender={({ listDom, action }, { record, index }) => {
                        return (
                            <ProCard
                                key={index}
                                bordered
                                extra={action}
                                title={
                                    index == 0
                                        ? intl.formatMessage({
                                              id: 'workflow.title.if',
                                              defaultMessage: 'IF',
                                          })
                                        : intl.formatMessage({
                                              id: 'workflow.title.elseIf',
                                              defaultMessage: 'ELSE-IF',
                                          })
                                }
                                style={{
                                    marginBlockEnd: 14,
                                    padding: 0,
                                    border: '1px solid #e8e8e8',
                                }}
                                bodyStyle={{
                                    paddingBottom: 0,
                                }}
                            >
                                {listDom}
                            </ProCard>
                        );
                    }}
                    creatorButtonProps={{
                        creatorButtonText: intl.formatMessage({
                            id: 'workflow.button.addCondition',
                            defaultMessage: '',
                        }),
                        type: 'primary',
                    }}
                >
                    <ProFormList
                        name="labels"
                        min={1}
                        initialValue={[{}]}
                        creatorButtonProps={{
                            creatorButtonText: intl.formatMessage({
                                id: 'workflow.button.addComparison',
                                defaultMessage: '',
                            }),
                        }}
                        itemRender={({ listDom, action }, listProps) => {
                            return (
                                <div
                                    className="relative mb-2"
                                    style={{
                                        width: 'fit-content',
                                    }}
                                >
                                    <div className="flex overflow-x-auto">
                                        <div>{listDom}</div>
                                        <div>{action}</div>
                                    </div>
                                    {listProps.index != listProps.fields.length - 1 && (
                                        <div className="h-8 absolute top-8 flex justify-center items-center w-full">
                                            <ProFormDependency ignoreFormListField name={['count']}>
                                                {({ count }) => {
                                                    return (
                                                        <>
                                                            <Tag
                                                                color={
                                                                    count[listProps.name[0]].type
                                                                        ? 'cyan'
                                                                        : 'red'
                                                                }
                                                                onClick={() =>
                                                                    andOrClick(
                                                                        listProps.name[0],
                                                                        count[listProps.name[0]]
                                                                            .type,
                                                                    )
                                                                }
                                                                className="cursor-pointer"
                                                                icon={<RedoOutlined />}
                                                            >
                                                                {count[listProps.name[0]].type
                                                                    ? intl.formatMessage({
                                                                          id: 'workflow.tag.and',
                                                                          defaultMessage: 'and',
                                                                      })
                                                                    : intl.formatMessage({
                                                                          id: 'workflow.tag.or',
                                                                          defaultMessage: 'or',
                                                                      })}
                                                            </Tag>
                                                        </>
                                                    );
                                                }}
                                            </ProFormDependency>
                                        </div>
                                    )}
                                </div>
                            );
                        }}
                    >
                        <ProFormGroup key="group">
                            <div className="flex gap-2">
                                <ProFormSelect
                                    name="variable"
                                    width={130}
                                    allowClear={false}
                                    options={editorOptions}
                                    onChange={(e, i) => {
                                        console.log(e, i);
                                    }}
                                    fieldProps={{
                                        optionRender: e => {
                                            return (
                                                <Tooltip title={e.label}>
                                                    <div title="">{e.label}</div>
                                                </Tooltip>
                                            );
                                        },
                                    }}
                                />
                                <ProFormDependency name={['variable']}>
                                    {({ variable }) => {
                                        const vars = getVariables(nodeId)?.find(
                                            x => x.value == variable,
                                        );
                                        const type = vars?.createVar?.type;
                                        console.log(type);
                                        return (
                                            <ProFormSelect
                                                name="count"
                                                showSearch
                                                options={transformCountOptions(type)}
                                            />
                                        );
                                    }}
                                </ProFormDependency>

                                <ProFormText name="target"></ProFormText>
                            </div>
                        </ProFormGroup>
                    </ProFormList>
                </ProFormList>
                {/* <ProFormDependency ignoreFormListField name={['count']}>
                    {({ count }) => {
                        return count?.length ? (
                            <div className="">
                                <Typography.Title level={5}>ELSE</Typography.Title>
                            </div>
                        ) : null;
                    }}
                </ProFormDependency> */}
            </ProForm>
        );
    },
    () => true,
);

export default ConditionBranch;
