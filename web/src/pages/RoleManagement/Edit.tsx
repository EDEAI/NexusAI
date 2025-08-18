import { ArrowLeftOutlined } from '@ant-design/icons';
import { Button, Card, Checkbox, Form, Input, Spin, message } from 'antd';
import { useEffect, useState } from 'react';
import { useIntl } from '@umijs/max';
import { updateRole } from '@/api';

interface Permission {
    id: number;
    title: string;
}

interface RoleDetail {
    id: number;
    name: string;
    description: string;
    permissions: Permission[];
}

interface UpdateRoleForm {
    name: string;
    description: string;
    permissions: number[];
}

interface EditRoleProps {
    permissionsList: Permission[];
    roleDetail: RoleDetail | null;
    onClose: () => void;
}

const EditRole: React.FC<EditRoleProps> = ({ permissionsList, roleDetail, onClose }) => {
    const intl = useIntl();
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    // Set form values when roleDetail changes
    useEffect(() => {
        if (roleDetail) {
            const selectedPermissionIds = roleDetail.permissions.map(permission => permission.id);
            form.setFieldsValue({
                name: roleDetail.name,
                description: roleDetail.description,
                permissions: selectedPermissionIds,
            });
        }
    }, [roleDetail, form]);

    // Handle form submission
    const handleSubmit = async (values: UpdateRoleForm) => {
        if (!roleDetail) return;
        
        setSubmitting(true);
        try {
            const res = await updateRole({
                id: roleDetail.id,
                name: values.name,
                description: values.description,
                list: values.permissions,
            });
            if (res.code === 0) {
                message.success(
                    intl.formatMessage({ id: 'workflow.roleManagement.updateSuccess' })
                );
                onClose();
            } else {
                message.error(res.message || 'Failed to update role');
            }
        } catch (error) {
            console.error('Failed to update role:', error);
        } finally {
            setSubmitting(false);
        }
    };

    // Handle back button
    const handleBack = () => {
        onClose();
    };

    if (!roleDetail) {
        return (
            <div className="p-6">
                <div className="flex justify-center items-center h-64">
                    <Spin size="large" />
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="flex items-center mb-6">
                <Button
                    type="text"
                    icon={<ArrowLeftOutlined />}
                    onClick={handleBack}
                    className="mr-4"
                >
                    {intl.formatMessage({ id: 'workflow.roleManagement.back' })}
                </Button>
                <h1 className="text-2xl font-semibold">
                    {intl.formatMessage({ id: 'workflow.roleManagement.editRole' })}
                </h1>
            </div>

            <Card>
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                    disabled={submitting}
                >
                    <Form.Item
                        name="name"
                        label={intl.formatMessage({ id: 'workflow.roleManagement.roleName' })}
                        rules={[
                            {
                                required: true,
                                message: intl.formatMessage({
                                    id: 'workflow.roleManagement.roleNameRequired',
                                }),
                            },
                            {
                                max: 50,
                                message: intl.formatMessage({
                                    id: 'workflow.roleManagement.roleNameMaxLength',
                                }),
                            },
                        ]}
                    >
                        <Input
                            placeholder={intl.formatMessage({
                                id: 'workflow.roleManagement.roleNamePlaceholder',
                            })}
                        />
                    </Form.Item>

                    <Form.Item
                        name="description"
                        label={intl.formatMessage({ id: 'workflow.roleManagement.description' })}
                        rules={[
                            {
                                required: true,
                                message: intl.formatMessage({
                                    id: 'workflow.roleManagement.descriptionRequired',
                                }),
                            },
                            {
                                max: 200,
                                message: intl.formatMessage({
                                    id: 'workflow.roleManagement.descriptionMaxLength',
                                }),
                            },
                        ]}
                    >
                        <Input.TextArea
                            rows={4}
                            placeholder={intl.formatMessage({
                                id: 'workflow.roleManagement.descriptionPlaceholder',
                            })}
                        />
                    </Form.Item>

                    <Form.Item
                        name="permissions"
                        label={intl.formatMessage({ id: 'workflow.roleManagement.permissions' })}
                        rules={[
                            {
                                required: true,
                                message: intl.formatMessage({
                                    id: 'workflow.roleManagement.permissionsRequired',
                                }),
                            },
                        ]}
                    >
                        <Checkbox.Group className="w-full">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {permissionsList.map((permission) => (
                                    <Checkbox
                                        key={permission.id}
                                        value={permission.id}
                                        className="whitespace-nowrap"
                                    >
                                        {permission.title}
                                    </Checkbox>
                                ))}
                            </div>
                        </Checkbox.Group>
                    </Form.Item>

                    <Form.Item className="mb-0">
                        <div className="flex gap-4">
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={submitting}
                            >
                                {intl.formatMessage({ id: 'workflow.roleManagement.update' })}
                            </Button>
                            <Button onClick={handleBack}>
                                {intl.formatMessage({ id: 'workflow.roleManagement.cancel' })}
                            </Button>
                        </div>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
};

export default EditRole;