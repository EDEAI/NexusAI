import { Footer } from '@/components';

import { login } from '@/api';
import { getFakeCaptcha } from '@/services/ant-design-pro/login';
import { creationsearchdata } from '@/utils/useUser';
import { useUserInfo } from '@/hooks/useUserInfo';
import { LockOutlined, MobileOutlined, UserOutlined } from '@ant-design/icons';
import { LoginForm, ProFormCaptcha, ProFormText } from '@ant-design/pro-components';
import {
    FormattedMessage,
    Helmet,
    history,
    SelectLang,
    setLocale,
    useIntl,
    useModel,
} from '@umijs/max';
import { Alert, message, Tabs } from 'antd';
import { createStyles } from 'antd-style';
import React, { useState } from 'react';
import Settings from '../../../../config/defaultSettings';

const useStyles = createStyles(({ token }) => {
    return {
        action: {
            marginLeft: '8px',
            color: 'rgba(0, 0, 0, 0.2)',
            fontSize: '24px',
            verticalAlign: 'middle',
            cursor: 'pointer',
            transition: 'color 0.3s',
            '&:hover': {
                color: token.colorPrimaryActive,
            },
        },
        lang: {
            width: 42,
            height: 42,
            lineHeight: '42px',
            position: 'fixed',
            right: 16,
            borderRadius: token.borderRadius,
            ':hover': {
                backgroundColor: token.colorBgTextHover,
            },
        },
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

const Lang = () => {
    const { styles } = useStyles();
    const LangIconLoaded = () => <img src="/icons/lang.svg" />;
    return (
        <div className={styles.lang} data-lang>
            {SelectLang && <SelectLang icon={<LangIconLoaded />} />}
        </div>
    );
};

const LoginMessage: React.FC<{
    content: string;
}> = ({ content }) => {
    return (
        <Alert
            style={{
                marginBottom: 24,
            }}
            message={content}
            type="error"
            showIcon
        />
    );
};

const Login: React.FC = () => {
    const [userLoginState, setUserLoginState] = useState<API.LoginResult>({});
    const [type, setType] = useState<string>('account');
    const { initialState, setInitialState } = useModel('@@initialState');
    const { styles } = useStyles();
    const intl = useIntl();
    const { refreshUserInfo, userInfo } = useUserInfo();

    const fetchUserInfo = async () => {
        await refreshUserInfo();
        creationsearchdata('SET', 6, false, '');
        setTimeout(() => {
            setLocale(userInfo?.language == 'en' ? 'en-US' : 'zh-CN');
        }, 100);
    };

    const handleSubmit = async (values: API.LoginParams) => {
        try {
            //
            const { autoLogin, password, username } = values;

            const msg = await login({
                password,
                username,
            });
            console.log(msg);

            if (msg?.access_token) {
                const defaultLoginSuccessMessage = intl.formatMessage({
                    id: 'pages.login.success',
                    defaultMessage: '！',
                });
                // message.success(defaultLoginSuccessMessage);
                await fetchUserInfo();
                const urlParams = new URL(window.location.href).searchParams;
                history.push('/');
                return;
            }
            console.log(msg);
            //
            setUserLoginState({
                status: 'error',
                type: 'account',
            });
        } catch (error) {
            const defaultLoginFailureMessage = intl.formatMessage({
                id: 'pages.login.failure',
                defaultMessage: '，！',
            });
            console.log(error);
            message.error(defaultLoginFailureMessage);
        }
    };
    const { status, type: loginType } = userLoginState;

    return (
        <div className={styles.container}>
            <Helmet>
                <title>
                    {intl.formatMessage({
                        id: 'menu.login',
                        defaultMessage: '',
                    })}
                    - {Settings.title}
                </title>
            </Helmet>
            <Lang />
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
                    subTitle={intl.formatMessage({ id: 'pages.layouts.userLayout.title' })}
                    initialValues={{
                        autoLogin: true,
                    }}
                    onFinish={async values => {
                        await handleSubmit(values as API.LoginParams);
                    }}
                >
                    <Tabs activeKey={type} onChange={setType} centered items={[]} />

                    {status === 'error' && loginType === 'account' && (
                        <LoginMessage
                            content={intl.formatMessage({
                                id: 'pages.login.accountLogin.errorMessage',
                                defaultMessage: '',
                            })}
                        />
                    )}
                    {type === 'account' && (
                        <>
                            <ProFormText
                                name="username"
                                fieldProps={{
                                    size: 'large',
                                    prefix: <UserOutlined />,
                                }}
                                placeholder={intl.formatMessage({
                                    id: 'pages.login.username.placeholder',
                                    defaultMessage: ':',
                                })}
                                rules={[
                                    {
                                        required: true,
                                        message: (
                                            <FormattedMessage id="pages.login.username.required" />
                                        ),
                                    },
                                ]}
                            />
                            <ProFormText.Password
                                name="password"
                                fieldProps={{
                                    size: 'large',
                                    prefix: <LockOutlined />,
                                }}
                                placeholder={intl.formatMessage({
                                    id: 'pages.login.password.placeholder',
                                })}
                                rules={[
                                    {
                                        required: true,
                                        message: (
                                            <FormattedMessage id="pages.login.password.required" />
                                        ),
                                    },
                                ]}
                            />
                        </>
                    )}

                    {status === 'error' && loginType === 'mobile' && <LoginMessage content="" />}
                    {type === 'mobile' && (
                        <>
                            <ProFormText
                                fieldProps={{
                                    size: 'large',
                                    prefix: <MobileOutlined />,
                                }}
                                name="mobile"
                                placeholder={intl.formatMessage({
                                    id: 'pages.login.phoneNumber.placeholder',
                                })}
                                rules={[
                                    {
                                        required: true,
                                        message: (
                                            <FormattedMessage id="pages.login.phoneNumber.required" />
                                        ),
                                    },
                                    {
                                        pattern: /^1\d{10}$/,
                                        message: (
                                            <FormattedMessage id="pages.login.phoneNumber.invalid" />
                                        ),
                                    },
                                ]}
                            />
                            <ProFormCaptcha
                                fieldProps={{
                                    size: 'large',
                                    prefix: <LockOutlined />,
                                }}
                                captchaProps={{
                                    size: 'large',
                                }}
                                placeholder={intl.formatMessage({
                                    id: 'pages.login.captcha.placeholder',
                                })}
                                captchaTextRender={(timing, count) => {
                                    if (timing) {
                                        return `${count} ${intl.formatMessage({
                                            id: 'pages.getCaptchaSecondText',
                                        })}`;
                                    }
                                    return intl.formatMessage({
                                        id: 'pages.login.phoneLogin.getVerificationCode',
                                    });
                                }}
                                name="captcha"
                                rules={[
                                    {
                                        required: true,
                                        message: (
                                            <FormattedMessage id="pages.login.captcha.required" />
                                        ),
                                    },
                                ]}
                                onGetCaptcha={async phone => {
                                    const result = await getFakeCaptcha({
                                        phone,
                                    });
                                    if (!result) {
                                        return;
                                    }
                                }}
                            />
                        </>
                    )}
                    <div
                        style={{
                            marginTop: -14,
                            marginBottom: 8,
                            textAlign: 'right',
                        }}
                    >
                        <a
                            onClick={() => {
                                history.push('/user/forgot-password');
                            }}
                            style={{
                                color: '#1890ff',
                                textDecoration: 'none',
                            }}
                        >
                            {intl.formatMessage({
                                id: 'pages.login.forgotPassword',
                                defaultMessage: 'Forgot Password ?',
                            })}
                        </a>
                    </div>
                </LoginForm>
            </div>
            <Footer />
        </div>
    );
};

export default Login;
