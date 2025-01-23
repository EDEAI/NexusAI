import { skillDebug } from '@/api/workflow';
import { ProForm, ProFormInstance } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Modal, message } from 'antd';
import _ from 'lodash';
import { memo, useEffect, useRef, useState } from 'react';
import CodeEditor from '../WorkFlow/components/Editor/CodeEditor';
import RenderInput from '../WorkFlow/components/RunForm/RenderInput';
import BeforeCreate from './BeforeCreate';

interface BugFixProps {
    open: boolean;
    onCancel: () => void;
    skillData?: any;
    // onSubmit?: (values: any) => void;
}

const BugFix = memo(({ open, onCancel, skillData }: BugFixProps) => {
    const intl = useIntl();
    const formRef = useRef<ProFormInstance>();
    const [skillRunResult, setSkillRunResult] = useState('');

    useEffect(() => {
        if (!open) {
            setSkillRunResult('');
            formRef.current?.resetFields();
        }
    }, [open]);

    const handleCancel = () => {
        setSkillRunResult('');
        formRef.current?.resetFields();
        onCancel();
    };

    const onSubmit = async val => {
        console.log(val, skillData);
        const variable = _.cloneDeep(skillData?.input_variables || {});
        Object.entries(val).forEach(([key, val]) => {
            if (variable?.properties?.hasOwnProperty?.(key)) {
                variable.properties[key].value = val;
            }
        });
        console.log(variable);

        const debugData = {
            ...skillData,
            code: JSON.stringify(skillData?.code || {}),
            test_input: variable,
        };
        const res = await skillDebug(debugData);
        if (res.code == 0) {
            setSkillRunResult(res.data?.outputs);
            if(res.data?.error) {
                message.error(intl.formatMessage({ id: 'skill.debug.run.error' }, { error: res.data.error }));
            }
        } else {
            message.error(intl.formatMessage({ id: 'skill.debug.run.failed' }));
        }
    };

    return (
        <Modal
            title={intl.formatMessage({ id: 'skill.debug.title' })}
            className="xl:min-w-[1200px] lg:min-w-[1000px]"
            bodyProps={{
                className: '!h-[600px] overflow-y-auto p-4',
            }}
            open={open}
            footer={null}
            onCancel={handleCancel}
            width={1000}
            centered
        >
            <div className="flex gap-4 h-full relative">
                <div className="w-3/4">
                    {skillRunResult ? (
                        <CodeEditor
                            language="python3"
                            value={skillRunResult}
                            showMaximize={false}
                            // mdValue={nodeInfo?.outputs_md}
                            readOnly
                            isJSONStringifyBeauty
                            onChange={() => {}}
                            title={<div>JSON</div>}
                        ></CodeEditor>
                    ) : (
                        <BeforeCreate
                            hasHover={false}
                            icon="/icons/agent_skill.svg"
                            title={intl.formatMessage({ id: 'skill.debug.title' })}
                            loadingText={intl.formatMessage({ id: 'skill.debug.loading' })}
                        />
                    )}
                </div>

                <div className="w-1/2">
                    <ProForm
                        formRef={formRef}
                        submitter={{
                            resetButtonProps: false,
                            submitButtonProps: {
                                className: 'w-full',
                            },
                            searchConfig: {
                                submitText: intl.formatMessage({
                                    id: 'skill.debug.button.run',
                                }),
                            },
                        }}
                        onFinish={onSubmit}
                    >
                        <RenderInput data={skillData?.input_variables?.properties}></RenderInput>
                    </ProForm>
                </div>
            </div>
        </Modal>
    );
});

export default BugFix;
