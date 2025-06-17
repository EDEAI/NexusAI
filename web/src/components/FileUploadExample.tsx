import { FC, useState } from 'react';
import { Button, Tag, Image, Tooltip, message } from 'antd';
import { UploadOutlined, DownloadOutlined, FileOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import useFileUpload from '@/hooks/useFileUpload';

const downloadFile = (url: string, filename: string) => {
    try {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {
        console.error('下载文件失败', e);
        message.error('下载文件失败');
    }
};

interface FileUploadExampleProps {
    disabled?: boolean;
    onFilesChange?: (files: any[]) => void;
    customFileTypes?: string;
    maxSize?: number;
    multiple?: boolean;
}

const FileUploadExample: FC<FileUploadExampleProps> = ({
    disabled = false,
    onFilesChange,
    customFileTypes,
    maxSize = 15,
    multiple = true
}) => {
    const intl = useIntl();
    
    // 使用自定义的文件上传 hook
    const {
        uploadedFiles,
        handleUpload,
        removeFile,
        clearFiles,
        isUploading
    } = useFileUpload({
        maxSizeMB: maxSize,
        acceptedFileTypes: customFileTypes || '.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.jpeg',
        multiple
    });
    
    // 当文件列表变化时通知父组件
    useState(() => {
        if (onFilesChange) {
            onFilesChange(uploadedFiles);
        }
    });
    
    return (
        <div className="flex flex-col">
            <div className="flex items-center mb-2">
                <Button 
                    icon={<UploadOutlined />} 
                    onClick={handleUpload}
                    disabled={disabled || isUploading}
                    loading={isUploading}
                >
                    {intl.formatMessage({ id: 'common.upload.file' }) || '上传文件'}
                </Button>
                
                {uploadedFiles.length > 0 && (
                    <Button 
                        className="ml-2" 
                        size="small" 
                        onClick={clearFiles}
                        disabled={disabled}
                    >
                        {intl.formatMessage({ id: 'common.clear.all' }) || '清空所有'}
                    </Button>
                )}
            </div>
            
            {uploadedFiles.length > 0 && (
                <div className="p-2 border rounded-md bg-gray-50">
                    <Image.PreviewGroup>
                        <div className="flex flex-wrap gap-2">
                            {uploadedFiles.map(file => (
                                <Tag 
                                    key={file.uid}
                                    closable={!disabled}
                                    onClose={() => removeFile(file.uid)}
                                    className={`flex items-center ${file.isImage ? 'bg-blue-50 text-blue-600 hover:bg-blue-100' : 'bg-blue-50 text-blue-600'}`}
                                >
                                    <Tooltip title={file.name}>
                                        <div className="flex items-center">
                                            {file.isImage ? (
                                                <div className="mr-1 flex items-center">
                                                    <Image 
                                                        src={file.path_show || file.url} 
                                                        alt={file.name} 
                                                        className="w-6 h-6 max-w-6 max-h-6 object-cover mr-1 rounded-sm cursor-pointer" 
                                                        preview={{
                                                            src: file.path_show || file.url,
                                                            mask: false
                                                        }}
                                                    />
                                                    <span className="truncate mr-1 max-w-[120px]">{file.name}</span>
                                                    <DownloadOutlined 
                                                        className="text-gray-500 hover:text-blue-600 cursor-pointer ml-1"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            downloadFile(file.path_show || file.url, file.name);
                                                        }}
                                                    />
                                                </div>
                                            ) : (
                                                <div className="flex items-center">
                                                    <FileOutlined className="mr-1" />
                                                    <span className="truncate mr-1 max-w-[120px]">{file.name}</span>
                                                    <DownloadOutlined 
                                                        className="text-gray-500 hover:text-blue-600 cursor-pointer ml-1"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            downloadFile(file.path_show || file.url, file.name);
                                                        }}
                                                    />
                                                </div>
                                            )}
                                        </div>
                                    </Tooltip>
                                </Tag>
                            ))}
                        </div>
                    </Image.PreviewGroup>
                </div>
            )}
        </div>
    );
};

export default FileUploadExample; 