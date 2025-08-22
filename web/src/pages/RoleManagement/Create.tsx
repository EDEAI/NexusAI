import { ArrowLeftOutlined } from '@ant-design/icons';
import { Button, Card, Checkbox, Form, Input, message } from 'antd';
import { useState } from 'react';
import { history, useIntl } from '@umijs/max';
import { createRole } from '@/api';

interface Permission {
    id: number;
    title: string;
    status: number;
    created_at: string;
    updated_at: string | null;
}

interface CreateRoleForm {
    name: string;
    description: string;
    permissions: number[];
}

interface CreateRoleProps {
    permissionsList: Permission[];
}

const CreateRole: React.FC<CreateRoleProps> = ({ permissionsList }) => {
    const intl = useIntl();
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);

    // Handle form submission
    const handleSubmit = async (values: CreateRoleForm) => {
        setSubmitting(true);
        try {
            const res = await createRole({
                name: values.name,
                description: values.description,
                list: values.permissions,
            });
            if (res.code === 0) {
                message.success(
                    intl.formatMessage({ id: 'workflow.roleManagement.createSuccess' })
                );
                history.push('/role-management');
            }
        } catch (error) {
            console.error('Failed to create role:', error);
        } finally {
            setSubmitting(false);
        }
    };

    // Handle back button
    const handleBack = () => {
        history.push('/role-management');
    };



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
                    {intl.formatMessage({ id: 'workflow.roleManagement.createRole' })}
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
                                {intl.formatMessage({ id: 'workflow.roleManagement.create' })}
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

export default CreateRole;