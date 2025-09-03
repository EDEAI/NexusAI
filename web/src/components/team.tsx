import { UserOutlined, SwitcherOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import type { TableProps } from 'antd';
import { Avatar, Button, Input, message, Modal, Select, Space, Table, Tooltip, Typography } from 'antd';
import React, { useEffect, useState } from 'react';
import gandUp from '../../public/icons/gandUp.svg';
import { getTeamList, postInviteUser, getUserTeams, switchUserTeam } from '../api/team';
import { getRolesList, switchMemberRole, type RoleListResponse } from '../api/index';
import type { REQ_TYPE } from '../api/request';
import { useUserInfo } from '../hooks/useUserInfo';
import { usePermissions } from '../hooks/usePermissions';
import { PERMISSION_IDS } from '../utils/permissions';
import TeamSwitcher from './TeamSwitcher';
const { TextArea } = Input;
const { Paragraph, Text } = Typography;

export type TeamProps = {
    isModalOpen: boolean;
    setIsModalOpen: any;
};

interface DataType {
    // key: string;
    // name: string;
    // age: string;
    avatar: string;
    email: string;
    last_login_time: string;
    nickname: string;
    position: string;
    role: number;
    role_title: string;
    role_id: number; // Add role_id for role matching
    user_id?: number; // Add user_id for role switching
}

const Team: React.FC<TeamProps> = ({ isModalOpen, setIsModalOpen }) => {
    const intl = useIntl();
    const { userInfo, hasPermission, isTeamAdmin } = usePermissions();
    const { refreshUserInfo } = useUserInfo();
    const columns: TableProps<DataType>['columns'] = [
        {
            title: intl.formatMessage({ id: 'user.name', defaultMessage: '' }),
            dataIndex: 'name',
            key: 'name',
            width: '30%',
            render: (_, record) => (
                <div key={_}>
                    <div>{record.nickname}</div>
                    <div className="text-gray-300">{record.email}</div>
                </div>
            ),
        },
        {
            title: intl.formatMessage({ id: 'user.position', defaultMessage: '' }),
            dataIndex: 'position',
            key: 'position',
            width: '20%',
            render: (_, record) => (
                <div key={_}>{record.position || '-'}</div>
            ),
        },
        {
            title: intl.formatMessage({
                id: 'user.lastActivityTime',
                defaultMessage: '',
            }),
            dataIndex: 'age',
            key: 'age',
            width: '25%',
            render: (_, record) => <div key={_}>{record.last_login_time}</div>,
        },
        {
            title: intl.formatMessage({ id: 'user.role', defaultMessage: '' }),
            key: 'action',
            width: '25%',
            render: (_, record) => {
                // Get current user info to check if this is the user's own role
                const isOwnRole = userInfo && record.user_id === userInfo.uid;
                
                return (
                    <Space size="middle" key={_}>
                        {/* <a>Invite {record.name}</a> */}
                        {isTeamAdmin() && !isOwnRole ? (
                            // User with role assignment permission can change roles, but not their own
                            <Select
                                value={record.role === 1 ? 'admin' : record.role_id}
                                style={{ width: 150 }}
                                onChange={(value) => handleRoleChange(record, value)}
                                // Allow changing admin role if user has permission
                            >
                                <Select.Option value="admin">
                                    <Tooltip title={intl.formatMessage({ id: 'user.teamAdminDesc', defaultMessage: 'Team administrator with full access rights' })}>
                                        <div>{intl.formatMessage({ id: 'user.teamAdmin', defaultMessage: '' })}</div>
                                    </Tooltip>
                                </Select.Option>
                                {allRolesList.map(role => (
                                    <Select.Option key={role.id} value={role.id}>
                                        <Tooltip title={role.description || role.name}>
                                            <div>{role.name}</div>
                                        </Tooltip>
                                    </Select.Option>
                                ))}
                            </Select>
                        ) : (
                            // User without permission or viewing own role can only view roles
                            <div>
                                {record.role == 1
                                    ? intl.formatMessage({ id: 'user.teamAdmin', defaultMessage: '' })
                                    : record.role_title}
                            </div>
                        )}
                    </Space>
                );
            },
        },
    ];
    const [teammemberList, setTeammemberList] = useState<any>([]);
    const [isModalOpen2, setIsModalOpen2] = useState(false);
    const [EmailList, setEmaillist] = useState('');
    const [processedEmails, setProcessedEmails] = useState<string[]>([]);
    const [roleid, setRoleid] = useState('admin_user');
    const [isBtn, setIsBtn] = useState(true);
    const [isModalOpen3, setIsModalOpen3] = useState(false);
    const [gainEmail, setGainEmail] = useState(null);

    const [loading, setLoading] = useState(false);
    const [allRolesList, setAllRolesList] = useState<any[]>([]); // Store all roles from getRolesList
    const [currentUserRole, setCurrentUserRole] = useState<number | null>(null); // Store current user's role
    
    const [teams, setTeams] = useState<any[]>([]);
    const [currentTeam, setCurrentTeam] = useState<any>(null);
    const [loadingTeams, setLoadingTeams] = useState(false);
    
    // Search related state
    const [searchKeyword, setSearchKeyword] = useState('');
    const [searchLoading, setSearchLoading] = useState(false);
    
    // Add useEffect to fetch roles and user info on component mount
    useEffect(() => {
        fetchAllRolesList();
        getCurrentUserRole();
    }, []);
    
    const handleTeamChange = async (team: any) => {
        try {
            const res = await switchUserTeam(team.id);
            if (res.code === 0) {
                setCurrentTeam(team);
                message.success(intl.formatMessage({ id: 'component.team.switchSuccess' }));
                if (res.data && res.data.access_token) {
                    localStorage.setItem('token', res.data.access_token);
                }
                
                // Refresh user info to update role cache
                await refreshUserInfo();
                
                window.location.reload();
            }
        } finally {

        }
    };

    const TeamList = async (param: boolean, keyword?: string) => {
        if (param) {
            const res = await getTeamList(keyword ? { keyword } : undefined);
            // Ensure team_member_list contains user_id field
            const memberList = res.data.team_member_list || [];
            setTeammemberList(memberList);
        }
    };

    // Handle search functionality
    const handleSearch = async () => {
        if (!searchKeyword.trim()) {
            return;
        }
        
        setSearchLoading(true);
        try {
            await TeamList(true, searchKeyword.trim());
        } catch (error) {
            console.error('Search failed:', error);
            message.error('Search failed');
        } finally {
            setSearchLoading(false);
        }
    };

    // Handle clear search
    const handleClearSearch = async () => {
        setSearchKeyword('');
        setSearchLoading(true);
        try {
            await TeamList(true); // Load all members without search
        } catch (error) {
            console.error('Clear search failed:', error);
        } finally {
            setSearchLoading(false);
        }
    };

    const fetchUserTeams = async () => {
        setLoadingTeams(true);
        try {
            const res = await getUserTeams();
            if (res.code === 0 && res.data && res.data.teams) {
                const teamsData = res.data.teams.map((team: any) => ({
                    id: team.id,
                    name: team.name,
                    role: team.role,
                    roleName: team.role_name,
                    position: team.position,
                    memberCount: team.member_count
                }));
                setTeams(teamsData);

                // Get current team ID from user info
                const currentTeamId = userInfo?.team_id;
                
                if (teamsData.length > 0) {
                    if (currentTeamId) {
                        const currentTeam = teamsData.find(team => team.id === currentTeamId);
                        setCurrentTeam(currentTeam);
                    } else {
                        setCurrentTeam(teamsData[0]);
                    }
                }
            }
        } finally {
            setLoadingTeams(false);
        }
    };



    // Fetch all roles using getRolesList for role switching
    const fetchAllRolesList = async () => {
        try {
            const res = await getRolesList({ page: 1, page_size: 100, status: 2 }); // Get active roles
            if (res.code === 0) {
                setAllRolesList(res.data?.list || []);
            }
        } catch (error) {
            console.error('Failed to fetch all roles list:', error);
        }
    };

    // Get current user role from userinfo
    const getCurrentUserRole = async () => {
        try {
            if (userInfo) {
                setCurrentUserRole(userInfo.role);
            }
        } catch (error) {
            console.error('Failed to get current user role:', error);
        }
    };

    // Handle role change for team members
    const handleRoleChange = async (record: DataType, newRoleId: number | string) => {
        if (!record.user_id) {
            return; // Cannot change role without user_id
        }

        try {
            setLoading(true);
            
            // Determine role and role_id based on new role selection
            let role: number;
            let roleId: number;
            
            if (newRoleId === 'admin') {
                // Changing to team admin
                role = 1;
                roleId = 0;
            } else {
                // Changing to other roles
                role = 2;
                roleId = Number(newRoleId);
            }
            
            const res = await switchMemberRole({
                user_id: record.user_id,
                role: role,
                role_id: roleId
            });

            if (res.code === 0) {
                message.success(res.data.msg);
                // Refresh team member list
                TeamList(true);
            } else {
                message.error(res.data.msg);
            }
        } catch (error) {
            console.error('Failed to change member role:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCancel1 = () => {
        setIsModalOpen(false);
    };

    const handleCancel2 = () => {
        setIsModalOpen2(false);
    };

    const Rolechange = (e: any) => {

        setRoleid(e);
    };

    const handleCancel3 = () => {
        setIsModalOpen3(false);
    };

    const Emaillistonchange = (e: any) => {
        const textValue = e.target.value;
        setEmaillist(textValue);
        
        // Split by lines, trim whitespace, and filter out empty emails
        const emailArray = textValue
            .split('\n')
            .map((email: string) => email.trim())
            .filter((email: string) => email.length > 0);
        
        setProcessedEmails(emailArray);
        
        if (!!textValue.trim()) {
            setIsBtn(false);
        } else {
            setIsBtn(true);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        // Ensure Enter key works for new lines
        if (e.key === 'Enter') {
            e.stopPropagation();
            // Don't prevent default - let the textarea handle the Enter key naturally
        }
    };

    const Sendaninvitation = async (sendEmail: number = 0) => {
        let newintcode = [];
        const pattern =
            /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/; //
        
        processedEmails.forEach((item: any) => {
            if (pattern.test(item)) {
                newintcode.push(item);
            } else {
                console.log('');
            }
        });

        if (newintcode.length > 0) {
            setLoading(true);
            // Handle role parameter: admin_user for team admin, role id for member roles
            const roleParam = roleid === 'admin_user' ? 'admin_user' : roleid;

            const params = {
                role: roleParam,
                email_list: newintcode,
                send_email: sendEmail,
            };
            const res = await postInviteUser(params);
            setLoading(false);

            if (res.code == 0) {
                if (sendEmail === 1) {
                    setIsModalOpen2(false);
                    setEmaillist('');
                    setProcessedEmails([]);
                } else {
                    // Check if email_list is empty array
                    if (res.data.email_list && res.data.email_list.length === 0) {
                        setIsModalOpen2(false);
                        setEmaillist('');
                        setProcessedEmails([]);
                    } else {
                        setGainEmail(res.data.email_list);
                        setIsModalOpen3(true);
                        setIsModalOpen2(false);
                        setEmaillist('');
                        setProcessedEmails([]);
                    }
                }
                message.success(res.data.msg);
            }
        } else {
            message.error(
                intl.formatMessage({
                    id: 'user.enterValidEmail',
                    defaultMessage: '',
                }),
            );
        }
    };

    return (
        <div className="m-4">
            <Modal
                width={900}
                title={intl.formatMessage({ id: 'user.teamMember', defaultMessage: '' })}
                open={isModalOpen}
                footer={false}
                onCancel={handleCancel1}
                afterOpenChange={(open) => {
                    if (open) {
                        // Fetch teams data when modal is opened
                        fetchUserTeams();
                        TeamList(true);
                        fetchAllRolesList();
                    }
                }}
            >
                <div className="h-12 bg-gray-50 rounded flex items-center justify-between px-4 mb-8 ">
                    <div className="flex items-center">
                        <TeamSwitcher 
                            currentTeam={currentTeam}
                            teams={teams}
                            onTeamChange={handleTeamChange}
                            loading={loadingTeams}
                        />
                    </div>
                    <div>
                        <Button 
                            icon={<UserOutlined />} 
                            onClick={() => {
                                setIsModalOpen2(true);
                                fetchAllRolesList();
                            }}
                            disabled={!isTeamAdmin() || userInfo?.team_type === 2}
                        >
                            {intl.formatMessage({ id: 'user.add', defaultMessage: '' })}
                        </Button>
                    </div>
                </div>

                {/* Search functionality */}
                <div className="mb-4 flex items-center gap-2">
                    <Input
                        placeholder={intl.formatMessage({
                            id: 'role.search.placeholder',
                            defaultMessage: 'Search by account or name',
                        })}
                        value={searchKeyword}
                        onChange={(e) => setSearchKeyword(e.target.value)}
                        onPressEnter={handleSearch}
                        style={{ width: 300 }}
                    />
                    <Button 
                        type="primary" 
                        onClick={handleSearch}
                        loading={searchLoading}
                    >
                        {intl.formatMessage({
                            id: 'role.search.button',
                            defaultMessage: 'Search',
                        })}
                    </Button>
                    {searchKeyword && (
                        <Button 
                            onClick={handleClearSearch}
                        >
                            {intl.formatMessage({
                                id: 'role.search.clear',
                                defaultMessage: 'Clear',
                            })}
                        </Button>
                    )}
                </div>

                <Table
                    columns={columns}
                    dataSource={teammemberList}
                    rowKey="user_id"
                    pagination={{ pageSize: 20 }}
                    scroll={{ y: 340 }}
                />
            </Modal>
            <Modal
                width={500}
                title={intl.formatMessage({
                    id: 'user.addTeamMember',
                    defaultMessage: '',
                })}
                open={isModalOpen2}
                footer={false}
                onCancel={handleCancel2}
            >
                <div className="font-normal text-gray-600 mb-8">
                    {intl.formatMessage({
                        id: 'user.accessTeamData',
                        defaultMessage: '。',
                    })}
                </div>
                <p>{intl.formatMessage({ id: 'user.email', defaultMessage: '' })}</p>
                <div className="mb-8">
                    <TextArea
                        placeholder={intl.formatMessage({
                            id: 'user.enterMultipleEmailsSeparatedByComma',
                            defaultMessage: '(,)',
                        })}
                        value={EmailList}
                        onChange={Emaillistonchange}
                        rows={4}
                        style={{ resize: 'vertical' }}
                        onKeyDown={handleKeyDown}
                    />
                </div>
                <div className="mb-8">
                    <Select
                        style={{ width: 450 }}
                        placeholder={intl.formatMessage({
                            id: 'user.inviteAsMemberUser',
                            defaultMessage: '',
                        })}
                        onChange={Rolechange}
                        value={roleid}
                        options={[
                            {
                                value: 'admin_user',
                                label: intl.formatMessage({
                                    id: 'user.teamAdmin',
                                    defaultMessage: '',
                                }),
                                title: intl.formatMessage({
                                    id: 'user.teamAdminDesc',
                                    defaultMessage: '',
                                }),
                            },
                            ...allRolesList.map(role => ({
                                value: role.id,
                                label: role.name,
                                title: role.description || role.name, // Tooltip text
                            }))
                        ]}
                    />
                </div>
                <Button 
                    type="primary" 
                    block 
                    disabled={isBtn || loading} 
                    onClick={() => Sendaninvitation(1)}
                    loading={loading}
                    className="mb-4"
                >
                    {intl.formatMessage({ id: 'user.sendInvitationEmail', defaultMessage: '' })}
                </Button>
                <Button 
                    type="default" 
                    block 
                    disabled={isBtn || loading} 
                    onClick={() => Sendaninvitation(0)}
                    loading={loading}
                >
                    {intl.formatMessage({ id: 'user.sendInvitation', defaultMessage: '' })}
                </Button>
            </Modal>
            <Modal width={500} open={isModalOpen3} footer={false} onCancel={handleCancel3}>
                <div className="font-semibold text-base mt-8 mb-2 ">
                    {intl.formatMessage({
                        id: 'user.invitationSent',
                        defaultMessage: '',
                    })}
                </div>
                <div className=" text-gray-600 mb-6">
                    {intl.formatMessage({
                        id: 'user.invitationSentLoginNexusAI',
                        defaultMessage: '， NEXUS AI',
                    })}
                </div>
                <div className=" text-gray-600 mb-4">
                    {intl.formatMessage({ id: 'user.invitationLink', defaultMessage: '' })}
                </div>
                {gainEmail &&
                    gainEmail.map((item: any, index: number) => {
                        return (
                            <div
                                className="h-12 w-full bg-gray-50 rounded flex items-center justify-between px-4 mb-8 font-normal"
                                key={index}
                            >
                                <div className="overflow-hidden whitespace-nowrap text-ellipsis w-11/12">
                                    {' '}
                                    {item}
                                </div>
                                <Text copyable={{ text: item }} />
                            </div>
                        );
                    })}

                <div className="flex justify-end items-center">
                    <Button type="primary" disabled={isBtn} onClick={handleCancel3}>
                        {intl.formatMessage({ id: 'user.ok', defaultMessage: '' })}
                    </Button>
                </div>
            </Modal>
        </div>
    );
};
export default Team;
