/*
 * @LastEditors: biz
 */
import { headportrait } from '@/utils/useUser';
import { Popover, Upload, message, Modal } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import React, { useEffect, useState } from 'react';
import { getUploadUrl } from '@/api/createkb';
import { useIntl } from '@umijs/max';
import Cropper from 'react-cropper';
import 'cropperjs/dist/cropper.css';

interface ChildProps {
    CardData: any;
    setCardData: any;
}

const profilephoto: React.FC<ChildProps> = ({ CardData, setCardData }) => {
    const intl = useIntl();
    const [cropperVisible, setCropperVisible] = useState(false);
    const [imageUrl, setImageUrl] = useState('');
    const [cropper, setCropper] = useState<any>(null);
    const CROP_SIZE = 200;
   
    useEffect(() => {}, []);

    const handleBeforeUpload = (file: File) => {
        const isImage = file.type.startsWith('image/');
        const isLt2M = file.size / 1024 / 1024 < 2;
        
        if (!isImage) {
            message.error(intl.formatMessage({ id: 'workflow.uploadFileErrorType' }));
            return false;
        }
        if (!isLt2M) {
            message.error(intl.formatMessage({ id: 'workflow.uploadFileErrorText' }));
            return false;
        }

        // 创建图片预览
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            setImageUrl(reader.result as string);
            setCropperVisible(true);
        };
        return false;
    };

    const handleCrop = () => {
        if (cropper) {
            const croppedCanvas = cropper.getCroppedCanvas({
                width: CROP_SIZE,
                height: CROP_SIZE,
                minWidth: CROP_SIZE,
                minHeight: CROP_SIZE,
                maxWidth: CROP_SIZE,
                maxHeight: CROP_SIZE,
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high',
            });
            
            croppedCanvas.toBlob(async (blob: Blob) => {
                const formData = new FormData();
                formData.append('file', blob, 'avatar.png');
                
                const uploadUrl = await getUploadUrl();
                fetch(uploadUrl, {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`,
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(res => {
                    if (res.code === 0 && res.data?.path) {
                        setCardData({ ...CardData, avatar: res.data.path,avatar_show: res.data.path_show });
                        message.success(intl.formatMessage({ id: 'workflow.uploadSuccess' }));
                    } else {
                        message.error(intl.formatMessage({ id: 'workflow.uploadError' }));
                    }
                })
                .catch(() => {
                    message.error(intl.formatMessage({ id: 'workflow.uploadError' }));
                });
            }, 'image/png', 1);
            setCropperVisible(false);
        }
    };

    const contentPhone = () => {
        return (
            <div className="flex flex-col gap-2">
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
                <Upload
                    name="file"
                    accept=".jpg,.png,.jpeg"
                    showUploadList={false}
                    beforeUpload={handleBeforeUpload}
                >
                    <div className="w-full flex items-center justify-center p-2 cursor-pointer hover:bg-gray-100 rounded">
                        <UploadOutlined className="mr-2" />
                        {intl.formatMessage({ id: 'workflow.uploadAvatar' })}
                    </div>
                </Upload>
            </div>
        );
    };
   
    const pitchphone = (data: any) => {
        setCardData({ 
            ...CardData, 
            icon: data.image, 
            id: data.id,
            avatar: null ,// 清除自定义头像
            avatar_show: null,
        });
    };

    return (
        <>
            <Popover content={contentPhone} trigger="click" placement="bottomLeft">
                <div className="w-8 h-8 bg-[#F4F8F1] rounded-lg mr-1.5 flex items-center justify-center m-0.5 cursor-pointer">
                    <img
                        src={CardData.avatar_show ||CardData.avatar|| headportrait('single', CardData.id ? CardData.id : CardData.icon)}
                        alt=""
                        className='rounded'
                    />
                </div>
            </Popover>
            <Modal
                title={intl.formatMessage({ id: 'workflow.cropAvatar' })}
                open={cropperVisible}
                onOk={handleCrop}
                onCancel={() => setCropperVisible(false)}
                width={800}
            >
                <div className="w-full h-[400px]">
                    <Cropper
                        src={imageUrl}
                        style={{ height: '100%', width: '100%' }}
                        aspectRatio={1}
                        guides={true}
                        cropBoxResizable={true}
                        cropBoxMovable={true}
                        viewMode={2}
                        dragMode="move"
                        autoCropArea={1}
                        background={false}
                        responsive={true}
                        restore={false}
                        checkCrossOrigin={false}
                        checkOrientation={false}
                        modal={true}
                        highlight={true}
                        center={true}
                        zoomOnWheel={true}
                        wheelZoomRatio={0.1}
                        minContainerWidth={CROP_SIZE}
                        minContainerHeight={CROP_SIZE}
                        minCanvasWidth={CROP_SIZE}
                        minCanvasHeight={CROP_SIZE}
                        minCropBoxWidth={CROP_SIZE}
                        minCropBoxHeight={CROP_SIZE}
                        onInitialized={(instance) => {
                            setCropper(instance);
                            // 初始化时自动调整裁剪框大小
                            instance.setCropBoxData({
                                width: CROP_SIZE,
                                height: CROP_SIZE,
                            });
                        }}
                        ready={() => {
                            if (cropper) {
                                // 确保图片最短边不小于裁剪框大小
                                const imageData = cropper.getImageData();
                                const minDimension = Math.min(imageData.width, imageData.height);
                                if (minDimension < CROP_SIZE) {
                                    const scale = (CROP_SIZE / minDimension) * 1.1; // 增加10%的缩放比例，确保完全覆盖
                                    cropper.scale(scale);
                                }
                                // 确保裁剪框完全在图片范围内
                                cropper.setData({
                                    width: CROP_SIZE,
                                    height: CROP_SIZE,
                                });
                            }
                        }}
                    />
                </div>
            </Modal>
        </>
    );
};

export default profilephoto;
