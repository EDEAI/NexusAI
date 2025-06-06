import { message } from 'antd';
import { useIntl } from '@umijs/max';
import { useState } from 'react';
import { getUploadUrl } from '@/api/createkb';

export interface UploadedFile {
    name: string;
    url: string;
    uid: string;
    isImage?: boolean;
    file_id?: string;
    path_show?: string;
}

export const isImageFile = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension || '');
};

interface UseFileUploadOptions {
    maxSizeMB?: number;
    acceptedFileTypes?: string;
    multiple?: boolean;
}

export const useFileUpload = (options: UseFileUploadOptions = {}) => {
    const intl = useIntl();
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [isUploading, setIsUploading] = useState(false);

    const {
        maxSizeMB = 15,
        acceptedFileTypes = '.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.jpeg',
        multiple = true
    } = options;

    const handleUpload = () => {
        // 触发文件选择对话框
        const uploadInput = document.createElement('input');
        uploadInput.type = 'file';
        uploadInput.accept = acceptedFileTypes;
        uploadInput.multiple = multiple;
        
        uploadInput.onchange = async (e) => {
            const target = e.target as HTMLInputElement;
            if (target.files && target.files.length > 0) {
                setIsUploading(true);
                const files = Array.from(target.files);
                
                // 检查文件大小
                const oversizedFiles = files.filter(file => file.size / 1024 / 1024 > maxSizeMB);
                if (oversizedFiles.length > 0) {
                    message.error(`${oversizedFiles.map(f => f.name).join(', ')} ${intl.formatMessage({ id: 'workflow.uploadFileErrorText' })}`);
                    setIsUploading(false);
                    return;
                }
                
                // 上传所有文件
                const newFiles: UploadedFile[] = [];
                
                for (const file of files) {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    try {
                        const url = await getUploadUrl();
                        const response = await fetch(url, {
                            method: 'POST',
                            headers: {
                                Authorization: `Bearer ${localStorage.getItem('token')}`,
                            },
                            body: formData,
                        });
                        
                        const result = await response.json();
                        
                        if (result.code === 0) {
                            message.success(`${file.name} ${intl.formatMessage({ id: 'workflow.uploadSuccess' })}`);
                            
                            // 将文件添加到上传文件列表
                            if (result.data?.file_id) {
                                const isImage = isImageFile(file.name);
                                const fileData: UploadedFile = {
                                    name: file.name,
                                    url: result.data.file_url || '',
                                    uid: `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                                    isImage,
                                    file_id: result.data.file_id,
                                    path_show: result.data.file_url || result.data.path_show || ''
                                };
                                
                                newFiles.push(fileData);
                            }
                        } else {
                            message.error(`${file.name} ${intl.formatMessage({ id: 'workflow.uploadFailed' })}`);
                        }
                    } catch (error) {
                        console.error('Upload error:', error);
                        message.error(`${file.name} ${intl.formatMessage({ id: 'workflow.uploadFailed' })}`);
                    }
                }
                
                setUploadedFiles(prev => [...prev, ...newFiles]);
                setIsUploading(false);
            }
        };
        
        uploadInput.click();
    };

    const removeFile = (uid: string) => {
        setUploadedFiles(prev => prev.filter(file => file.uid !== uid));
    };

    const clearFiles = () => {
        setUploadedFiles([]);
    };

    return {
        uploadedFiles,
        setUploadedFiles,
        handleUpload,
        removeFile,
        clearFiles,
        isUploading
    };
};

export default useFileUpload; 