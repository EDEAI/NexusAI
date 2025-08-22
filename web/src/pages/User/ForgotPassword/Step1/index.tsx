import { Footer } from '@/components';
import { send_email_verification_code } from '@/api';
import { LockOutlined, MailOutlined } from '@ant-design/icons';
import { LoginForm, ProFormText } from '@ant-design/pro-components';
import { FormattedMessage, Helmet, history, useIntl } from '@umijs/max';
import { Button, Form, message } from 'antd';
import { createStyles } from 'antd-style';
import React, { useState, useEffect } from 'react';
import Settings from '../../../../../config/defaultSettings';

const useStyles = createStyles(({ token }) => {
    return {
        container: {
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            overflow: 'auto',
            backgroundImage:
                "url('https://mdn.alipayobjects.com/yuyan_qk0oxh/afts/img/V-_oS6r-i7wAAAAAAAAAAAAAFl94AQBr')",
            backgroundSize: '100% 100%',
        },
    };
});

const ForgotPasswordStep1: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const { styles } = useStyles();
    const intl = useIntl();
    const [email, setEmail] = useState<string>('');
    const [form] = Form.useForm();
    const [count, setCount] = useState<number>(0);
    const [initialValues, setInitialValues] = useState<{ email: string }>({ email: '' });

    useEffect(() => {
        const cachedEmail = localStorage.getItem('forgotPasswordEmail');
        if (cachedEmail) {
            setEmail(cachedEmail);
            setInitialValues({ email: cachedEmail });
            form.setFieldsValue({ email: cachedEmail });
        }
    }, [form]);

    const handleSubmit = async (values: { email: string }) => {
        setLoading(true);
        try {
            const response = await send_email_verification_code({ email: values.email });
            
            if (response.code === 0) {
                message.success(intl.formatMessage({
                    id: 'pages.forgotPassword.step1.sendSuccess',
                }));
                localStorage.removeItem('forgotPasswordEmail');
                history.push('/user/forgot-password/step2', { email: values.email });
            } else {
                message.error(response.message || intl.formatMessage({
                    id: 'pages.forgotPassword.step1.sendFailed',
                }));
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <Helmet>
                <title>
                    {intl.formatMessage({
                        id: 'pages.forgotPassword.step1.title',
                    })}
                    - {Settings.title}
                </title>
            </Helmet>
            <div
                style={{
                    flex: '1',
                    padding: '32px 0',
                }}
            >
                <LoginForm
                    form={form}
                    contentStyle={{
                        minWidth: 280,
                        maxWidth: '75vw',
                    }}
                    logo={<img alt="logo" src="/logo.svg" />}
                    title="NexusAI"
                    subTitle={intl.formatMessage({
                        id: 'pages.forgotPassword.step1.subtitle',
                    })}
                    initialValues={initialValues}
                    onFinish={async (values) => {
                        await handleSubmit(values as { email: string });
                    }}
                    submitter={{
                        render: (_, dom) => (
                            <div style={{ marginTop: 24 }}>
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    loading={loading}
                                    style={{ width: '100%' }}
                                >
                                    {intl.formatMessage({
                                        id: 'pages.forgotPassword.step1.sendCode',
                                    })}
                                </Button>
                                <Button
                                    style={{ width: '100%', marginTop: 8 }}
                                    onClick={() => history.push('/user/login')}
                                >
                                    {intl.formatMessage({
                                        id: 'pages.forgotPassword.backToLogin',
                                    })}
                                </Button>
                            </div>
                        ),
                    }}
                >
                    <ProFormText
                        name="email"
                        fieldProps={{
                            size: 'large',
                            prefix: <MailOutlined />,
                        }}
                        placeholder={intl.formatMessage({
                            id: 'pages.forgotPassword.step1.email.placeholder',
                        })}
                        rules={[
                            {
                                required: true,
                                message: (
                                    <FormattedMessage id="pages.forgotPassword.step1.email.required" />
                                ),
                            },
                            {
                                type: 'email',
                                message: (
                                    <FormattedMessage id="pages.forgotPassword.step1.email.invalid" />
                                ),
                            },
                        ]}
                        validateTrigger={['onChange', 'onBlur', 'onSubmit']}
                    />
                </LoginForm>
            </div>
            <Footer />
        </div>
    );
};

export default ForgotPasswordStep1;