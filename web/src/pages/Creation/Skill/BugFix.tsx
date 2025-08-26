import { PostskillRun, PutskillPublish } from '@/api/skill';
import FileDownloadList from '@/components/common/FileDownloadList';
import BeforeCreate from '@/components/SkillCreate/BeforeCreate';
import CodeEditor from '@/components/WorkFlow/components/Editor/CodeEditor';
import RenderInput from '@/components/WorkFlow/components/RunForm/RenderInput';
import { ProForm, ProFormInstance } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { Button, Collapse, message } from 'antd';
import _ from 'lodash';
import React, { useEffect, useRef, useState } from 'react';
import { history } from 'umi';
import { getErrorMessageKey, validateSkillData } from './components/skillValidator';

interface ChildProps {
    FourthlyValue: (value: any) => void;
    handleBack: (value: any) => void;
    Fourthlyref: any;
    Skillinfo: any;
    Operationbentate: any;
    skillid: any;
    app_id: any;
    skillupdata: any;
    isCreate: boolean;
    setSkillInfo: (value: any) => void;
    readOnly?: boolean;
}
const BugFix: React.FC<ChildProps> = ({
    FourthlyValue,
    Fourthlyref,
    handleBack,
    Skillinfo,
    Operationbentate,
    skillid,
    app_id,
    skillupdata,
    isCreate,
    setSkillInfo,
    readOnly = false,
}) => {
    const intl = useIntl();
    const [skillRun, setSkillRun] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [activeKeys, setActiveKeys] = useState<string | string[]>(['input']);
    const [fileList, setFileList] = useState<any[]>([]);
    const [showResult, setShowResult] = useState(false);
    const proFormRef = useRef<ProFormInstance>();

    useEffect(() => {}, []);

    const handlePublish = async () => {
        const res = await PutskillPublish(app_id ? app_id : Skillinfo.app_id);
        if (res.code == 0) {
            message.success(intl.formatMessage({ id: 'skill.publishsuccess' }));
            // Update skill status after successful publish
            setSkillInfo({
                ...Skillinfo,
                publish_status: 1,
                app_publish_status: 1,
            });
        } else {
            message.error(intl.formatMessage({ id: 'skill.select.value' }));
        }
    };

    const handleDebugRun = async (values: any) => {

        setLoading(true);

        // Save data first, ensure save is successful before executing debug
        const saveRes = await handleSave();

        // Check if save was successful, stop debug run if save failed
        if (saveRes === false || !saveRes || saveRes.code !== 0) {
            setLoading(false);
            return; // Save failed, do not continue with debug execution
        }

        // Wait 400ms after successful save to ensure save operation is fully completed
        // if (saveRes.code === 0) {
        //     await new Promise(resolve => setTimeout(resolve, 1400));
        // }

        // Get the latest skill_id from save result
        const currentSkillId = saveRes.skill_id || skillid || Skillinfo.id;

        const inputVariables = _.cloneDeep(Skillinfo?.input_variables || {});
        Object.entries(values).forEach(([key, val]) => {
            if (inputVariables?.properties?.hasOwnProperty?.(key)) {
                if (inputVariables.properties[key].type === 'file') {
                    inputVariables.properties[key].value = val[0]?.response?.data?.file_id;
                } else {
                    inputVariables.properties[key].value = val;
                }
            }
        });

        const debugData = {
            ...Skillinfo,
            code: JSON.stringify(Skillinfo?.code || {}),
            test_input: inputVariables,
        };

        try {
            console.log('Using skill_id for debug run:', currentSkillId);
            const res = await PostskillRun({
                skill_id: currentSkillId,
                input_dict: debugData.test_input,
            });

            message.success(intl.formatMessage({ id: 'skill.run.success' }));
            setSkillRun(res.data?.outputs);
            setFileList(res.data?.file_list || []);
            setShowResult(true);
            setActiveKeys([]); // Collapse the panel
            setLoading(false);

            if (res.data?.error) {
                message.error(
                    intl.formatMessage({ id: 'skill.debug.run.error' }, { error: res.data.error }),
                );
            }
        } catch (error) {
            setLoading(false);
            setShowResult(false);
            message.error(intl.formatMessage({ id: 'skill.debug.run.failed' }));
            console.error('Skill run error:', error);
        }
    };

    const handleAmend = async () => {
        history.push(`/Skill?app_id=${app_id ? app_id : Skillinfo?.app_id}&type=false`);
        location.reload();
    };

    const handleSave = async () => {
        // Execute full data validation
        const validationResult = validateSkillData(Skillinfo);

        if (!validationResult.isValid) {
            // Display validation errors
            const errorMessages = validationResult.errors
                .filter(error => error.type === 'error')
                .map(error => {
                    // Try to get internationalized message, use original message if not found
                    try {
                        return intl.formatMessage({ id: getErrorMessageKey(error.code) });
                    } catch {
                        return error.message;
                    }
                });

            if (errorMessages.length > 0) {
                message.error(
                    intl.formatMessage(
                        {
                            id: 'skill.message.save.failed.validation',
                        },
                        {
                            errors: errorMessages.join('\n'),
                        },
                    ),
                );
                return false; // Explicitly return false to indicate save failure
            }

            // If only warnings, ask user whether to continue
            const warningMessages = validationResult.errors
                .filter(error => error.type === 'warning')
                .map(error => error.message);

            if (warningMessages.length > 0) {
                message.warning(
                    intl.formatMessage(
                        {
                            id: 'skill.message.save.failed.warnings',
                        },
                        {
                            warnings: warningMessages.join('\n'),
                        },
                    ),
                );
            }
        }

        // Validation passed, execute save logic and wait for completion
        try {
            const result = await skillupdata();
            // skillupdata internally already displays success message, so no need to repeat here
            return result; // Return save result
        } catch (error) {
            message.error(intl.formatMessage({ id: 'skill.conserve.failed' }));
            console.error('Save skill error:', error);
            return false; // Return false when save exception occurs
        }
    };

    const inputPanelItems = [
        {
            key: 'input',
            label: intl.formatMessage({ id: 'skill.inputsetting' }),
            children: (
                <div className="bg-gray-50 rounded-lg p-4">
                    {Skillinfo?.input_variables?.properties &&
                    Object.keys(Skillinfo.input_variables.properties).length > 0 ? (
                        <ProForm formRef={proFormRef} onFinish={handleDebugRun} submitter={false}>
                            <RenderInput data={Skillinfo?.input_variables?.properties} />
                            <div className="flex gap-3 mt-6">
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    loading={loading}
                                    className="flex-1"
                                >
                                    {intl.formatMessage({ id: 'skill.run' })}
                                </Button>
                            </div>
                        </ProForm>
                    ) : (
                        <div className="h-full flex items-center justify-center">
                            <BeforeCreate
                                hasHover={false}
                                icon="/icons/agent_skill.svg"
                                title={intl.formatMessage({ id: 'skill.debug.title' })}
                                loadingText={intl.formatMessage({
                                    id: 'skill.debug.no.input.parameters',
                                })}
                            />
                        </div>
                    )}
                </div>
            ),
        },
    ];

    return (
        <div style={{ height: 'calc(100vh-100px)', width: '100%' }}>
            <div className="flex align-center justify-between my-5 px-4">
                <div className="flex-1 flex items-center font-bold text-base">
                    {intl.formatMessage({ id: 'skill.operationrun' })}
                    {readOnly && (
                        <span className="ml-2 text-sm text-gray-500 font-normal">
                            - {intl.formatMessage({ id: 'readonly.mode' })}
                        </span>
                    )}
                </div>
                {!readOnly && (
                    <>
                        <div>
                            <Button type="primary" className="min-w-24" onClick={handleSave}>
                                {intl.formatMessage({ id: 'skill.btn.save' })}
                            </Button>
                        </div>
                        <Button type="primary" onClick={handlePublish} className="ml-4 min-w-24">
                            {intl.formatMessage({ id: 'skill.publish' })}
                        </Button>
                    </>
                )}
            </div>
            <div className="h-[calc(100vh-160px)] overflow-y-auto px-4 relative flex flex-col gap-4">
                <Collapse
                    activeKey={activeKeys}
                    onChange={setActiveKeys}
                    items={inputPanelItems}
                    size="small"
                    className="[&_.ant-collapse-content-box]:bg-transparent [&_.ant-collapse-content-box]:p-0"
                />

                {showResult && (
                    <div className=" bg-gray-50 rounded-lg p-4">
                        <div className="text-[#555555] text-sm font-medium mb-4">
                            {intl.formatMessage({ id: 'skill.runpreview' })}
                        </div>
                        <div className="min-h-[calc(100vh-400px)] flex flex-col overflow-y-auto">
                            {fileList.length > 0 && (
                                <div>
                                    <FileDownloadList
                                        files={fileList}
                                        title={intl.formatMessage({ id: 'agent.file.output' })}
                                        className="mb-8 !mt-2"
                                    />
                                </div>
                            )}
                            <div className="mb-4 h-[calc(100vh-400px)]">
                                <CodeEditor
                                    language="python3"
                                    value={skillRun && skillRun}
                                    showMaximize={false}
                                    readOnly
                                    isJSONStringifyBeauty
                                    onChange={() => {}}
                                    title={
                                        <div>
                                            {intl.formatMessage({ id: 'skill.debug.output.title' })}
                                        </div>
                                    }
                                />
                            </div>
                        </div>
                    </div>
                )}
            </div>
            <div className="h-[30px] w-1"></div>
        </div>
    );
};
export default BugFix;
