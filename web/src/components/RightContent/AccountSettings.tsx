import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Button, message, Tabs } from 'antd';
import { UserOutlined, LockOutlined, IdcardOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { userinfo, updateProfile, changePassword } from '@/api';
import { userinfodata } from '@/utils/useUser';

type AccountSettingsProps = {
  isModalOpen: boolean;
  setIsModalOpen: (open: boolean) => void;
};

const AccountSettings: React.FC<AccountSettingsProps> = ({ isModalOpen, setIsModalOpen }) => {
  const intl = useIntl();
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [userInfo, setUserInfo] = useState<any>(null);

  // Get user info when modal opens
  useEffect(() => {
    if (isModalOpen) {
      fetchUserInfo();
    }
  }, [isModalOpen]);

  const fetchUserInfo = async () => {
    try {
      const response = await userinfo();
      setUserInfo(response.data);
      form.setFieldsValue({
        nickname: response.data.nickname || response.data.nickname,
        position: response.data.position,
      });
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  };

  const handleProfileSubmit = async (values: any) => {
    setLoading(true);
    try {
      await updateProfile({
        nickname: values.nickname,
        position: values.position,
      });
      message.success(intl.formatMessage({ id: 'user.profileUpdateSuccess' }));
      // Update local user info
      const updatedUserInfo = {
        ...userInfo,
        nickname: values.nickname,
        position: values.position,
      };
      setUserInfo(updatedUserInfo);
      // Update localStorage for global user info
      userinfodata('SET', updatedUserInfo);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (values: any) => {
    setPasswordLoading(true);
    try {
      await changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
        confirm_password: values.confirm_password,
      });
      message.success(intl.formatMessage({ id: 'user.passwordChangeSuccess' }));
      passwordForm.resetFields();
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleCancel = () => {
    setIsModalOpen(false);
    form.resetFields();
    passwordForm.resetFields();
  };

  const tabItems = [
    {
      key: 'profile',
      label: intl.formatMessage({ id: 'user.accountSettings' }),
      children: (
        <Form
          form={form}
          layout="vertical"
          onFinish={handleProfileSubmit}
          autoComplete="off"
        >
          <Form.Item label={intl.formatMessage({ id: 'user.email' })}>
            <div style={{ padding: '4px 11px', color: '#000', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
              {userInfo?.email}
            </div>
          </Form.Item>
          
          <Form.Item
            label={intl.formatMessage({ id: 'user.name' })}
            name="nickname"
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'user.nameRequired' }),
              },
            ]}
          >
            <Input
              placeholder={intl.formatMessage({ id: 'user.nameRequired' })}
              prefix={<UserOutlined />}
            />
          </Form.Item>
          
          <Form.Item
            label={intl.formatMessage({ id: 'user.position' })}
            name="position"
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'user.positionRequired' }),
              },
            ]}
          >
            <Input
              placeholder={intl.formatMessage({ id: 'user.positionRequired' })}
              prefix={<IdcardOutlined />}
            />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              {intl.formatMessage({ id: 'user.save' })}
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'password',
      label: intl.formatMessage({ id: 'user.changePassword' }),
      children: (
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handlePasswordSubmit}
          autoComplete="off"
        >
          <Form.Item
            label={intl.formatMessage({ id: 'user.oldPassword' })}
            name="old_password"
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'user.oldPasswordRequired' }),
              },
            ]}
          >
            <Input.Password
              placeholder={intl.formatMessage({ id: 'user.oldPasswordRequired' })}
              prefix={<LockOutlined />}
            />
          </Form.Item>
          
          <Form.Item
            label={intl.formatMessage({ id: 'user.newPassword' })}
            name="new_password"
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'user.newPasswordRequired' }),
              },
            ]}
          >
            <Input.Password
              placeholder={intl.formatMessage({ id: 'user.newPasswordRequired' })}
              prefix={<LockOutlined />}
            />
          </Form.Item>
          
          <Form.Item
            label={intl.formatMessage({ id: 'user.confirmPassword' })}
            name="confirm_password"
            dependencies={['new_password']}
            rules={[
              {
                required: true,
                message: intl.formatMessage({ id: 'user.confirmPasswordRequired' }),
              },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(
                    new Error(intl.formatMessage({ id: 'user.passwordMismatch' }))
                  );
                },
              }),
            ]}
          >
            <Input.Password
              placeholder={intl.formatMessage({ id: 'user.confirmPasswordRequired' })}
              prefix={<LockOutlined />}
            />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={passwordLoading}>
              {intl.formatMessage({ id: 'user.save' })}
            </Button>
          </Form.Item>
        </Form>
      ),
    },
  ];

  return (
    <Modal
      title={intl.formatMessage({ id: 'user.accountSettings' })}
      open={isModalOpen}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      <Tabs items={tabItems} />
    </Modal>
  );
};

export default AccountSettings;