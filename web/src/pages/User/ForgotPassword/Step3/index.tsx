import { Footer } from '@/components';
import { LockOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { LoginForm, ProFormText } from '@ant-design/pro-components';
import { FormattedMessage, Helmet, history, useIntl, useLocation } from '@umijs/max';
import { Button, message } from 'antd';
import { createStyles } from 'antd-style';
import React, { useState } from 'react';
import Settings from '../../../../../config/defaultSettings';
import { reset_password } from '@/api';

interface LocationState {
  email: string;
  code: string;
}

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

const ForgotPasswordStep3: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const { styles } = useStyles();
    const intl = useIntl();
    const location = useLocation();
    const state = location.state as LocationState;
    const email = state?.email || '';
    const code = state?.code || '';

    const handleSubmit = async (values: { password: string; confirmPassword: string }) => {
        if (values.password !== values.confirmPassword) {
            message.error(intl.formatMessage({
                id: 'pages.forgotPassword.step3.passwordMismatch',
            }));
            return;
        }
        
        setLoading(true);
        try {
            const response = await reset_password({ email, password: values.password, confirm_password: values.confirmPassword });
            
            if (response.code === 0) {
                message.success(intl.formatMessage({
                    id: 'pages.forgotPassword.step3.resetSuccess',
                }));
                localStorage.removeItem('forgotPasswordEmail');
                history.push('/user/login');
            } else {
                message.error(response.message || intl.formatMessage({
                    id: 'pages.forgotPassword.step3.resetFailed',
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
                        id: 'pages.forgotPassword.step3.title',
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
                    contentStyle={{
                        minWidth: 280,
                        maxWidth: '75vw',
                    }}
                    logo={<img alt="logo" src="/logo.svg" />}
                    title="NexusAI"
                    subTitle={intl.formatMessage({
                        id: 'pages.forgotPassword.step3.subtitle',
                    })}
                    onFinish={async (values) => {
                        await handleSubmit(values as { password: string; confirmPassword: string });
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
                                        id: 'pages.forgotPassword.step3.resetPassword',
                                    })}
                                </Button>
                            </div>
                        ),
                    }}
                >
                    <ProFormText.Password
                        name="password"
                        fieldProps={{
                            size: 'large',
                            prefix: <LockOutlined />,
                        }}
                        placeholder={intl.formatMessage({
                            id: 'pages.forgotPassword.step3.password.placeholder',
                        })}
                        rules={[
                            {
                                required: true,
                                message: (
                                    <FormattedMessage id="pages.forgotPassword.step3.password.required" />
                                ),
                            },
                        ]}
                    />
                    <ProFormText.Password
                        name="confirmPassword"
                        fieldProps={{
                            size: 'large',
                            prefix: <SafetyCertificateOutlined />,
                        }}
                        placeholder={intl.formatMessage({
                            id: 'pages.forgotPassword.step3.confirmPassword.placeholder',
                        })}
                        rules={[
                            {
                                required: true,
                                message: (
                                    <FormattedMessage id="pages.forgotPassword.step3.confirmPassword.required" />
                                ),
                            },
                            ({ getFieldValue }) => ({
                                validator(_, value) {
                                    if (!value || getFieldValue('password') === value) {
                                        return Promise.resolve();
                                    }
                                    return Promise.reject(
                                        new Error(
                                            intl.formatMessage({
                                                id: 'pages.forgotPassword.step3.confirmPassword.mismatch',
                                            })
                                        )
                                    );
                                },
                            }),
                        ]}
                    />

                </LoginForm>
            </div>
            <Footer />
        </div>
    );
};

export default ForgotPasswordStep3;