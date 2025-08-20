import { Button, Form, Input, message } from 'antd';
import { createStyles } from 'antd-style';
import React, { useEffect, useState } from 'react';
import { history } from 'umi';
import { postRegisterUser } from '../../../api/team';
import { useIntl } from 'umi';
import { use } from '@reactuses/core';

interface DataNodeType {
    value: string;
    label: string;
    children?: DataNodeType[];
}

const useStyles = createStyles(({ token }) => {
    return {
        container: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'start',
            height: '100vh',
            overflow: 'auto',
            backgroundImage:
                "url('https://mdn.alipayobjects.com/yuyan_qk0oxh/afts/img/V-_oS6r-i7wAAAAAAAAAAAAAFl94AQBr')",
            backgroundSize: '100% 100%',
        },
    };
});

const formItemLayout = {
    labelCol: {
        xs: { span: 24 },
        sm: { span: 8 },
    },
    wrapperCol: {
        xs: { span: 24 },
        sm: { span: 16 },
    },
};

const tailFormItemLayout = {
    wrapperCol: {
        xs: {
            span: 24,
            offset: 0,
        },
        sm: {
            span: 16,
            offset: 8,
        },
    },
};

const Register: React.FC = () => {
    const [form] = Form.useForm();
    const { styles } = useStyles();
    const intl = useIntl(); 
    const [team,setTeam]=useState(null);
    const [myEmail, setmyEmail] = useState<any>(''); 
    useEffect(() => {
        aginEmail();
    }, []);
    const aginEmail = () => {
        let params = new URLSearchParams(window.location.search);
        setmyEmail(params.get('email'));
        setTeam(params.get('team'))
    };
    const onFinish = async (values: any) => {
        console.log('Received values of form: ', values);
        const param = {
            email: myEmail,
            password: values.password,
            nickname: values.nickname,
            position: values.position,
        };
        const res = await postRegisterUser(param);
        if (res.code === 0) {
            message.success(intl.formatMessage({ id: 'register.success' }));
            history.push('/user/login');
        } else {
            message.error(intl.formatMessage({ id: 'register.error' }));
        }
    };
    return (
        <div className={styles.container}>
            <Form
                {...formItemLayout}
                form={form}
                name="register"
                onFinish={onFinish}
                initialValues={{ residence: ['zhejiang', 'hangzhou', 'xihu'], prefix: '86' }}
                style={{ minWidth: 350 }}
                scrollToFirstError
            >
                <Form.Item name="header">
                    <div className="text-base mt-10 pl-32 w-full">
                        <div className="w-12 h-12 ">
                            <img alt="logo" src="/logo.svg" />
                        </div>
                        <div className="text-3xl font-semibold mb-3 mt-4">{intl.formatMessage({ id: 'register.join' })} {team}</div>
                        <div className="w-96 text-xs">{intl.formatMessage({ id: 'register.invite' })} {team}</div>
                    </div>
                </Form.Item>
                <Form.Item name="email" label={intl.formatMessage({ id: 'register.email' })}>
                    <div className="text-base">{myEmail && myEmail}</div>
                </Form.Item>

                <Form.Item
                    name="nickname"
                    label={intl.formatMessage({ id: 'register.nickname' })}
                    tooltip={intl.formatMessage({ id: 'register.nickname.tooltip' })}
                    rules={[{ required: true, message: intl.formatMessage({ id: 'register.nickname.required' }), whitespace: true }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="position"
                    label={intl.formatMessage({ id: 'register.position' })}
                    tooltip={intl.formatMessage({ id: 'register.position.tooltip' })}
                    rules={[{ required: true, message: intl.formatMessage({ id: 'register.position.required' }), whitespace: true }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    name="password"
                    label={intl.formatMessage({ id: 'register.password' })}
                    rules={[
                        {
                            required: true,
                            message: intl.formatMessage({ id: 'register.password.required' }),
                        },
                    ]}
                    hasFeedback
                >
                    <Input.Password />
                </Form.Item>
                <Form.Item
                    name="confirm"
                    label={intl.formatMessage({ id: 'register.confirm' })}
                    dependencies={['password']}
                    hasFeedback
                    rules={[
                        {
                            required: true,
                            message: intl.formatMessage({ id: 'register.confirm.required' }),
                        },
                        ({ getFieldValue }) => ({
                            validator(_, value) {
                                if (!value || getFieldValue('password') === value) {
                                    return Promise.resolve();
                                }
                                return Promise.reject(new Error(intl.formatMessage({ id: 'register.confirm.error' })));
                            },
                        }),
                    ]}
                >
                    <Input.Password />
                </Form.Item>
                <Form.Item {...tailFormItemLayout}>
                    <Button type="primary" htmlType="submit" block>
                        {intl.formatMessage({ id: 'register.register' })}
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default Register;
