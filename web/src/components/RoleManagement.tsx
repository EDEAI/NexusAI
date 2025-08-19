import React, { useState, useEffect } from 'react';
import {
  Modal,
  Table,
  Button,
  Form,
  Input,
  Select,
  Space,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Tag,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { getRolesList, createRole, updateRole, deleteRole, getPermissionsList, getRoleDetail } from '@/api/index';

interface Role {
  id: number;
  name: string;
  description: string;
  status: number;
  created_at: string;
  updated_at: string | null;
  permissions?: number[]; // Permission IDs
  built_in: number; // 1 for built-in roles, 0 for custom roles
}

interface RoleManagementProps {
  visible: boolean;
  onClose: () => void;
}

const RoleManagement: React.FC<RoleManagementProps> = ({ visible, onClose }) => {
  const intl = useIntl();
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [form] = Form.useForm();

  // Fetch permissions data
  const fetchPermissions = async () => {
    try {
      const response = await getPermissionsList();
      if (response.code === 0) {
        setPermissions(response.data.list);
      }
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
    }
  };

  // Permission options
  const permissionOptions = permissions.map(perm => ({
    label: perm.title,
    value: perm.id,
  }));

  // Fetch roles data
  const fetchRoles = async () => {
    setLoading(true);
    try {
      const response = await getRolesList({ page: 1, page_size: 10, status: 1 });
      if (response.code === 0) {
        // Ensure each role has built_in field with default value 0
        const rolesWithBuiltIn = response.data.list.map((role: any) => ({
          ...role,
          built_in: role.built_in ?? 0,
        }));
        setRoles(rolesWithBuiltIn);
      }
    } catch (error) {
      message.error(intl.formatMessage({ id: 'role.fetchError', defaultMessage: 'Failed to fetch roles' }));
    } finally {
      setLoading(false);
    }
  };

  // Load roles and permissions when modal opens
  useEffect(() => {
    if (visible) {
      fetchRoles();
      fetchPermissions();
    }
  }, [visible]);

  // Handle create role
  const handleCreate = () => {
    setEditingRole(null);
    form.resetFields();
    setEditModalVisible(true);
  };

  // Handle edit role
  const handleEdit = async (role: Role) => {
    setEditingRole(role);
    // Fetch role detail to get complete role information including permissions
    try {
      const response = await getRoleDetail(role.id);
      if (response.code === 0 && response.data) {
        const roleData = response.data;
        const selectedPermissionIds = roleData.permissions.map(permission => permission.id);
        form.setFieldsValue({
          name: roleData.name,
          description: roleData.description,
          permissions: selectedPermissionIds,
        });
      }
    } catch (error) {
      console.error('Failed to fetch role detail:', error);
      // Fallback to existing role data
      form.setFieldsValue({
        name: role.name,
        description: role.description,
        permissions: role.permissions || [],
      });
    }
    setEditModalVisible(true);
  };

  // Handle delete role
  const handleDelete = async (roleId: number) => {
    try {
      const response = await deleteRole(roleId);
      if (response.code === 0) {
        message.success(intl.formatMessage({ id: 'role.deleteSuccess', defaultMessage: 'Role deleted successfully' }));
        fetchRoles();
      }
    } catch (error) {
      console.error('Failed to delete role:', error);
    }
  };

  // Handle form submit
  const handleSubmit = async (values: any) => {
    try {
      const roleData = {
        name: values.name,
        description: values.description,
        list: values.permissions || [], // Permission IDs
      };

      let response;
      if (editingRole) {
        response = await updateRole({ id: editingRole.id, ...roleData });
      } else {
        response = await createRole(roleData);
      }

      if (response.code === 0) {
        message.success(
          intl.formatMessage({
            id: editingRole ? 'role.updateSuccess' : 'role.createSuccess',
            defaultMessage: editingRole ? 'Role updated successfully' : 'Role created successfully',
          })
        );
        setEditModalVisible(false);
        fetchRoles();
      }
    } catch (error) {
      console.log('Failed to submit role:', error);
    }
  };

  // Table columns
  const columns = [
    {
      title: intl.formatMessage({ id: 'role.name', defaultMessage: 'Role Name' }),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: intl.formatMessage({ id: 'role.description', defaultMessage: 'Description' }),
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: intl.formatMessage({ id: 'role.actions', defaultMessage: 'Actions' }),
      key: 'actions',
      render: (_, record: Role) => (
        <Space size={4} style={{ display: 'flex', alignItems: 'center' }}>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={record.built_in === 1}
            style={{ padding: '0 4px', height: '24px', lineHeight: '24px' }}
          >
            {intl.formatMessage({ id: 'role.edit', defaultMessage: 'Edit' })}
          </Button>
          <Popconfirm
            title={intl.formatMessage({ id: 'role.confirmDelete', defaultMessage: 'Are you sure to delete this role?' })}
            onConfirm={() => handleDelete(record.id)}
            okText={intl.formatMessage({ id: 'role.confirm', defaultMessage: 'Confirm' })}
            cancelText={intl.formatMessage({ id: 'role.cancel', defaultMessage: 'Cancel' })}
            disabled={record.built_in === 1}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={record.built_in === 1}
              style={{ padding: '0 4px', height: '24px', lineHeight: '24px' }}
            >
              {intl.formatMessage({ id: 'role.delete', defaultMessage: 'Delete' })}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Modal
        title={intl.formatMessage({ id: 'role.title', defaultMessage: '' })}
        open={visible}
        onCancel={onClose}
        width={1000}
        footer={null}
        destroyOnClose
      >
        <Card>
          <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
            <Col>
              <h3>{intl.formatMessage({ id: 'role.list', defaultMessage: 'Role List' })}</h3>
            </Col>
            <Col>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreate}
              >
                {intl.formatMessage({ id: 'role.create', defaultMessage: 'Create Role' })}
              </Button>
            </Col>
          </Row>
          <Table
            columns={columns}
            dataSource={roles}
            rowKey="id"
            loading={loading}
            scroll={{ y: 340 }}
            locale={{
              emptyText: intl.formatMessage({ id: 'role.noData', defaultMessage: 'No role data' }),
            }}
          />
        </Card>
      </Modal>

      {/* Create/Edit Role Modal */}
      <Modal
        title={intl.formatMessage({
          id: editingRole ? 'role.editRole' : 'role.createRole',
          defaultMessage: editingRole ? 'Edit Role' : 'Create Role',
        })}
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => form.submit()}
        okText={intl.formatMessage({ id: 'role.save', defaultMessage: 'Save' })}
        cancelText={intl.formatMessage({ id: 'role.cancel', defaultMessage: 'Cancel' })}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label={intl.formatMessage({ id: 'role.name', defaultMessage: 'Role Name' })}
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'role.nameRequired', defaultMessage: 'Please enter role name' }),
              },
            ]}
          >
            <Input placeholder={intl.formatMessage({ id: 'role.namePlaceholder', defaultMessage: 'Enter role name' })} />
          </Form.Item>
          <Form.Item
            name="description"
            label={intl.formatMessage({ id: 'role.description', defaultMessage: 'Description' })}
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'role.descriptionRequired', defaultMessage: 'Please enter role description' }),
              },
            ]}
          >
            <Input.TextArea
              rows={3}
              placeholder={intl.formatMessage({ id: 'role.descriptionPlaceholder', defaultMessage: 'Enter role description' })}
            />
          </Form.Item>
          <Form.Item
            name="permissions"
            label={intl.formatMessage({ id: 'role.permissions', defaultMessage: 'Permissions' })}
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'role.permissionsRequired', defaultMessage: 'Please select permissions' }),
              },
            ]}
          >
            <Select
              mode="multiple"
              placeholder={intl.formatMessage({ id: 'role.selectPermissions', defaultMessage: 'Select permissions' })}
              options={permissionOptions}
            />
          </Form.Item>

        </Form>
      </Modal>
    </>
  );
};

export default RoleManagement;