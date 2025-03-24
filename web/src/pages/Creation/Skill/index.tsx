import { PostappsCreate } from '@/api/creation';
import { GetskillInfo, PutskillUpdate } from '@/api/skill';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
import { createappdata, skilldefault } from '@/utils/useUser';
import {
    ArrowLeftOutlined,
    CodeOutlined,
    CreditCardOutlined,
    FileDoneOutlined,
    FileTextOutlined,
} from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import type { MenuProps } from 'antd';
import { Button, Form, Menu, message, Spin } from 'antd';
import React, { useEffect, useState } from 'react';
import SkillFirst from './components/SkillFirst';
import SkillSecond from './components/SkillSecond';
import SkillThirdly from './components/SkillThirdly';
import SkillFourthly from './components/skillFourthly';

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
    const [loading, setLoading] = useState(false);
    const [skillmenudisabled, setskillmenudisabled] = useState({
        first: false,
        second: false,
        thirdly: false,
        fourthly: false,
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
        {
            key: '4',
            disabled: skillmenudisabled.fourthly,
            icon: <FileTextOutlined />,
            label: intl.formatMessage({ id: 'skill.menu.debug' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                // background: pageKey == '3' ? 'rgba(27,100,243,0.1)' : '#FAFAFA',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '4' ? '#1B64F3' : '#213044',
            },
        },
    ];
    useEffect(() => {
        setLoading(true);
        let params = new URLSearchParams(window.location.search);
        if (!params.get('app_id')) {
            setskillmenudisabled({
                first: false,
                second: true,
                thirdly: true,
                fourthly: true,
            });
        }
        getSkill();
    }, []);

    //Skill
    const getSkill = async (app_id?: any) => {
        let params = new URLSearchParams(window.location.search);
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
            // setOperationbentate(res.data.publish_status === 1 ? 'true' : 'false')
            // if (res.data.publish_status == 1) {
            //     message.warning(intl.formatMessage({ id: 'skill.message.listwarning' }), 5);
            // }
            const firstvalue = objecttoarray(res.data.input_variables);
            FirstSkillref.setFieldsValue(firstvalue);

            setSkillRelyOn(res.data.dependencies ? res.data.dependencies.python3 : []);
            const Thirdlyvalue = objecttoarray(res.data.output_variables);
            Thirdlyref.setFieldsValue(Thirdlyvalue);
            //
            const param = objecttoarray(res.data.input_variables);
            Fourthlyref.setFieldsValue(param);
        } else {
            message.error(intl.formatMessage({ id: 'skill.message.listerror' }));
        }
    };
    //
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
        // if (Operationbentate === 'false') {
        
        const param = {
            app_id: newappId ? newappId : app_id,
            data: value,
        };
        const res = await PutskillUpdate(param);
        setLoading(false);
        if (res.code === 0) {
            // skill.conserve.success{intl.formatMessage({ id: 'skill.back' })}
            message.success(intl.formatMessage({ id: 'skill.conserve.success' }));
            getSkill(newappId ? newappId : app_id);
            setLoading(false);
        }
    };
    //
    const returnList = () => {
        // SkillMenuClick({
        //     key: pageKey,
        //     keyPath: [],
        //     item: undefined,
        //     domEvent: undefined
        // })
        history.back();
    };

    const FirstValue = (value: any, newappId?: any) => {
        debugger
        Skill_update(value, newappId);
        debugger
        const param = objecttoarray(value.input_variables);
        debugger
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
    //
    const skillupdata = () => {
        
        setLoading(true);
        if (!app_id) {
            PostappsCreate(createappdata('GET'))
                .then(res => {
                    setApp_id(res.data.app_id);
                    GetskillInfo(res.data.app_id, false)
                        .then(newres => {
                            setSkillid(newres.data.id);
                            var data = {};
                            data = {
                                input_variables:Skillinfo.input_variables ? Skillinfo.input_variables : arraytoobject(FirstSkillref.getFieldsValue()),
                                is_public: Skillinfo.is_public,
                                attrs_are_visible:Skillinfo.attrs_are_visible,
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
                                output_variables:Skillinfo.output_variables ? Skillinfo.output_variables : arraytoobject(Thirdlyref.getFieldsValue()),
                            };
                            const param = objecttoarray(
                                arraytoobject(FirstSkillref.getFieldsValue()),
                            );
                            Fourthlyref.setFieldsValue(param);
                            Skill_update(data, res.data.app_id);
                            const createdData = {
                                ...createappdata('GET'),
                                app_id: res.data.app_id,
                            };
                            createappdata('SET', createdData);
                            pageKeyfun('4');
                            setskillmenudisabled({ ...skillmenudisabled, fourthly: false });
                        })
                        .catch(err => {});
                })
                .catch(err => {
                });
        } else {
            const data = {
                input_variables:Skillinfo.input_variables ? Skillinfo.input_variables : arraytoobject(FirstSkillref.getFieldsValue()),
                is_public: Skillinfo.is_public,
                attrs_are_visible:Skillinfo.attrs_are_visible,
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
                output_variables: Skillinfo.output_variables ? Skillinfo.output_variables : arraytoobject(Thirdlyref.getFieldsValue()),
            };
            const param = objecttoarray(arraytoobject(FirstSkillref.getFieldsValue()));
            Fourthlyref.setFieldsValue(param);
            Skill_update(data, app_id);
            pageKeyfun('4');
            setskillmenudisabled({ ...skillmenudisabled, fourthly: false });
        }
    };
    const firstjudgingcondition = (users: any, id?: Number) => {
        const firstusers = users.filter((item: any) => {
            return !item || !item.name || !item.content;
        });
        if (!users[0]) {
            message.warning(
                `${
                    id === 1
                        ? intl.formatMessage({ id: 'skill.message.inputerror1' })
                        : intl.formatMessage({ id: 'skill.message.inputerror2' })
                }`,
            );
            return true;
        } else if (firstusers.length !== 0) {
            message.warning(
                `${
                    id === 1
                        ? intl.formatMessage({ id: 'skill.message.inputerror3' })
                        : intl.formatMessage({ id: 'skill.message.inputerror4' })
                }`,
            );
            return true;
        }
        if (hasDuplicateField(users, 'name')) {
            message.warning(intl.formatMessage({ id: 'skill.message.inputerror5' }));
            return true;
        } else {
            return false;
        }
    };
    const hasDuplicateField = (array: any[], field: string) => {
        const uniqueValues = new Set();
        return array.some(item => {
            const value = item[field];
            return uniqueValues.has(value)
                ? uniqueValues.add(value)
                : uniqueValues.add(value) && false;
        });
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
            <Spin spinning={loading} size="large" className="mt-[112px]">
                <div
                    className="flex flex-col "
                    style={{
                        height: 'calc(100vh - 56px)',
                        width: 'calc(100vw - 230px)',
                        overflowY: 'scroll',
                        scrollbarWidth: 'none',
                    }}
                >
                    <div
                        className="px-[30px] "
                        style={{ overflowX: 'auto', minWidth: '960px', height: '100%' }}
                    >
                        <div className="w-full flex justify-center  mt-[30px]">
                            <div className="flex items-center  w-[900px] ">
                                <div className="mr-[10px] w-[16px] h-[16px]">
                                    <img
                                        src="/icons/flag.svg"
                                        alt=""
                                        className="w-[16px] h-[16px]"
                                    />
                                </div>
                                <div className="mr-[6px]  text-lg text-[#213044] font-medium">
                                    {createappdata('GET')?.app_id
                                        ? intl.formatMessage({ id: 'skill.Editingskill' })
                                        : intl.formatMessage({ id: 'skill.Creatingskill' })}
                                </div>
                                {Skillinfo?.app_publish_status === 1 ? (
                                    <div className="bg-[#1B64F3] text-[#fff] px-[7px] rounded font-normal text-xs flex items-center justify-center h-[18px]">
                                        {intl.formatMessage({ id: 'skill.havepublished' })}
                                    </div>
                                ) : (
                                    <div className=" bg-[#EEE]  text-[#999] px-[7px] rounded font-normal text-xs flex items-center justify-center h-[18px]">
                                        {intl.formatMessage({ id: 'skill.unpublish' })}
                                    </div>
                                )}
                            </div>
                        </div>
                        <div
                            style={{
                                display: pageKey === '1' ? 'flex' : 'none',
                                height: 'calc(100vh - 146px)',
                                justifyContent: 'center',
                            }}
                        >
                            <SkillFirst
                                FirstValue={FirstValue}
                                Skillinfo={Skillinfo}
                                setSkillInfo={setSkillInfo}
                                FirstSkillref={FirstSkillref}
                                Operationbentate={Operationbentate}
                                firstjudgingcondition={firstjudgingcondition}
                                pageKeyfun={pageKeyfun}
                                skillmenudisabled={skillmenudisabled}
                                setskillmenudisabled={setskillmenudisabled}
                            />
                        </div>
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
                        <div
                            style={{
                                display: pageKey === '3' ? 'flex' : 'none',
                                height: 'calc(100vh - 146px)',
                                justifyContent: 'center',
                            }}
                        >
                            <SkillThirdly
                                ThirdlyValue={ThirdlyValue}
                                handleBack={handleBack}
                                Thirdlyref={Thirdlyref}
                                Skillinfo={Skillinfo}
                                setSkillInfo={setSkillInfo}
                                Operationbentate={Operationbentate}
                                firstjudgingcondition={firstjudgingcondition}
                                pageKeyfun={pageKeyfun}
                                skillmenudisabled={skillmenudisabled}
                                setskillmenudisabled={setskillmenudisabled}
                                skillupdata={skillupdata}
                            />
                        </div>
                        <div
                            style={{
                                display: pageKey === '4' ? 'flex' : 'none',
                                height: 'calc(100vh - 146px)',
                                justifyContent: 'center',
                            }}
                        >
                            <SkillFourthly
                                FourthlyValue={FourthlyValue}
                                handleBack={handleBack}
                                Fourthlyref={Fourthlyref}
                                Skillinfo={Skillinfo}
                                skillid={skillid}
                                app_id={app_id}
                                Operationbentate={Operationbentate}
                            />
                        </div>
                    </div>
                </div>
            </Spin>
        </div>
    );
};
export default Skill;
