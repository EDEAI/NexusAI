import { PostappsCreate } from '@/api/creation';
import { GetskillInfo, PutskillUpdate } from '@/api/skill';
import { skillDebug, skillDirectCorrection, SkillDirectCorrectionParams } from '@/api/workflow';
import BeforeCreate from '@/components/SkillCreate/BeforeCreate';
import CodeEditor from '@/components/WorkFlow/components/Editor/CodeEditor';
import RenderInput from '@/components/WorkFlow/components/RunForm/RenderInput';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
import { createappdata, skilldefault } from '@/utils/useUser';
import {
    ArrowLeftOutlined,
    CodeOutlined,
    CreditCardOutlined,
    FileDoneOutlined,
    FileTextOutlined,
} from '@ant-design/icons';
import { ProForm, ProFormInstance } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import type { MenuProps } from 'antd';
import { Button, Form, Menu, message, Modal, Spin, Splitter } from 'antd';
import _ from 'lodash';
import React, { useEffect, useRef, useState } from 'react';
import useSocketStore from '@/store/websocket';
import SkillFirst from './components/SkillFirst';
import SkillSecond from './components/SkillSecond';
import SkillThirdly from './components/SkillThirdly';
import BugFix from './BugFix';
import SkillOptimizeModal from '../components/SkillOptimizeModal';
import SkillOptimizeDiffModal, {
    SkillOptimizeData,
    SkillVariableComparison,
    SkillVariableInfo,
} from '../components/SkillOptimizeDiffModal';

interface PendingOptimizeJob {
    app_run_id: number;
    record_id: number;
}

const Skill: React.FC = () => {
    const intl = useIntl();
    const [FirstSkillref] = Form.useForm();
    const [Secondref] = Form.useForm();
    const [Thirdlyref] = Form.useForm();
    const [Fourthlyref] = Form.useForm();
    const [Procedure, setProcedure] = useState(0);
    const [pageKey, pageKeyfun] = useState('1');
    const [Skillinfo, setSkillInfo] = useState<any>(null);
    const [SkillRelyOn, setSkillRelyOn] = useState<any>(null);
    const [Operationbentate, setOperationbentate] = useState<any>(true);
    const [skillcodestate, setskillcodestate] = useState<any>(false);
    const [Newcode, setNewcode] = useState<any>(null);
    const [app_id, setApp_id] = useState<any>(null);
    const [skillid, setSkillid] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [isCreate, setIsCreate] = useState(false);
    const [optimizeModalVisible, setOptimizeModalVisible] = useState(false);
    const [optimizePrompt, setOptimizePrompt] = useState('');
    const [diffBaseData, setDiffBaseData] = useState<SkillOptimizeData | null>(null);
    const [pendingDiffBaseData, setPendingDiffBaseData] = useState<SkillOptimizeData | null>(null);
    const [nextOptimizeInputData, setNextOptimizeInputData] = useState<SkillOptimizeData | null>(null);
    const [optimizedData, setOptimizedData] = useState<SkillOptimizeData | null>(null);
    const [optimizeLoading, setOptimizeLoading] = useState(false);
    const [optimizeJob, setOptimizeJob] = useState<PendingOptimizeJob | null>(null);
    const [inputComparisons, setInputComparisons] = useState<SkillVariableComparison[]>([]);
    const [outputComparisons, setOutputComparisons] = useState<SkillVariableComparison[]>([]);
    const [diffVisible, setDiffVisible] = useState(false);
    const skillCorrectMessages = useSocketStore(state =>
        state.getTypedMessages('generate_skill_correct'),
    );

    const [skillmenudisabled, setskillmenudisabled] = useState({
        first: false,
        second: false,
        thirdly: false,
    });



    type MenuItem = Required<MenuProps>['items'][number];
    const items: MenuItem[] = [
        {
            key: '1',
            disabled: skillmenudisabled.first,
            icon: <FileDoneOutlined />,
            label: intl.formatMessage({ id: 'skill.menu.input' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                // background: pageKey == '3' ? 'rgba(27,100,243,0.1)' : '#FAFAFA',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '1' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '2',
            disabled: skillmenudisabled.second,
            icon: <CodeOutlined />,
            label: intl.formatMessage({ id: 'skill.menu.code' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                // background: pageKey == '3' ? 'rgba(27,100,243,0.1)' : '#FAFAFA',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '2' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '3',
            disabled: skillmenudisabled.thirdly,
            icon: <CreditCardOutlined />,
            label: intl.formatMessage({ id: 'skill.menu.output' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                // background: pageKey == '3' ? 'rgba(27,100,243,0.1)' : '#FAFAFA',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '3' ? '#1B64F3' : '#213044',
            },
        },

    ];
    useEffect(() => {
        setLoading(true);
        let params = new URLSearchParams(window.location.search);
        const isCreate=!!params.get('app_id')
        setIsCreate(isCreate);
        getSkill();
    }, []);

    //Skill
    const getSkill = async (app_id?: any) => {
        let params = new URLSearchParams(window.location.search);
        setLoading(true);
        let res = null;
        if (!!params.get('app_id') || !!app_id) {
            res = await GetskillInfo(app_id ? app_id : params.get('app_id'), params.get('type'));
            setApp_id(res.data.app_id);
            setSkillid(res.data.id);
        } else {
            res = skilldefault();
        }
        setLoading(false);
        if (res.code == 0) {
            setSkillInfo(res.data);
           
            const firstvalue = objecttoarray(res.data.input_variables);
            FirstSkillref.setFieldsValue(firstvalue);

            setSkillRelyOn(res.data.dependencies ? res.data.dependencies.python3 : []);
            const Thirdlyvalue = objecttoarray(res.data.output_variables);
            Thirdlyref.setFieldsValue(Thirdlyvalue);
            // Initialize fourth form values
            const param = objecttoarray(res.data.input_variables);
            Fourthlyref.setFieldsValue(param);
        } else {
            message.error(intl.formatMessage({ id: 'skill.message.listerror' }));
        }
    };
    // Convert object format to array format for form display
    const objecttoarray = (obj?: any) => {
        const codeData = {
            users:
                !!obj && !!obj.properties
                    ? Object.values(obj.properties).map((item: any) => {
                          return {
                              name: item.name,
                              type: item.type,
                              content: item.display_name,
                              status: item.required,
                              description: item.description,
                          };
                      })
                    : [
                          {
                              name: '',
                              content: '',
                              output_format: 0,
                              status: true,
                              type: 'string',
                              description: '',
                          },
                      ],
        };
        return codeData;
    };

    const Skill_update = async (value: any, newappId?: any) => {
        const param = {
            app_id: newappId ? newappId : app_id,
            data: value,
        };
        const res = await PutskillUpdate(param);
        setLoading(false);
        if (res.code === 0) {
            message.success(intl.formatMessage({ id: 'skill.conserve.success' }));
            // Remove duplicate API call - no need to re-fetch data after successful save
            // getSkill(newappId ? newappId : app_id);
            setLoading(false);
        }
        return res; // Return API response result
    };
    // Return to previous page
    const returnList = () => {

        history.back();
    };

    const FirstValue = (value: any, newappId?: any) => {
        Skill_update(value, newappId);

        const param = objecttoarray(value.input_variables);

        Fourthlyref.setFieldsValue(param);
    };

    const SecondValue = (value: any) => {
        Skill_update(value);
    };

    const ThirdlyValue = (value: any) => {
        Skill_update(value);
    };

    const FourthlyValue = (value: any) => {
        Skill_update(value);
    };

    const handleBack = (id: number) => {
        setProcedure(id);
    };

    const SkillMenuClick: MenuProps['onClick'] = e => {
        pageKeyfun(e.key);
    };
    // Unified skill save/update logic
    const skillupdata = async () => {
        // setLoading(true);
        try {
            if (!app_id) {
                const res = await PostappsCreate(createappdata('GET'));
                setApp_id(res.data.app_id);
                
                const newres = await GetskillInfo(res.data.app_id, false);
                setSkillid(newres.data.id);
                
                const data = {
                    name: Skillinfo?.name || '',
                    description: Skillinfo?.description || '',
                    input_variables: Skillinfo.input_variables
                        ? Skillinfo.input_variables
                        : arraytoobject(FirstSkillref.getFieldsValue()),
                    is_public: Skillinfo.is_public,
                    attrs_are_visible: Skillinfo.attrs_are_visible,
                    dependencies: { python3: !!SkillRelyOn ? SkillRelyOn : [] },
                    code: Newcode
                        ? Newcode
                        : Skillinfo.code
                        ? Skillinfo.code
                        : JSON.stringify({
                              python3: `def main(arg1: int) -> dict:
    return {
        "result": (arg1 + 2) * 3,
    }`,
                          }),
                    output_type: Skillinfo.output_type,
                    output_variables: Skillinfo.output_variables
                        ? Skillinfo.output_variables
                        : arraytoobject(Thirdlyref.getFieldsValue()),
                };
                
                const param = objecttoarray(arraytoobject(FirstSkillref.getFieldsValue()));
                Fourthlyref.setFieldsValue(param);
                
                const updateResult = await Skill_update(data, res.data.app_id);
                
                const createdData = {
                    ...createappdata('GET'),
                    app_id: res.data.app_id,
                };
                createappdata('SET', createdData);
                
                // Update URL after successful creation, add app_id parameter
                if (updateResult.code === 0) {
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('app_id', res.data.app_id);
                    window.history.replaceState({}, '', currentUrl.toString());
                }

                // pageKeyfun('3');
                // Return result containing latest skill_id
                return {
                    ...updateResult,
                    skill_id: newres.data.id
                };
            } else {
                const data = {
                    name: Skillinfo?.name || '',
                    description: Skillinfo?.description || '',
                    input_variables: Skillinfo.input_variables
                        ? Skillinfo.input_variables
                        : arraytoobject(FirstSkillref.getFieldsValue()),
                    is_public: Skillinfo.is_public,
                    attrs_are_visible: Skillinfo.attrs_are_visible,
                    dependencies: { python3: !!SkillRelyOn ? SkillRelyOn : [] },
                    code: Newcode
                        ? Newcode
                        : Skillinfo.code
                        ? Skillinfo.code
                        : JSON.stringify({
                              python3: `def main(arg1: int) -> dict:
    return {
        "result": (arg1 + 2) * 3,
    }`,
                          }),
                    output_type: Skillinfo.output_type,
                    output_variables: Skillinfo.output_variables
                        ? Skillinfo.output_variables
                        : arraytoobject(Thirdlyref.getFieldsValue()),
                };
                
                const param = objecttoarray(arraytoobject(FirstSkillref.getFieldsValue()));
                Fourthlyref.setFieldsValue(param);
                
                const updateResult = await Skill_update(data, app_id);
                
                // Ensure return result contains correct skill_id
                if (updateResult.code === 0) {
                    // If no skillid, get latest skill information
                    if (!skillid) {
                        const skillInfo = await GetskillInfo(app_id, false);
                        if (skillInfo.code === 0) {
                            setSkillid(skillInfo.data.id);
                            setLoading(false);
                            return {
                                ...updateResult,
                                skill_id: skillInfo.data.id
                            };
                        }
                    }
                }
                
                setLoading(false);

                // pageKeyfun('3');
                // Return result containing skill_id
                return {
                    ...updateResult,
                    skill_id: skillid || Skillinfo.id
                };
            }
        } catch (err) {
            setLoading(false);
            throw err; // Re-throw error for caller to handle
        }
    };
    const arraytoobject = (value: any) => {
        const input_variables = new ObjectVariable('output', '', '');
        value.users.forEach((item: any) => {
            const variable = new SkillVariable(
                item.name,
                item.type ? item.type : 'string',
                item.value ? item.value : '',
                item.content, //display_name
                item.status ? item.status : false, //required
            );
            if (item.description !== undefined) {
                variable.description = item.description;
            }
            input_variables.addProperty(item.name, variable);
        });
        return input_variables;
    };

    const normalizeVariableArray = (variables?: any): SkillVariableInfo[] => {
        if (!variables) return [];
        const mapItem = (item: any): SkillVariableInfo => ({
            name: item?.name || '',
            type: item?.type || 'string',
            required:
                typeof item?.required === 'boolean'
                    ? item.required
                    : typeof item?.status === 'boolean'
                    ? item.status
                    : false,
            display_name: item?.display_name || item?.content || item?.name || '',
            description: item?.description || '',
        });
        if (Array.isArray(variables)) {
            return variables.map(mapItem);
        }
        if (variables?.properties) {
            return Object.values(variables.properties).map(mapItem);
        }
        return [];
    };

    const createVariableObjectFromArray = (
        list: SkillVariableInfo[],
        type: 'input' | 'output',
    ) => {
        const variableObject = new ObjectVariable(type === 'input' ? 'input' : 'output', '', '');
        list.forEach(item => {
            if (!item.name) {
                return;
            }
            const variable = new SkillVariable(
                item.name,
                item.type || 'string',
                '',
                item.display_name || item.name,
                item.required ?? false,
            );
            if (item.description !== undefined) {
                variable.description = item.description;
            }
            variableObject.addProperty(item.name, variable);
        });
        return variableObject;
    };

    const convertCodeToString = (codeValue: any): string => {
        if (!codeValue) return '';
        if (typeof codeValue === 'string') {
            try {
                const parsed = JSON.parse(codeValue);
                if (parsed && typeof parsed === 'object' && typeof parsed.python3 === 'string') {
                    return parsed.python3;
                }
            } catch {
                return codeValue;
            }
            return codeValue;
        }
        if (typeof codeValue === 'object' && codeValue !== null) {
            if (typeof codeValue.python3 === 'string') {
                return codeValue.python3;
            }
            return JSON.stringify(codeValue);
        }
        return '';
    };

    const normalizeSkillData = (data: any): SkillOptimizeData => {
        const dependencies =
            Array.isArray(data?.dependencies) || typeof data?.dependencies === 'string'
                ? { python3: Array.isArray(data?.dependencies) ? data.dependencies : [data.dependencies] }
                : {
                      python3: Array.isArray(data?.dependencies?.python3)
                          ? data.dependencies.python3
                          : [],
                  };
        const codeString = convertCodeToString(data?.code);
        return {
            name: data?.name || '',
            description: data?.description || '',
            input_variables: normalizeVariableArray(data?.input_variables),
            dependencies,
            code: {
                python3: codeString,
            },
            output_type:
                typeof data?.output_type === 'number' && data.output_type > 0
                    ? data.output_type
                    : 1,
            output_variables: normalizeVariableArray(data?.output_variables),
        };
    };

    const extractCurrentSkillData = (): SkillOptimizeData | null => {
        if (!Skillinfo) {
            return null;
        }
        const inputList = normalizeVariableArray(Skillinfo.input_variables);
        const outputList = normalizeVariableArray(Skillinfo.output_variables);
        const dependenciesList = Array.isArray(SkillRelyOn)
            ? SkillRelyOn
            : Array.isArray(Skillinfo?.dependencies?.python3)
            ? Skillinfo.dependencies.python3
            : [];
        const codeSource = Newcode || Skillinfo?.code;
        const codeString = convertCodeToString(codeSource);

        return {
            name: Skillinfo.name || '',
            description: Skillinfo.description || '',
            input_variables: inputList,
            dependencies: {
                python3: dependenciesList,
            },
            code: {
                python3: codeString,
            },
            output_type: Skillinfo.output_type || 1,
            output_variables: outputList,
        };
    };

    const mapVariablesForApi = (list: SkillVariableInfo[]) =>
        list.map(item => ({
            name: item.name,
            type: item.type,
            required: item.required ?? false,
            display_name: item.display_name || item.name,
            description: item.description || '',
        }));

    const buildVariableComparisons = (
        currentList: SkillVariableInfo[] = [],
        optimizedList: SkillVariableInfo[] = [],
    ): SkillVariableComparison[] => {
        const getKey = (item: SkillVariableInfo, index: number) =>
            item?.name && item.name.trim() ? item.name : `__index_${index}`;
        const optimizedMap = new Map<string, { item: SkillVariableInfo; index: number }>();
        optimizedList.forEach((item, index) => {
            optimizedMap.set(getKey(item, index), { item, index });
        });
        const usedKeys = new Set<string>();
        const comparisons: SkillVariableComparison[] = currentList.map((item, index) => {
            const key = getKey(item, index);
            const match = optimizedMap.get(key)?.item;
            if (match) {
                usedKeys.add(key);
            }
            return {
                name: item.name || key,
                current: item,
                optimized: match,
            };
        });

        optimizedList.forEach((item, index) => {
            const key = getKey(item, index);
            if (!usedKeys.has(key)) {
                comparisons.push({
                    name: item.name || key,
                    optimized: item,
                });
            }
        });

        return comparisons;
    };

    const buildSkillDirectPayload = (
        baseData: SkillOptimizeData,
        promptText: string,
    ): SkillDirectCorrectionParams => ({
        name: baseData.name,
        description: baseData.description,
        input_variables: mapVariablesForApi(baseData.input_variables),
        dependencies: baseData.dependencies,
        code: baseData.code,
        output_type: baseData.output_type,
        output_variables: mapVariablesForApi(baseData.output_variables),
        correction_prompt: promptText,
    });

    const resetDiffState = () => {
        setDiffVisible(false);
        setOptimizedData(null);
        setDiffBaseData(null);
        setPendingDiffBaseData(null);
        setNextOptimizeInputData(null);
        setInputComparisons([]);
        setOutputComparisons([]);
        setOptimizeJob(null);
        setOptimizeLoading(false);
    };

    const handleOpenOptimizeModal = () => {
        if (optimizeLoading) {
            return;
        }
        if (!Skillinfo) {
            message.warning(intl.formatMessage({ id: 'skill.optimize.error.noData' }));
            return;
        }
        const currentData = extractCurrentSkillData();
        if (!currentData) {
            message.warning(intl.formatMessage({ id: 'skill.optimize.error.noData' }));
            return;
        }
        setNextOptimizeInputData(currentData);
        setOptimizePrompt('');
        setOptimizeModalVisible(true);
    };

    const handleOptimizeCancel = () => {
        if (optimizeLoading && optimizeJob) {
            return;
        }
        setOptimizeModalVisible(false);
        if (!optimizeLoading) {
            setNextOptimizeInputData(null);
        }
    };

    const handleContinueOptimize = () => {
        if (!optimizedData || optimizeLoading) {
            return;
        }
        const baseData = normalizeSkillData(optimizedData);
        setNextOptimizeInputData(baseData);
        setOptimizePrompt('');
        setOptimizeModalVisible(true);
    };

    const handleOptimizeSubmit = async () => {
        if (optimizeLoading) {
            return;
        }
        const promptText = optimizePrompt.trim();
        if (!promptText) {
            message.warning(intl.formatMessage({ id: 'skill.optimize.error.required' }));
            return;
        }
        let baseData = nextOptimizeInputData;
        if (!baseData) {
            const currentData = extractCurrentSkillData();
            if (!currentData) {
                message.warning(intl.formatMessage({ id: 'skill.optimize.error.noData' }));
                return;
            }
            baseData = currentData;
            setNextOptimizeInputData(baseData);
        }
        try {
            setOptimizeModalVisible(false);
            setOptimizePrompt('');
            setPendingDiffBaseData(baseData);
            setDiffBaseData(baseData);
            setOptimizedData(null);
            setInputComparisons([]);
            setOutputComparisons([]);
            setDiffVisible(true);
            setOptimizeLoading(true);

            const payload: SkillDirectCorrectionParams = buildSkillDirectPayload(baseData, promptText);
            const res = await skillDirectCorrection(payload);
            if (res?.code === 0 && res?.data) {
                setOptimizeJob(res.data);
            } else {
                const errorMsg =
                    res?.detail ||
                    res?.message ||
                    intl.formatMessage({ id: 'skill.optimize.error.failed' });
                message.error(errorMsg);
                resetDiffState();
            }
        } catch (error) {
            message.error(intl.formatMessage({ id: 'skill.optimize.error.failed' }));
            resetDiffState();
        }
    };

    useEffect(() => {
        if (!optimizeJob) {
            return;
        }
        const messagesArray = Array.isArray(skillCorrectMessages) ? skillCorrectMessages : [];
        if (!messagesArray.length) {
            return;
        }
        const matched = [...messagesArray]
            .reverse()
            .find(
                item =>
                    item?.data?.app_run_id === optimizeJob.app_run_id &&
                    item?.data?.exec_data?.exec_id === optimizeJob.record_id,
            );
        if (!matched) {
            return;
        }
        if (matched?.data?.status !== 3) {
            const errorMessage =
                matched?.data?.exec_data?.error ||
                matched?.data?.error ||
                intl.formatMessage({ id: 'skill.optimize.error.failed' });
            message.error(errorMessage);
            setOptimizeLoading(false);
            setOptimizeJob(null);
            setPendingDiffBaseData(null);
            setNextOptimizeInputData(null);
            return;
        }
        const rawValue = matched?.data?.exec_data?.outputs?.value;
        try {
            let payload = rawValue;
            if (typeof payload === 'string') {
                payload = JSON.parse(payload);
            }
            if (typeof payload === 'string') {
                payload = JSON.parse(payload);
            }
            const normalized = normalizeSkillData(payload);
            const effectiveBase = pendingDiffBaseData || diffBaseData || normalized;
            setDiffBaseData(effectiveBase);
            setOptimizedData(normalized);
            setInputComparisons(
                buildVariableComparisons(
                    effectiveBase?.input_variables || [],
                    normalized.input_variables || [],
                ),
            );
            setOutputComparisons(
                buildVariableComparisons(
                    effectiveBase?.output_variables || [],
                    normalized.output_variables || [],
                ),
            );
            setOptimizeLoading(false);
            setOptimizeJob(null);
            setPendingDiffBaseData(null);
            setNextOptimizeInputData(null);
        } catch (error) {
            message.error(intl.formatMessage({ id: 'skill.optimize.error.invalid' }));
            setOptimizeLoading(false);
            setOptimizeJob(null);
            setPendingDiffBaseData(null);
            setNextOptimizeInputData(null);
        }
    }, [skillCorrectMessages, optimizeJob, intl, pendingDiffBaseData, diffBaseData]);

    const handleApplyOptimizedResult = () => {
        if (!optimizedData) {
            return;
        }
        const inputObject = createVariableObjectFromArray(optimizedData.input_variables, 'input');
        const outputObject = createVariableObjectFromArray(optimizedData.output_variables, 'output');
        const dependenciesList = optimizedData.dependencies?.python3 || [];
        const codeString = JSON.stringify({
            python3: optimizedData.code?.python3 || '',
        });

        setSkillInfo((prev: any) => ({
            ...(prev || {}),
            name: optimizedData.name,
            description: optimizedData.description,
            input_variables: inputObject,
            dependencies: {
                python3: dependenciesList,
            },
            code: codeString,
            output_type: optimizedData.output_type,
            output_variables: outputObject,
        }));
        setSkillRelyOn(dependenciesList);
        setNewcode(codeString);
        FirstSkillref.setFieldsValue(objecttoarray(inputObject));
        Thirdlyref.setFieldsValue(objecttoarray(outputObject));
        Fourthlyref.setFieldsValue(objecttoarray(inputObject));
        message.success(intl.formatMessage({ id: 'skill.optimize.apply.success' }));
        resetDiffState();
    };

    const handleDiffCancel = () => {
        if (!diffVisible) {
            return;
        }
        Modal.confirm({
            centered: true,
            title: intl.formatMessage({ id: 'skill.optimize.diff.confirm.title' }),
            content: intl.formatMessage({ id: 'skill.optimize.diff.confirm.content' }),
            okText: intl.formatMessage({ id: 'skill.optimize.diff.confirm.ok' }),
            cancelText: intl.formatMessage({ id: 'skill.optimize.diff.confirm.cancel' }),
            onOk: () => {
                resetDiffState();
            },
        });
    };



    return (
        <div className="flex bg-white" style={{ height: 'calc(100vh - 56px)' }}>
          
            <div className="flex flex-col w-[300px]" style={{ height: 'calc(100vh - 56px)' }}>
                <div className="flex w-full items-center bg-white px-[30px] pt-[30px] border-[#e5e7eb] border-solid border-r">
                    <Button
                        type="link"
                        shape="circle"
                        size="middle"
                        className=""
                        onClick={returnList}
                    >
                        <ArrowLeftOutlined />
                        <span className="text-sm font-medium text-[#213044]">
                            {intl.formatMessage({ id: 'skill.back' })}
                        </span>
                    </Button>
                </div>
                <div className="w-full flex-1 px-[30px] py-[30px] bg-white border-[#e5e7eb] border-solid border-r">
                    <Menu
                        selectedKeys={[pageKey]}
                        onClick={SkillMenuClick}
                        style={{ width: '100%', borderInlineEnd: '1px solid rgba(0,0,0,0)' }}
                        defaultSelectedKeys={[pageKey]}
                        mode="inline"
                        items={items}
                    />
                </div>
            </div>

            <div className="flex-1 relative w-[calc(100%-300px)]">
                <Splitter style={{ height: '100%', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
                    <Splitter.Panel defaultSize="50%" min="40%" max="70%">
                        <Spin spinning={loading} size="large" className="mt-[112px] mr-4">
                            <div
                                className="flex flex-col"
                                style={{
                                    height: 'calc(100vh - 56px)',
                                    overflowY: 'scroll',
                                    scrollbarWidth: 'none',
                                }}
                            >
                                <div
                                    className="px-[30px]"
                                    style={{ overflowX: 'auto', height: '100%' }}
                                >
                                    <div className="w-full flex justify-center mt-[30px]">
                                        <div className="flex items-center w-full">
                                            <div className="mr-[10px] w-[16px] h-[16px]">
                                                <img
                                                    src="/icons/flag.svg"
                                                    alt=""
                                                    className="w-[16px] h-[16px]"
                                                />
                                            </div>
                                            <div className="flex items-center">
                                                <div className="mr-[6px] text-lg text-[#213044] font-medium">
                                                    {createappdata('GET')?.app_id
                                                        ? intl.formatMessage({
                                                              id: 'skill.Editingskill',
                                                          })
                                                        : intl.formatMessage({
                                                              id: 'skill.Creatingskill',
                                                          })}
                                                </div>
                                                {Skillinfo?.app_publish_status === 1 ? (
                                                    <div className="bg-[#1B64F3] text-[#fff] px-[7px] rounded font-normal text-xs flex items-center justify-center h-[18px]">
                                                        {intl.formatMessage({
                                                            id: 'skill.havepublished',
                                                        })}
                                                    </div>
                                                ) : (
                                                    <div className="bg-[#EEE] text-[#999] px-[7px] rounded font-normal text-xs flex items-center justify-center h-[18px]">
                                                        {intl.formatMessage({
                                                            id: 'skill.unpublish',
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Skill input settings page */}
                                    <div
                                        style={{
                                            display: pageKey === '1' ? 'flex' : 'none',
                                            height: 'calc(100vh - 146px)',
                                            justifyContent: 'center',
                                        }}
                                    >
                                        {!loading && (
                                            <SkillFirst
                                                loading={loading}
                                                FirstValue={FirstValue}
                                                Skillinfo={Skillinfo}
                                                setSkillInfo={setSkillInfo}
                                                FirstSkillref={FirstSkillref}
                                                Operationbentate={Operationbentate}
                                                pageKeyfun={pageKeyfun}
                                                skillmenudisabled={skillmenudisabled}
                                                setskillmenudisabled={setskillmenudisabled}
                                                isCreate={isCreate}
                                            />
                                        )}
                                    </div>
                                    {/* Skill code settings page */}
                                    <div
                                        style={{
                                            display: pageKey === '2' ? 'flex' : 'none',
                                            height: 'calc(100vh - 146px)',
                                            justifyContent: 'center',
                                        }}
                                    >
                                        <SkillSecond
                                            SecondValue={SecondValue}
                                            handleBack={handleBack}
                                            Skillinfo={Skillinfo}
                                            setSkillInfo={setSkillInfo}
                                            SkillRelyOn={SkillRelyOn}
                                            setSkillRelyOn={setSkillRelyOn}
                                            Secondref={Secondref}
                                            setskillcodestate={setskillcodestate}
                                            setNewcode={setNewcode}
                                            pageKeyfun={pageKeyfun}
                                            skillmenudisabled={skillmenudisabled}
                                            setskillmenudisabled={setskillmenudisabled}
                                        />
                                    </div>
                                    {/* Skill output settings page */}
                                    <div
                                        style={{
                                            display: pageKey === '3' ? 'flex' : 'none',
                                            height: 'calc(100vh - 146px)',
                                            justifyContent: 'center',
                                        }}
                                    >
                                        {!loading && (
                                            <SkillThirdly
                                                loading={loading}
                                                ThirdlyValue={ThirdlyValue}
                                                handleBack={handleBack}
                                                Thirdlyref={Thirdlyref}
                                                Skillinfo={Skillinfo}
                                                setSkillInfo={setSkillInfo}
                                                Operationbentate={Operationbentate}
                                                pageKeyfun={pageKeyfun}
                                                skillmenudisabled={skillmenudisabled}
                                                setskillmenudisabled={setskillmenudisabled}
                                                skillupdata={skillupdata}
                                            />
                                        )}
                                    </div>

                                </div>
                            </div>
                        </Spin>
                    </Splitter.Panel>
                    <Splitter.Panel>
                        <BugFix
                            FourthlyValue={FourthlyValue}
                            handleBack={handleBack}
                            Fourthlyref={Fourthlyref}
                            Skillinfo={Skillinfo}
                            skillid={skillid}
                            app_id={app_id}
                            Operationbentate={Operationbentate}
                            skillupdata={skillupdata}
                            isCreate={isCreate}
                            setSkillInfo={setSkillInfo}
                            onOpenOptimize={!loading && Skillinfo ? handleOpenOptimizeModal : undefined}
                            optimizeLoading={optimizeLoading}
                        />
                    </Splitter.Panel>
                </Splitter>
            </div>
            <SkillOptimizeModal
                open={optimizeModalVisible}
                loading={optimizeLoading}
                title={intl.formatMessage({ id: 'skill.optimize.modal.title' })}
                description={intl.formatMessage({ id: 'skill.optimize.modal.desc' })}
                placeholder={intl.formatMessage({ id: 'skill.optimize.modal.placeholder' })}
                okText={intl.formatMessage({ id: 'skill.optimize.submit' })}
                cancelText={intl.formatMessage({ id: 'skill.optimize.cancel' })}
                value={optimizePrompt}
                onChange={setOptimizePrompt}
                onOk={handleOptimizeSubmit}
                onCancel={handleOptimizeCancel}
            />
            <SkillOptimizeDiffModal
                open={diffVisible}
                current={diffBaseData}
                optimized={optimizedData}
                loading={optimizeLoading && !optimizedData}
                inputComparisons={inputComparisons}
                outputComparisons={outputComparisons}
                onApply={handleApplyOptimizedResult}
                onCancel={handleDiffCancel}
                onContinue={optimizedData ? handleContinueOptimize : undefined}
                applying={optimizeLoading}
                continuing={optimizeLoading && !!optimizeJob}
            />
        </div>
    );
};
export default Skill;
