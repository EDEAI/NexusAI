import Callword from '@/components/callword';
import { useIntl } from '@umijs/max';
import { Form, Select } from 'antd';
import React, { useEffect } from 'react';
import CodeEditor from '../../../../../components/WorkFlow/components/Editor/CodeEditor';
//

interface ChildProps {
    SecondValue: (value: any) => void;
    handleBack: (value: any) => void; //
    Skillinfo: any;
    setSkillInfo: any;
    SkillRelyOn: any;
    setSkillRelyOn: any;
    Secondref: any;
    setskillcodestate: any;
    setNewcode: any;
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
}) => {
    const intl = useIntl();
    useEffect(() => {}, []);

    const readed = {
        readOnly: true,
    };
    const disabled = {
        disabled: true,
    };
    const SkillrelyInput = (value: any) => {
        console.log(value);
        setSkillRelyOn(value);
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
                <Form.Item

                    className="mb-[30px]"
                >
                    {/* <div className='w-full'> */}
                    <div className="text-[#555555] text-xs mb-[15px] font-medium">
                        <Callword
                            name={intl.formatMessage({ id: 'skill.dependency' })}
                            title={intl.formatMessage({ id: 'skill.Callword.dependency' })}
                        />
                    </div>
                    <Select
                        {...disabled}
                        mode="tags"
                        variant="filled"
                        style={{ width: '100%' }}
                        value={SkillRelyOn}
                        tokenSeparators={[',']}
                    />
                </Form.Item>
                <Form.Item>
                    <div className="text-[#555555] text-xs mb-[15px] font-medium">
                        {intl.formatMessage({ id: 'skill.code' })}
                    </div>
                    <div className="h-80">
                        <CodeEditor
                            readOnly
                            language="python3"
                            value={
                                Skillinfo && Skillinfo.code
                                    ? JSON.parse(Skillinfo.code).python3
                                    : `def main(arg1: int) -> dict:
    return {
        "result": (arg1 + 2) * 3,
    }`
                            }
                            title={`python3`}
                        ></CodeEditor>
                    </div>
                </Form.Item>
            </Form>
        </div>
    );
};
export default SkillSecond;
