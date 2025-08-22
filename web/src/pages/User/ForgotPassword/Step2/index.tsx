import { Footer } from '@/components';
import { LockOutlined, SafetyOutlined } from '@ant-design/icons';
import { LoginForm, ProFormText } from '@ant-design/pro-components';
import { FormattedMessage, Helmet, history, useIntl, useLocation } from '@umijs/max';
import { Button, message } from 'antd';
import { createStyles } from 'antd-style';
import React, { useState, useRef } from 'react';
import Settings from '../../../../../config/defaultSettings';
import { verify_email_code } from '@/api';

interface LocationState {
  email: string;
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

const ForgotPasswordStep2: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const isResendingRef = useRef(false);
    const { styles } = useStyles();
    const intl = useIntl();
    const location = useLocation();
    const state = location.state as LocationState;
    const email = state?.email || '';

    const handleSubmit = async (values: { code: string }) => {
        // Guard: if user clicked resend, skip verification entirely
        if (isResendingRef.current) {
            isResendingRef.current = false;
            return;
        }
        setLoading(true);
        try {
            const response = await verify_email_code({ email, verification_code: values.code });
            
            if (response.code === 0) {
                message.success(intl.formatMessage({
                    id: 'pages.forgotPassword.step2.verifySuccess',
                }));
                localStorage.removeItem('forgotPasswordEmail');
                history.push('/user/forgot-password/step3', { email, code: values.code });
            } else {
                message.error(response.message || intl.formatMessage({
                    id: 'pages.forgotPassword.step2.verifyFailed',
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
                        id: 'pages.forgotPassword.step2.title',
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
                        id: 'pages.forgotPassword.step2.subtitle',
                    })}
                    onSubmitCapture={(e) => {
                        if (isResendingRef.current) {
                            e.preventDefault();
                            e.stopPropagation();
                            isResendingRef.current = false;
                        }
                    }}
                    onFinish={async (values) => {
                        await handleSubmit(values as { code: string });
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
                                        id: 'pages.forgotPassword.step2.verifyCode',
                                    })}
                                </Button>
                                <Button
                                    style={{ width: '100%', marginTop: 8 }}
                                    htmlType="button"
                                    onMouseDown={(e) => {
                                        e.preventDefault();
                                    }}
                                    onClick={() => {
                                        isResendingRef.current = true;
                                        localStorage.setItem('forgotPasswordEmail', email);
                                        history.push('/user/forgot-password');
                                    }}
                                >
                                    {intl.formatMessage({ id: 'pages.forgotPassword.step2.resend' })}
                                </Button>
                            </div>
                        ),
                    }}
                >
                    <ProFormText
                        name="code"
                        fieldProps={{
                            size: 'large',
                            prefix: <SafetyOutlined />,
                            maxLength: 6,
                        }}
                        placeholder={intl.formatMessage({
                            id: 'pages.forgotPassword.step2.code.placeholder',
                        })}
                        rules={[
                            {
                                required: true,
                                message: (
                                    <FormattedMessage id="pages.forgotPassword.step2.code.required" />
                                ),
                            },
                            {
                                pattern: /^[A-Za-z0-9]{6}$/,
                                message: (
                                    <FormattedMessage id="pages.forgotPassword.step2.code.format" />
                                ),
                            },
                        ]}
                        validateTrigger={['onChange', 'onBlur', 'onSubmit']}
                    />
                    <div style={{ marginTop: 16, textAlign: 'center', color: '#666' }}>
                        {intl.formatMessage(
                            { id: 'pages.forgotPassword.step2.emailSent' },
                            { email }
                        )}
                        <br />
                        {intl.formatMessage({
                            id: 'pages.forgotPassword.step2.emailSentNotice',
                        })}
                    </div>
                </LoginForm>
            </div>
            <Footer />
        </div>
    );
};

export default ForgotPasswordStep2;