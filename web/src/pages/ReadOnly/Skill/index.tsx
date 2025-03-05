import { GetskillInfo, PutskillUpdate } from '@/api/skill';
import { ObjectVariable, Variable as SkillVariable } from '@/py2js/variables.js';
import {
    ArrowLeftOutlined,
    CodeOutlined,
    CreditCardOutlined,
    FileDoneOutlined,
    FileTextOutlined,
} from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import type { MenuProps } from 'antd';
import { Button, Form, Menu, message } from 'antd';
import React, { useEffect, useState } from 'react';
import SkillFirst from './components/SkillFirst';
import SkillSecond from './components/SkillSecond';
import SkillThirdly from './components/SkillThirdly';
import SkillFourthly from './components/skillFourthly';
type MenuItem = Required<MenuProps>['items'][number];

const Skill: React.FC = () => {
    const intl = useIntl();
    const [FirstSkillref] = Form.useForm(); //ref
    const [Secondref] = Form.useForm(); //ref
    const [Thirdlyref] = Form.useForm(); //ref
    const [Fourthlyref] = Form.useForm(); //ref
    const [Procedure, setProcedure] = useState(0); //
    const [pageKey, pageKeyfun] = useState('1'); //
    const [Skillinfo, setSkillInfo] = useState<any>(null); //
    const [app_id, setApp_id] = useState<any>(null); //id
    const [SkillRelyOn, setSkillRelyOn] = useState<any>(null); //
    const [Operationbentate, setOperationbentate] = useState<any>(null); //
    const [skillcodestate, setskillcodestate] = useState<any>(false);
    const [Newcode, setNewcode] = useState<any>(null);
    const items: MenuItem[] = [
        {
            key: '1',
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
            icon: <CodeOutlined />,
            label: intl.formatMessage({ id: 'skill.menu.code' }),
            disabled:SkillRelyOn && Skillinfo.attrs_are_visible == 0,
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
            icon: <CreditCardOutlined />,
            label: intl.formatMessage({ id: 'skill.menu.output' }),
            disabled:SkillRelyOn && Skillinfo.attrs_are_visible !== 1,
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
        getSkill();
    }, []);


    const getSkill = async () => {
        let params = new URLSearchParams(window.location.search);
        // setOperationbentate(params.get('type'))
        setApp_id(params.get('app_id'));
        const res = await GetskillInfo(params.get('app_id'), params.get('type'));
        console.log(res, 'res-===>');
        if (res.code == 0) {
            setSkillInfo(res.data);

            setOperationbentate(res.data.publish_status === 1 ? 'true' : 'false');
            if (res.data.publish_status == 1) {
                message.warning(intl.formatMessage({ id: 'skill.message.listwarning' }), 5);
            }
            const firstvalue = objecttoarray(res.data.input_variables);

            FirstSkillref.setFieldsValue(firstvalue);

            setSkillRelyOn(res.data.dependencies ? res.data.dependencies.python3 : []);
            const Thirdlyvalue = objecttoarray(res.data.output_variables);
            Thirdlyref.setFieldsValue(Thirdlyvalue);
        } else {
            message.error(intl.formatMessage({ id: 'skill.message.listerror' }));
        }
    };

    const objecttoarray = (obj?: any) => {
        console.log(!!obj && !!obj.properties, 'obj');
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

    const Skill_update = async (value: any) => {
        if (Operationbentate === 'false') {
            const param = {
                app_id: app_id,
                data: value,
            };
            const res = await PutskillUpdate(param);
            console.log(res);
            if (res.code == 0) {
                getSkill();
            }
        }
    };

    const returnList = () => {
        SkillMenuClick({
            key: pageKey,
            keyPath: [],
            item: undefined,
            domEvent: undefined,
        });
        history.back();
    };

    const FirstValue = (value: any) => {
        // Skill_update(value)
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
        if (pageKey == '1') {
            const data = {
                input_variables: arraytoobject(FirstSkillref.getFieldValue()),
                is_public: Skillinfo.is_public,
            };
            FirstValue(data);
            pageKeyfun(e.key);
        }
        pageKeyfun(e.key);
    };

    const firstjudgingcondition = (users: any, id?: Number) => {
        console.log(users, 'users');
        const firstusers = users.filter((item: any) => {
            return !item || !item.name || !item.content;
        });
        console.log('firstusers', firstusers, !users[0]);
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

            <div
                className="flex flex-col h-full w-[300px]"
                style={{ height: 'calc(100vh - 56px)' }}
            >
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
                        <div className="flex items-center  w-[900px]">
                            <div className="mr-[10px] w-[16px] h-[16px]">
                                <img src="/icons/flag.svg" alt="" className="w-[16px] h-[16px]" />
                            </div>
                            <div className="mr-[6px]  text-lg text-[#213044] font-medium">
                                {Skillinfo ? Skillinfo.nickname : ''}
                                {intl.formatMessage({ id: 'skill.skills' })}
                            </div>
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
                            Operationbentate={Operationbentate}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Skill;
