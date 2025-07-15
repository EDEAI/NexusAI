import { PostappsCreate } from '@/api/creation';
import { GetskillInfo, PutskillUpdate } from '@/api/skill';
import { skillDebug } from '@/api/workflow';
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
import { Button, Form, Menu, message, Spin, Splitter } from 'antd';
import _ from 'lodash';
import React, { useEffect, useRef, useState } from 'react';
import SkillFirst from './components/SkillFirst';
import SkillSecond from './components/SkillSecond';
import SkillThirdly from './components/SkillThirdly';
import BugFix from './BugFix';
import { useLatest } from 'ahooks';

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
                          };
                      })
                    : [{ name: '', content: '', output_format: 0, status: true, type: 'string' }],
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
            input_variables.addProperty(item.name, variable);
        });
        return input_variables;
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
                        />
                    </Splitter.Panel>
                </Splitter>
            </div>
        </div>
    );
};
export default Skill;
