/*
 * @LastEditors: biz
 */
import { Variable as FlowVariable, ObjectVariable } from '@/py2js/variables.js';
import { DeleteOutlined, EditOutlined, FunctionOutlined, PlusOutlined } from '@ant-design/icons';
import type { ProFormInstance } from '@ant-design/pro-components';
import { ProForm, ProFormRadio, ProFormSwitch, ProFormText } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useControllableValue, useHover, useMount, useResetState, useUpdateEffect } from 'ahooks';
import { Button, Modal } from 'antd';
import { memo, useRef, useState } from 'react';
interface VariableItem {
    name: string;
    display_name: string;
    max_length?: number;
    required: boolean;
    type: string;
}
interface VariableList {
    variables?: VariableItem[];
    onChange?: (obj: { value: VariableItem[]; free: ObjectVariable }) => void;
}
type VariableProps = VariableItem & {
    onEdit: () => void;
    onDel: () => void;
    key: number;
};

const Variable = memo((props: VariableProps) => {
    const ref = useRef(null);
    const isHovering = useHover(ref);
    const intl = useIntl();
    const typeObject = {
        string: intl.formatMessage({ id: 'workflow.vars.text', defaultMessage: '' }),
        long_string: intl.formatMessage({ id: 'workflow.vars.paragraph', defaultMessage: '' }),
        number: intl.formatMessage({ id: 'workflow.vars.number', defaultMessage: '' }),
    };
    return (
        <div
            ref={ref}
            className="flex gap-2 justify-between truncate h-10 items-center p-2 border border-slate-300 rounded-md mt-2 cursor-pointer"
        >
            <div className="flex items-center gap-1 truncate">
                <div>
                    <FunctionOutlined />
                </div>

                <div className="max-w-28 truncate">{props.name}</div>
                <div className="max-w-20 truncate">{props.display_name}</div>
            </div>
            <div className="shrink-0">
                {isHovering ? (
                    <div className="flex gap-1 ">
                        <Button type="text" icon={<EditOutlined />} onClick={props.onEdit}></Button>
                        <Button
                            type="text"
                            icon={<DeleteOutlined />}
                            onClick={props.onDel}
                        ></Button>
                    </div>
                ) : (
                    <div className="flex items-center gap-2 ">
                        {props.required && <div className="text-slate-500 text-xs">{intl.formatMessage({ id: 'workflow.vars.required',defaultMessage:'' })}</div>}
                        <div>{typeObject[props.type]}</div>
                    </div>
                )}
            </div>
        </div>
    );
});

export default memo((props: VariableList) => {
    const intl = useIntl();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editIndex, setEditIndex] = useState(-1);
    const [formDefault, setFormDefault, resetFormDefault] = useResetState({
        name: '',
        display_name: '',
        max_length: 48,
        required: true,
        type: 'string',
    });
    const formRef = useRef<ProFormInstance>();
    const [variables, setVariables] = useControllableValue(props?.variables || [], {
        defaultValue: [],
    });

    useMount(() => {
        props?.variables && setVariables(props.variables);
    });
    const objectTransformFlow = (): ObjectVariable => {
        const flowObjectVariable = new ObjectVariable('input_var', 'Input Object Variable');
        variables.forEach(item => {
            const variable = new FlowVariable(
                item.name,
                item.type == 'long_string' ? 'string' : item.type,
                '',
                item.display_name,
                item.required,
                item.max_length,
            );
            flowObjectVariable.addProperty(item.name, variable);
        });

        return flowObjectVariable;
    };

    useUpdateEffect(() => {
        objectTransformFlow();
        props.onChange?.({
            value: variables,
            free: objectTransformFlow(),
        });
    }, [variables]);

    const handleOk = () => {
        formRef.current?.submit();
    };

    const [type, setType] = useState('string');
    const finishForm = e => {
        setIsModalOpen(false);
        if (editIndex !== -1) {
            setVariables(prev => {
                const newVariables = [...prev];
                newVariables[editIndex] = e;
                console.log(newVariables);

                return newVariables;
            });
            return;
        }
        setVariables(prev => [...prev, e]);
    };

    const delVariable = index => {
        setVariables(prev => prev.filter((item, i) => i !== index));
    };
    const editVariable = index => {
        const item = variables[index];
        formRef.current?.setFieldsValue(item);
        setIsModalOpen(true);
        setEditIndex(index);
    };
    return (
        <>
            <div>
                <div className="flex justify-between items-center pt-4">
                    <div>{intl.formatMessage({ id: 'workflow.vars.inputFields' })}</div>
                    <Button
                        onClick={() => {
                            formRef.current?.resetFields();
                            resetFormDefault();
                            setEditIndex(-1);
                            setIsModalOpen(true);
                        }}
                        type="text"
                        shape="default"
                        icon={<PlusOutlined />}
                    />
                </div>
                <div>
                    {variables.map((item, index) => (
                        <Variable
                            {...item}
                            key={index}
                            onEdit={() => editVariable(index)}
                            onDel={() => delVariable(index)}
                        ></Variable>
                    ))}
                </div>
            </div>

            <Modal
                title={intl.formatMessage({ id: 'workflow.vars.createVariable' })}
                open={isModalOpen}
                onOk={handleOk}
                forceRender={true}
                onCancel={() => setIsModalOpen(false)}
            >
                <ProForm
                    submitter={{
                        render: () => null,
                    }}
                    initialValues={formDefault}
                    formRef={formRef}
                    onFinish={finishForm}
                    autoComplete="off"
                    className="mt-6"
                >
                    <ProFormRadio.Group
                        radioType="button"
                        layout="horizontal"
                        label={intl.formatMessage({ id: 'workflow.vars.variableType' })}
                        name={'type'}
                        fieldProps={{
                            buttonStyle: 'solid',
                            onChange: e => setType(e.target.value),
                        }}
                        options={[
                            {
                                label: intl.formatMessage({ id: 'workflow.vars.text' }),
                                value: 'string',
                            },

                            {
                                label: intl.formatMessage({ id: 'workflow.vars.number' }),
                                value: 'number',
                            },
                        ]}
                    ></ProFormRadio.Group>
                    <ProFormText
                        name={'name'}
                        label={intl.formatMessage({ id: 'workflow.vars.variableName' })}
                        fieldProps={{
                            autoComplete: 'off',
                        }}
                        rules={[
                            { required: true, message:  intl.formatMessage({ id: 'workflow.vars.enterVariableName' })  },
                            {
                                pattern: /^[a-zA-Z0-9_]+$/,
                                message:intl.formatMessage({ id: 'workflow.vars.variableNamePattern' }),
                            },
                            {
                                validator: (rule, value) => {
                                    if (
                                        variables.some(item => item.name === value) &&
                                        editIndex === -1
                                    ) {
                                        return Promise.reject(intl.formatMessage({ id: 'workflow.vars.variableNameExists' }));
                                    }
                                    return Promise.resolve();
                                },
                            },
                        ]}
                    ></ProFormText>
                    <ProFormText name={'display_name'}label={intl.formatMessage({ id: 'workflow.vars.displayName' })}></ProFormText>
                    {/* {type !== 'number' && (
                        <ProFormDigit name={'max_length'} label=""></ProFormDigit>
                    )} */}
                    <ProFormSwitch name={'required'} label={intl.formatMessage({ id: 'workflow.vars.isRequired' })}></ProFormSwitch>
                </ProForm>
            </Modal>
        </>
    );
});
