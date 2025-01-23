/*
 * @LastEditors: biz
 */
/*
 * @LastEditors: biz
 */
import { skillCorrection, skillCreate, skillDataCreate } from '@/api/workflow';
import useUserStore, { UPDATE_NOTIFICATIONS } from '@/store/user';
import useSocketStore from '@/store/websocket';
import {
    BugOutlined,
    EditOutlined,
    SaveOutlined,
    SendOutlined,
    ToolOutlined,
} from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { useLatest, useSetState, useUpdateEffect } from 'ahooks';
import { Button, Modal, Tooltip } from 'antd';
import { memo, useCallback, useEffect, useMemo, useState } from 'react';
import { PromptTextarea } from '../AgentCreate/ResultDisplay';
import CodeEditor from '../WorkFlow/components/Editor/CodeEditor';
import BeforeCreate from './BeforeCreate';
import BugFix from './BugFix';
import ResultDisplay from './ResultDisplay';
import InfiniteScrollDemo from '../common/InfiniteScrollDemo';

const SkillCreate = memo(() => {
    const intl = useIntl();
    const [prompt, setPrompt] = useState('');
    const [loading, setLoading] = useState(false);
    const { skillCreateOpen, setSkillCreateOpen } = useUserStore(state => ({
        skillCreateOpen: state.skillCreateOpen,
        setSkillCreateOpen: state.setSkillCreateOpen,
    }));
    const [skillCreateResult, setSkillCreateResult] = useState(null);
    const [bugFixshow, setBugFixshow] = useState(false);
    const [params, setParams] = useSetState(null);
    const lastParams=useLatest(params)
    const flowMessage = useSocketStore(state => state.flowMessage);
    const [hasProcessed, setHasProcessed] = useState(false);
    const [changeSkill, setChangeSkill] = useState(null);
    const changeSkillLast = useLatest(changeSkill);
    const { setUpdateNotification } = useUserStore(state => ({
        setUpdateNotification: state.setUpdateNotification,
    }));
    const CodeEditorMemo = useMemo(
        () => (
            <CodeEditor
                language="python3"
                value={skillCreateResult?.code?.['python3']}
                onChange={value => {
                    setChangeSkill(prev => ({
                        ...prev,
                        code: {
                            ...prev?.code,
                            python3: value,
                        },
                    }));
                }}
                title={
                    <div>
                        python3 <EditOutlined></EditOutlined>
                    </div>
                }
            />
        ),
        [skillCreateResult?.code],
    );

    useEffect(() => {
        console.log('skillCreateOpen', skillCreateOpen);
    }, [skillCreateOpen]);

    const resetState = useCallback(() => {
        setLoading(false);
        setSkillCreateResult(null);
        setSkillCreateOpen(false);
        setPrompt('');
        setBugFixshow(false);
        setParams(null);
        setHasProcessed(false);
        setChangeSkill(null);
    }, []);

    const handleCancel = () => {
        if (skillCreateResult) {
            Modal.confirm({
                title: intl.formatMessage({ id: 'agent.modal.leave.title' }),
                content: intl.formatMessage({ id: 'agent.modal.leave.content' }),
                centered: true,
                onOk: () => {
                    resetState();
                },
            });
            return 
        }
        resetState();
    };

    const handleOk = async () => {
        try {
            setSkillCreateOpen(false);
            resetState();
        } catch (error) {
            console.error(error);
        }
    };

    const handleSubmit = useCallback(async (value: string) => {
        setLoading(true);
        try {
            const res = await skillCreate(value);
            if (res.code == 0) {
                // setSkillCreateResult(res.data);
                setHasProcessed(false);
                setParams(res.data);
                setPrompt(value);
                setParams({
                    app_id: null,
                });
            }

            console.log('submit prompt:', value);
        } catch (error) {
            console.error(error);
        } finally {
        }
    }, []);

    const handleCorrection = useCallback(
        async (value: string, app_run_id) => {
            setLoading(true);
            try {
                const res = await skillCorrection(app_run_id, value);
                if (res.code == 0) {
                    // setSkillCreateResult(res.data);
                    setHasProcessed(false);
                }
            } catch (e) {
                console.log(e);
            }
        },
        [params],
    );

    useUpdateEffect(() => {
        const currentMessage = flowMessage?.find(
            item =>
                item?.data?.app_run_id == params?.app_run_id &&
                item?.data?.exec_data?.exec_id == params?.record_id,
        );
        if (currentMessage && !hasProcessed) {
            try {
                const output = JSON.parse(currentMessage?.data?.exec_data?.outputs?.value);
                setSkillCreateResult(output);
                setChangeSkill(output);
            } catch (e) {
                console.log(e);
            }
            setLoading(false);
            setHasProcessed(true);
        }
    }, [flowMessage]);

    const Create = useCallback(
        ({ loading }) => {
            return (
                <div className="flex gap-4 h-full relative">
                    <BeforeCreate
                        hasHover={false}
                        loading={loading}
                        icon="/icons/agent_skill.svg"
                        title={intl.formatMessage({ id: 'skill.create.beforeTitle' })}
                        // description={intl.formatMessage({ id: 'skill.create.beforeDesc' })}
                        loadingText={intl.formatMessage({ id: 'skill.create.loading' })}
                    />
                    <div className="w-1/2">
                        <PromptTextarea
                            className="h-full"
                            defaultValue={prompt}
                            placeholder={intl.formatMessage({ id: 'skill.prompt.placeholder' })}
                            submitText={intl.formatMessage({ id: 'skill.prompt.submit' })}
                            submitIcon={<SendOutlined />}
                            loading={loading}
                            onSubmit={handleSubmit}
                        />
                    </div>
                </div>
            );
        },
        [prompt],
    );

    const onSave = useCallback(async () => {
        setSkillCreateResult(changeSkillLast.current);
        try {
            setLoading(true);
            console.log({
                ...changeSkillLast.current,
                code: JSON.stringify(changeSkillLast.current?.code || {}),
                app_id: lastParams.current?.app_id || null,
            });

            const res = await skillDataCreate({
                ...changeSkillLast.current,
                code: JSON.stringify(changeSkillLast.current?.code || {}),
                app_id: lastParams.current?.app_id || null,
            });
            if (res.code == 0) {
                setParams(res.data);
                setUpdateNotification(UPDATE_NOTIFICATIONS.AGENT_LIST, {
                    action: 'create',
                    data: {},
                });
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [changeSkillLast]);
    
    useEffect(()=>{
        console.log('params',params);
        
    },[params])

    const Created = useCallback(
        ({ loading }) => {
            const [correctVisible, setCorrectVisible] = useState(false);
            const onCorrectVisibleChange = useCallback((visible: boolean) => {
                setCorrectVisible(visible);
            }, []);

            const onCorrect = useCallback(async (value: string) => {
                // 处理修正逻辑
                setCorrectVisible(false);
            }, []);

            return (
                <div className="flex gap-4 h-full relative z-[10000]">
                    <div className="relative flex-1">
                        <ResultDisplay
                            loading={loading}
                            onChange={setChangeSkill}
                            initialValues={skillCreateResult}
                        ></ResultDisplay>
                        <div className="absolute bottom-2 right-2 flex gap-2 p-1  bg-opacity-50 rounded-md">
                            <Tooltip
                                title={intl.formatMessage({
                                    id: 'skill.create.tooltip.regenerate',
                                })}
                            >
                                <Button
                                    type="primary"
                                    color="primary"
                                    variant="filled"
                                    icon={<BugOutlined />}
                                    loading={loading}
                                    onClick={() => setBugFixshow(true)}
                                />
                            </Tooltip>
                            <Tooltip
                                title={intl.formatMessage({ id: 'skill.create.tooltip.correct' })}
                            >
                                <Button
                                    type="primary"
                                    color="primary"
                                    variant="filled"
                                    icon={<ToolOutlined />}
                                    loading={loading}
                                    onClick={() => setCorrectVisible(true)}
                                />
                            </Tooltip>
                            <Tooltip
                                title={intl.formatMessage({ id: 'skill.create.tooltip.save' })}
                            >
                                <Button
                                    type="primary"
                                    variant="filled"
                                    icon={<SaveOutlined />}
                                    loading={loading}
                                    onClick={onSave}
                                />
                            </Tooltip>
                        </div>
                        {correctVisible && (
                            <div className="absolute bottom-2 right-2 w-[calc(100%-20px)] z-10">
                                <PromptTextarea
                                    placeholder={intl.formatMessage({
                                        id: 'skill.create.prompt.modify',
                                    })}
                                    submitText={intl.formatMessage({
                                        id: 'skill.create.button.modify',
                                    })}
                                    submitIcon={<ToolOutlined />}
                                    showCloseButton={true}
                                    className="h-[100px]"
                                    loading={loading}
                                    onClose={() => onCorrectVisibleChange(false)}
                                    onSubmit={e => handleCorrection(e, params?.app_run_id || '')}
                                    submitButtonProps={{
                                        size: 'small',
                                        loading: loading,
                                    }}
                                    key="single-prompt"
                                />
                            </div>
                        )}
                    </div>
                    <div className="w-1/2 flex flex-col gap-4">
                        <PromptTextarea
                            className="flex-1"
                            placeholder={intl.formatMessage({ id: 'skill.prompt.placeholder' })}
                            submitText={intl.formatMessage({ id: 'skill.prompt.submit' })}
                            submitIcon={<SendOutlined />}
                            loading={loading}
                            defaultValue={prompt}
                            onSubmit={handleSubmit}
                        />
                        <div className="h-2/3 z-30">{CodeEditorMemo}</div>
                    </div>
                </div>
            );
        },
        [skillCreateResult, CodeEditorMemo, prompt],
    );

    const handleBugFixSubmit = useCallback(async (values: any) => {
        try {
            // 处理调试提交逻辑
            console.log('debug values:', values);
            setBugFixshow(false);
        } catch (error) {
            console.error(error);
        }
    }, []);

    return (
        <Modal
            title={intl.formatMessage({ id: 'skill.create.title' })}
            className="xl:min-w-[1200px] lg:min-w-[1000px]"
            bodyProps={{
                className: '!h-[600px] overflow-y-auto p-4',
            }}
            closable={true}
            open={skillCreateOpen}
            footer={null}
            onOk={handleOk}
            centered
            onCancel={handleCancel}
            
        >
            {/* <InfiniteScrollDemo></InfiniteScrollDemo> */}
            {skillCreateResult ? <Created loading={loading} /> : <Create loading={loading} />}
            <BugFix
                open={bugFixshow}
                onCancel={() => setBugFixshow(false)}
                skillData={{ ...changeSkill, app_run_id: params?.app_run_id }}
                onSubmit={handleBugFixSubmit}
            />
        </Modal>
    );
});

export default SkillCreate;
