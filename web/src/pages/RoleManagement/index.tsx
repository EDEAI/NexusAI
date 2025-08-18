import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Modal, Table, TableColumnsType, Tooltip, message } from 'antd';
import { useEffect, useState } from 'react';
import { history, useIntl } from '@umijs/max';
import { getRolesList, deleteRole } from '@/api';

interface Role {
    id: number;
    name: string;
    description: string;
    status: number;
    created_at: string;
    updated_at: string | null;
}

const RoleManagement: React.FC = () => {
    const intl = useIntl();
    const [loading, setLoading] = useState(false);
    const [rolesList, setRolesList] = useState<Role[]>([]);
    const [pagination, setPagination] = useState({
        current: 1,
        pageSize: 10,
        total: 0,
    });

    // Get roles list
    const fetchRolesList = async (page = 1, pageSize = 10) => {
        setLoading(true);
        try {
            const res = await getRolesList({ page, page_size: pageSize });
            if (res.code === 0) {
                setRolesList(res.data.list);
                setPagination({
                    current: page,
                    pageSize,
                    total: res.data.total_count,
                });
            }
        } catch (error) {
            console.error('Failed to fetch roles list:', error);
        } finally {
            setLoading(false);
        }
    };

    // Handle delete role
    const handleDelete = (roleId: number, roleName: string) => {
        Modal.confirm({
            title: intl.formatMessage({ id: 'workflow.roleManagement.deleteConfirmTitle' }),
            content: intl.formatMessage(
                { id: 'workflow.roleManagement.deleteConfirmContent' },
                { name: roleName }
            ),
            okText: intl.formatMessage({ id: 'workflow.roleManagement.confirm' }),
            cancelText: intl.formatMessage({ id: 'workflow.roleManagement.cancel' }),
            okType: 'danger',
            onOk: async () => {
                try {
                    const res = await deleteRole(roleId);
                    if (res.code === 0) {
                        message.success(
                            intl.formatMessage({ id: 'workflow.roleManagement.deleteSuccess' })
                        );
                        fetchRolesList(pagination.current, pagination.pageSize);
                    }
                } catch (error) {
                    console.error('Failed to delete role:', error);
                }
            },
        });
    };

    // Handle edit role
    const handleEdit = (roleId: number) => {
        history.push(`/role-management/edit/${roleId}`);
    };

    // Handle create role
    const handleCreate = () => {
        history.push('/role-management/create');
    };

    // Handle table change (pagination, sorting, filtering)
    const handleTableChange = (paginationInfo: any) => {
        fetchRolesList(paginationInfo.current, paginationInfo.pageSize);
    };

    // Table columns definition
    const columns: TableColumnsType<Role> = [
        {
            title: intl.formatMessage({ id: 'workflow.roleManagement.roleName' }),
            dataIndex: 'name',
            key: 'name',
            width: 200,
        },
        {
            title: intl.formatMessage({ id: 'workflow.roleManagement.description' }),
            dataIndex: 'description',
            key: 'description',
            ellipsis: {
                showTitle: false,
            },
            render: (description: string) => (
                <Tooltip placement="topLeft" title={description}>
                    {description}
                </Tooltip>
            ),
        },
        {
            title: intl.formatMessage({ id: 'workflow.roleManagement.createdAt' }),
            dataIndex: 'created_at',
            key: 'created_at',
            width: 180,
            render: (date: string) => new Date(date).toLocaleString(),
        },
        {
            title: intl.formatMessage({ id: 'workflow.roleManagement.actions' }),
            key: 'actions',
            width: 120,
            render: (_, record) => (
                <div className="flex gap-2">
                    <Button
                        type="text"
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(record.id)}
                        title={intl.formatMessage({ id: 'workflow.roleManagement.edit' })}
                    />
                    <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleDelete(record.id, record.name)}
                        title={intl.formatMessage({ id: 'workflow.roleManagement.delete' })}
                    />
                </div>
            ),
        },
    ];

    useEffect(() => {
        fetchRolesList();
    }, []);

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-semibold">
                    {intl.formatMessage({ id: 'workflow.roleManagement.title' })}
                </h1>
                <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleCreate}
                >
                    {intl.formatMessage({ id: 'workflow.roleManagement.createRole' })}
                </Button>
            </div>

            <Table<Role>
                columns={columns}
                dataSource={rolesList}
                loading={loading}
                rowKey="id"
                pagination={{
                    ...pagination,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total, range) =>
                        intl.formatMessage(
                            { id: 'workflow.roleManagement.pagination' },
                            { start: range[0], end: range[1], total }
                        ),
                }}
                onChange={handleTableChange}
            />
        </div>
    );
};

export default RoleManagement;