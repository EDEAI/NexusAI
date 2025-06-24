/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import { DownloadOutlined, FileOutlined } from '@ant-design/icons';
import { Image, Tag, Tooltip } from 'antd';
import { downloadFile } from '../utils';

interface FileUploadAreaProps {
    uploadedFiles: any[];
    handleRemoveFile: (uid: string) => void;
}

export const FileUploadArea: FC<FileUploadAreaProps> = props => {
    const { uploadedFiles, handleRemoveFile } = props;

    if (!uploadedFiles.length) {
        return null;
    }

    return (
        <Image.PreviewGroup>
            <div className="p-2 border-b border-gray-200">
                <div className="flex flex-wrap gap-2">
                    {uploadedFiles.map(file => (
                        <Tag
                            key={file.uid}
                            closable
                            onClose={() => handleRemoveFile(file.uid)}
                            className={`flex items-center ${
                                file.isImage
                                    ? 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                                    : 'bg-blue-50 text-blue-600'
                            }`}
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
                                                    mask: false,
                                                }}
                                            />
                                            <span className="truncate mr-1">
                                                {file.name}
                                            </span>
                                            <DownloadOutlined
                                                className="text-gray-500 hover:text-blue-600 cursor-pointer ml-1"
                                                onClick={e => {
                                                    e.stopPropagation();
                                                    downloadFile(
                                                        file.path_show || file.url,
                                                        file.name,
                                                    );
                                                }}
                                            />
                                        </div>
                                    ) : (
                                        <div className="flex items-center">
                                            <FileOutlined className="mr-1" />
                                            <span className="truncate mr-1">
                                                {file.name}
                                            </span>
                                            <DownloadOutlined
                                                className="text-gray-500 hover:text-blue-600 cursor-pointer ml-1"
                                                onClick={e => {
                                                    e.stopPropagation();
                                                    downloadFile(
                                                        file.path_show || file.url,
                                                        file.name,
                                                    );
                                                }}
                                            />
                                        </div>
                                    )}
                                </div>
                            </Tooltip>
                        </Tag>
                    ))}
                </div>
            </div>
        </Image.PreviewGroup>
    );
}; 