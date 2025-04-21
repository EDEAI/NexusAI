/*
 * @LastEditors: biz
 */
import React, { useState, useEffect } from 'react';
import { Modal, Upload, Avatar, message, Popover } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { headportrait } from '@/utils/useUser';

interface SelectAvatarProps {
  value?: string;
  onChange?: (value: string) => void;
  CardData: any;
  setCardData: any;
}

const defaultAvatars = [
  'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=4',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=5',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=6',
];

const SelectAvatar: React.FC<SelectAvatarProps> = ({ value, onChange, CardData, setCardData }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAvatar, setSelectedAvatar] = useState(value || defaultAvatars[0]);

  useEffect(() => {}, []);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSelectAvatar = (avatar: string) => {
    setSelectedAvatar(avatar);
    onChange?.(avatar);
    handleCloseModal();
  };

  const uploadProps: UploadProps = {
    name: 'avatar',
    showUploadList: false,
    beforeUpload: (file) => {
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('You can only upload image files!');
        return false;
      }
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = reader.result as string;
        setCardData({ ...CardData, icon: base64, id: null });
      };
      return false;
    },
  };

  const contentPhone = () => {
    return (
      <div className="flex flex-col">
        <div className="flex justify-start items-center flex-wrap w-40">
          {headportrait('all').map((item: any) => {
            return (
              <div
                key={item.id}
                className="w-8 h-8 bg-[#F4F8F1] rounded-lg mr-1.5 flex items-center justify-center m-0.5 cursor-pointer"
                onClick={() => {
                  pitchphone(item);
                }}
              >
                <img src={item.image} alt="" />
              </div>
            );
          })}
        </div>
        <div className="mt-2 flex justify-center">
          <Upload {...uploadProps}>
            <button className="flex items-center px-2 py-1 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
              <UploadOutlined className="mr-1" />
              Upload Avatar
            </button>
          </Upload>
        </div>
      </div>
    );
  };

  const pitchphone = (data: any) => {
    setCardData({ ...CardData, icon: data.image, id: data.id });
  };

  return (
    <Popover content={contentPhone} trigger="click" placement="bottomLeft">
      <div className="w-8 h-8 bg-[#F4F8F1] rounded-lg mr-1.5 flex items-center justify-center m-0.5 cursor-pointer">
        <img
          src={headportrait('single', CardData.id ? CardData.id : CardData.icon)}
          alt=""
        />
      </div>
    </Popover>
  );
};

export default SelectAvatar;
