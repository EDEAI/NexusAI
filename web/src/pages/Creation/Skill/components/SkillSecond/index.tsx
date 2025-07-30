import Callword from '@/components/callword';
import CodeEditor from '@/components/WorkFlow/components/Editor/CodeEditor';
import { useIntl } from '@umijs/max';
import { Button, Form, Select } from 'antd';
import React, { useEffect } from 'react';
//

interface ChildProps {
    SecondValue: (value: any) => void;
    handleBack: (value: any) => void;
    Skillinfo: any;
    setSkillInfo: any;
    SkillRelyOn: any;
    setSkillRelyOn: any;
    Secondref: any;
    setskillcodestate: any;
    setNewcode: any;
    pageKeyfun: any;
    skillmenudisabled: any;
    setskillmenudisabled: any;
}
const SkillSecond: React.FC<ChildProps> = ({
    SecondValue,
    handleBack,
    Skillinfo,
    setSkillInfo,
    SkillRelyOn,
    setSkillRelyOn,
    Secondref,
    setskillcodestate,
    setNewcode,
    pageKeyfun,
    skillmenudisabled,
    setskillmenudisabled,
}) => {
    const intl = useIntl();
    useEffect(() => {}, []);

    const SkillrelyInput = (value: any) => {
        setSkillRelyOn(value);
    };
    //
    const handleCodeChange = (e: any) => {
        if (e === '') {
            setskillcodestate(true);
        } else {
            setskillcodestate(false);
        }
        setNewcode(JSON.stringify({ python3: e }));
    };
    //
  

    //
    const updata = () => {
        pageKeyfun('3');
        setskillmenudisabled({ ...skillmenudisabled, thirdly: false });
    };
    return (
        <div style={{ height: '100%', width: '100%' }}>
            <div className="flex align-center justify-between mt-[30px]">
                <div className="text-base font-medium mb-[30px] text-[#333333]">
                    {intl.formatMessage({ id: 'skill.codesetting' })}
                </div>
            </div>
            <Form
                name="dynamic_form_nest_item"
                style={{ width: '100%' }}
                autoComplete="off"
                form={Secondref}
            >
                <Form.Item className="mb-[30px]">
                    {/* <div className='w-full'> */}
                    <div className="text-[#555555] text-xs mb-[15px]">
                        <Callword
                            className="font-medium"
                            name={intl.formatMessage({ id: 'skill.dependency' })}
                            title={intl.formatMessage({ id: 'skill.Callword.dependency' })}
                        />
                    </div>
                    <Select
                        mode="tags"
                        style={{ width: '100%' }}
                        value={SkillRelyOn}
                        onChange={SkillrelyInput}
                        tokenSeparators={[',']}
                    />
                </Form.Item>
                <div className="text-xs text-gray-500 p-3 whitespace-pre-line border-l-4 mb-2 border-gray-300 bg-gray-50">
                    {`${intl.formatMessage({ id: 'customcode.notice.title' })}:

${intl.formatMessage({ id: 'customcode.notice.file.write' })}：
${intl.formatMessage({ id: 'customcode.notice.file.write.desc' })}
${intl.formatMessage({ id: 'customcode.notice.file.write.example' })}

${intl.formatMessage({ id: 'customcode.notice.file.return' })}：
${intl.formatMessage({ id: 'customcode.notice.file.return.desc' })}
${intl.formatMessage({ id: 'customcode.notice.file.return.example' })}`}
                </div>
                <Form.Item>
                    <div className="">{intl.formatMessage({ id: 'skill.code' })}</div>
                    <div className="h-[345px]">
                        {/*Skillinfo && Skillinfo.code || */}
                        <CodeEditor
                            language="python3"
                            value={
                                Skillinfo && Skillinfo.code
                                    ? JSON.parse(Skillinfo.code).python3
                                    : ``
                            }
                            onChange={handleCodeChange}
                            title={`python3`}
                        ></CodeEditor>
                    </div>
                </Form.Item>
                <div>
                    <Button
                        type="primary"
                        className="mr-[20px]"
                        onClick={() => {
                            updata();
                        }}
                    >
                        {intl.formatMessage({ id: 'skill.btn.nextstep' })}
                    </Button>
                    {/* <Button
                        onClick={() => {
                            history.back();
                        }}
                    >
                        {intl.formatMessage({ id: 'skill.btn.back' })}
                    </Button> */}
                </div>
                <div className="h-[30px] w-1"></div>
            </Form>
        </div>
    );
};
export default SkillSecond;
