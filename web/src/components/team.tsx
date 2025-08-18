import { UserOutlined, SwitcherOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import type { TableProps } from 'antd';
import { Avatar, Button, Input, message, Modal, Select, Space, Table, Typography } from 'antd';
import React, { useEffect, useState } from 'react';
import gandUp from '../../public/icons/gandUp.svg';
import { getTeamList, postInviteUser, getRoleList, getUserTeams, switchUserTeam } from '../api/team';
import { userinfo } from '../api/index';
import { userinfodata } from '../utils/useUser';
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
}

const Team: React.FC<TeamProps> = ({ isModalOpen, setIsModalOpen }) => {
    const intl = useIntl();
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
            render: (_, record) => (
                <Space size="middle" key={_}>
                    {/* <a>Invite {record.name}</a> */}
                    <div>
                        {record.role == 1
                            ? intl.formatMessage({ id: 'user.teamAdmin', defaultMessage: '' })
                            : record.role_title}
                    </div>
                </Space>
            ),
        },
    ];
    const [teammemberList, setTeammemberList] = useState<any>(null);
    const [isModalOpen2, setIsModalOpen2] = useState(false);
    const [EmailList, setEmaillist] = useState('');
    const [processedEmails, setProcessedEmails] = useState<string[]>([]);
    const [roleid, setRoleid] = useState('admin_user');
    const [isBtn, setIsBtn] = useState(true);
    const [isModalOpen3, setIsModalOpen3] = useState(false);
    const [gainEmail, setGainEmail] = useState(null);
    const [roleList, setRoleList] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    
    const [teams, setTeams] = useState<any[]>([]);
    const [currentTeam, setCurrentTeam] = useState<any>(null);
    const [loadingTeams, setLoadingTeams] = useState(false);
    
    const handleTeamChange = async (team: any) => {
        try {
            const res = await switchUserTeam(team.id);
            if (res.code === 0) {
                setCurrentTeam(team);
                message.success(intl.formatMessage({ id: 'component.team.switchSuccess' }));
                if (res.data && res.data.access_token) {
                    localStorage.setItem('token', res.data.access_token);
                }
                
                // Get latest user info to update role cache
                const userInfoRes = await userinfo();
                if (userInfoRes.code === 0 && userInfoRes.data) {
                    userinfodata('SET', userInfoRes.data);
                }
                
                window.location.reload();
            }
        } finally {

        }
    };

    const TeamList = async (param: boolean) => {
        if (param) {
            const res = await getTeamList();
            setTeammemberList(res.data);
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

                // Get current team ID from user_info API
                const userInfoRes = await userinfo();
                const currentTeamId = userInfoRes?.data?.team_id;
                
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

    const fetchRoleList = async () => {
        try {
            const res = await getRoleList();
            if (res.code === 0) {
                setRoleList(res.data.list || []);
            }
        } catch (error) {
            console.error('Failed to fetch role list:', error);
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
                                fetchRoleList();
                            }}
                            disabled={userinfodata('GET')?.role !== 1}
                        >
                            {intl.formatMessage({ id: 'user.add', defaultMessage: '' })}
                        </Button>
                    </div>
                </div>

                <Table
                    columns={columns}
                    dataSource={teammemberList && teammemberList.team_member_list}
                    pagination={{ pageSize: 20 }}
                    scroll={{ y: 360 }}
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
                            ...roleList.map(role => ({
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
