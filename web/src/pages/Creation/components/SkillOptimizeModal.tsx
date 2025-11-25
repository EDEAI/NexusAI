import { Alert, Input, Modal } from 'antd';
import React from 'react';
import './optimize-modal.less';

const { TextArea } = Input;

interface SkillOptimizeModalProps {
    open: boolean;
    loading: boolean;
    title: string;
    description: string;
    placeholder: string;
    okText: string;
    cancelText: string;
    value: string;
    onChange: (value: string) => void;
    onOk: () => void;
    onCancel: () => void;
}

const SkillOptimizeModal: React.FC<SkillOptimizeModalProps> = ({
    open,
    loading,
    title,
    description,
    placeholder,
    okText,
    cancelText,
    value,
    onChange,
    onOk,
    onCancel,
}) => {
    const normalizedValue = value || '';
    const disableOk = loading || !normalizedValue.trim();

    return (
        <Modal
            open={open}
            title={title}
            onOk={onOk}
            onCancel={onCancel}
            okText={okText}
            cancelText={cancelText}
            okButtonProps={{ loading, disabled: disableOk }}
            cancelButtonProps={{ disabled: loading }}
            destroyOnClose
            maskClosable={!loading}
        >
            <div className="space-y-4 py-2">
                <Alert type="info" message={description} showIcon />
                <TextArea
                    rows={4}
                    showCount
                    className="optimize-textarea"
                    style={{ resize: 'vertical' }}
                    placeholder={placeholder}
                    value={value}
                    onChange={e => onChange(e.target.value)}
                    disabled={loading}
                />
            </div>
        </Modal>
    );
};

export default SkillOptimizeModal;
