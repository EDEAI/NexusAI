import { userinfodata } from '@/utils/useUser';
import {
    DeploymentUnitOutlined,
    LogoutOutlined,
    SettingOutlined,
    TeamOutlined,
    UserOutlined,
} from '@ant-design/icons';
import { history, useIntl, useModel } from '@umijs/max';
import { Spin } from 'antd';
import { createStyles } from 'antd-style';
import { stringify } from 'querystring';
import React, { useCallback, useState, useEffect } from 'react';
import { flushSync } from 'react-dom';
import HeaderDropdown from '../HeaderDropdown';
import Modelsetup from '../ModelSetup';
import Team from '../team';
import AccountSettings from './AccountSettings';
import RoleManagement from '../RoleManagement';

export type GlobalHeaderRightProps = {
    menu?: boolean;
    children?: React.ReactNode;
};

export const AvatarName = () => {
    const [nickname, setNickname] = useState<string>('');
    
    useEffect(() => {
        // Initial load
        const userInfo = userinfodata('GET');
        setNickname(userInfo?.nickname || '');
        
        // Listen for storage changes
        const handleStorageChange = () => {
            const userInfo = userinfodata('GET');
            setNickname(userInfo?.nickname || '');
        };
        
        // Custom event for same-tab updates
        const handleCustomEvent = (event: CustomEvent) => {
            if (event.detail?.type === 'userInfoUpdated') {
                handleStorageChange();
            }
        };
        
        window.addEventListener('storage', handleStorageChange);
        window.addEventListener('userInfoUpdated', handleCustomEvent as EventListener);
        
        return () => {
            window.removeEventListener('storage', handleStorageChange);
            window.removeEventListener('userInfoUpdated', handleCustomEvent as EventListener);
        };
    }, []);
    
    return (
        <div className=" w-[100px] truncate">
            <span className="">{nickname}</span>
        </div>
    );
};

const useStyles = createStyles(({ token }) => {
    return {
        action: {
            display: 'flex',
            height: '48px',
            marginLeft: 'auto',
            overflow: 'hidden',
            alignItems: 'center',
            padding: '0 8px',
            cursor: 'pointer',
            borderRadius: token.borderRadius,
            '&:hover': {
                backgroundColor: token.colorBgTextHover,
            },
        },
    };
});

export const AvatarDropdown: React.FC<GlobalHeaderRightProps> = ({ menu, children }) => {
    const loginOut = async () => {
        const { search, pathname } = window.location;
        const urlParams = new URL(window.location.href).searchParams;

        const redirect = urlParams.get('redirect');
        localStorage.removeItem('token');

        if (window.location.pathname !== '/user/login' && !redirect) {
            history.replace({
                pathname: '/user/login',
                search: stringify({
                    redirect: pathname + search,
                }),
            });
        }
    };
    const { styles } = useStyles();
    const intl = useIntl();
    const { initialState, setInitialState } = useModel('@@initialState');
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const [ModelSetupOpen, setModelSetupOpen] = useState<boolean>(false);
    const [isAccountSettingsOpen, setIsAccountSettingsOpen] = useState<boolean>(false);
    const [isRoleManagementOpen, setIsRoleManagementOpen] = useState<boolean>(false);

    const onMenuClick = useCallback(
        event => {
            const { key } = event;
            if (key === 'logout') {
                flushSync(() => {
                    setInitialState(s => ({ ...s, currentUser: undefined }));
                });
                loginOut();
                return;
            } else if (key === 'team') {
                console.log('team');
                setIsModalOpen(true);
            } else if (key === 'Modelsetup') {
                setModelSetupOpen(true);
            } else if (key === 'accountSettings') {
                setIsAccountSettingsOpen(true);
            } else if (key === 'roleManagement') {
                setIsRoleManagementOpen(true);
            } else {
                history.push(`/account/${key}`);
            }
        },
        [setInitialState],
    );

    const loading = (
        <span className={styles.action}>
            <Spin
                size="small"
                style={{
                    marginLeft: 8,
                    marginRight: 8,
                }}
            />
        </span>
    );

    if (!initialState) {
        return loading;
    }

    // const { currentUser } = initialState;

    // if (!currentUser || !currentUser.name) {
    //   return loading;
    // }

    const menuItems = [
        {
            key: 'accountSettings',
            icon: <SettingOutlined />,
            label: intl.formatMessage({
                id: 'workflow.menu.accountSettings',
                defaultMessage: '',
            }),
        },
        {
            key: 'roleManagement',
            icon: <UserOutlined />,
            label: intl.formatMessage({
                id: 'workflow.menu.roleManagement',
                defaultMessage: 'Role Management',
            }),
        },
        ...(menu
            ? [
                  {
                      key: 'center',
                      icon: <UserOutlined />,
                      label: intl.formatMessage({
                          id: 'workflow.menu.personalCenter',
                          defaultMessage: '',
                      }),
                  },
                  {
                      key: 'settings',
                      icon: <SettingOutlined />,
                      label: intl.formatMessage({
                          id: 'workflow.menu.personalSettings',
                          defaultMessage: '',
                      }),
                  },
                  {
                      type: 'divider' as const,
                  },
              ]
            : []),

        {
            key: 'team',
            icon: <TeamOutlined />,
            disabled: false,
            label: intl.formatMessage({
                id: 'workflow.menu.teamAndMembers',
                defaultMessage: '',
            }),
        },
        {
            key: 'Modelsetup',
            icon: <DeploymentUnitOutlined />,
            disabled: userinfodata('GET')?.role == 1 ? false : true,
            label: intl.formatMessage({
                id: 'workflow.menu.modelSetup',
                defaultMessage: '',
            }),
        },

        {
            key: 'logout',
            icon: <LogoutOutlined />,
            label: intl.formatMessage({ id: 'workflow.menu.logout', defaultMessage: '' }),
        },
    ];

    return (
        <div>
            <HeaderDropdown
                menu={{
                    selectedKeys: [],
                    onClick: onMenuClick,
                    items: menuItems,
                }}
            >
                {children}
            </HeaderDropdown>
            <Team isModalOpen={isModalOpen} setIsModalOpen={setIsModalOpen} />
            <Modelsetup isModalOpen={ModelSetupOpen} setIsModalOpen={setModelSetupOpen} />
            <AccountSettings isModalOpen={isAccountSettingsOpen} setIsModalOpen={setIsAccountSettingsOpen} />
            <RoleManagement visible={isRoleManagementOpen} onClose={() => setIsRoleManagementOpen(false)} />
        </div>
    );
};
