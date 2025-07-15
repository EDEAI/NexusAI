import React, { forwardRef, useImperativeHandle, useRef, useState, useCallback } from 'react';
import { useIntl } from '@umijs/max';
import { message, Upload, Progress, Button, Space, Typography, Card } from 'antd';
import { 
    DeleteOutlined, 
    PauseCircleOutlined, 
    PlayCircleOutlined, 
    ReloadOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    CloudUploadOutlined
} from '@ant-design/icons';
import './index.css';

const { Dragger } = Upload;
const { Text } = Typography;

export interface FileUploadWithProgressProps {
    /** Upload URL */
    action?: string;
    /** Request headers */
    headers?: Record<string, string>;
    /** Whether to disable */
    disabled?: boolean;
    /** Upload mode: single or multiple */
    mode?: 'single' | 'multiple';
    /** Accepted file types */
    accept?: string;
    /** Maximum file size (MB) */
    maxSize?: number;
    /** Maximum number of files (only for multiple mode) */
    maxCount?: number;
    /** Custom CSS class name */
    className?: string;
    /** Component height */
    height?: string | number;
    /** Timeout duration (milliseconds) */
    timeout?: number;
    /** Whether to show progress details */
    showProgressDetails?: boolean;
    /** Whether to auto remove files after successful upload */
    autoRemoveOnSuccess?: boolean;
    /** File upload success callback */
    onSuccess?: (file: any, response: any) => void;
    /** File upload error callback */
    onError?: (file: any, error: any) => void;
    /** File upload progress callback */
    onProgress?: (file: any, progress: number) => void;
    /** File list change callback */
    onChange?: (fileList: any[]) => void;
    /** Custom drag area content */
    children?: React.ReactNode;
    /** Custom drag text */
    dragText?: string;
    /** Custom hint text */
    hintText?: string;
}

export interface FileUploadWithProgressRef {
    reset: () => void;
    upload: () => void;
    pause: () => void;
    resume: () => void;
    getFileList: () => any[];
}

interface FileItem {
    uid: string;
    name: string;
    size: number;
    status: 'ready' | 'uploading' | 'success' | 'error' | 'paused';
    percent: number;
    file: File;
    response?: any;
    error?: any;
    xhr?: XMLHttpRequest;
}

const FileUploadWithProgress = forwardRef<FileUploadWithProgressRef, FileUploadWithProgressProps>(({
    action = '',
    headers,
    disabled = false,
    mode = 'multiple',
    accept = ".txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.gif,.zip,.rar",
    maxSize = 15,
    maxCount = 10,
    className = '',
    height = '200px',
    timeout = 300000,
    showProgressDetails = true,
    autoRemoveOnSuccess = false,
    onSuccess,
    onError,
    onProgress,
    onChange,
    children,
    dragText,
    hintText,
}, ref) => {
    const intl = useIntl();
    const [fileList, setFileList] = useState<FileItem[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const getDefaultHeaders = useCallback(() => {
        return headers || {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        };
    }, [headers]);

    const generateUID = () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    };

    const validateFile = (file: File): boolean => {
        // Check file size
        if (file.size / 1024 / 1024 > maxSize) {
            message.error(
                intl.formatMessage({
                    id: 'common.upload.error.fileSize',
                    defaultMessage: `File size cannot exceed ${maxSize}MB`,
                }, { maxSize, fileName: file.name })
            );
            return false;
        }

        // Check file type if accept is specified
        if (accept) {
            const acceptTypes = accept.split(',').map(type => type.trim());
            const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
            if (!acceptTypes.includes(fileExt)) {
                message.error(
                    intl.formatMessage({
                        id: 'common.upload.error.fileType',
                        defaultMessage: `File type ${fileExt} is not supported`,
                    }, { fileType: fileExt, fileName: file.name })
                );
                return false;
            }
        }

        return true;
    };

    const handleFileSelect = (files: FileList) => {
        const validFiles: File[] = [];
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (validateFile(file)) {
                validFiles.push(file);
            }
        }

        if (validFiles.length === 0) return;

        // Check max count for multiple mode
        if (mode === 'multiple' && fileList.length + validFiles.length > maxCount) {
            message.warning(
                intl.formatMessage({
                    id: 'common.upload.error.maxCount',
                    defaultMessage: `Cannot exceed ${maxCount} files`,
                }, { maxCount })
            );
            return;
        }

        // For single mode, replace existing file
        if (mode === 'single') {
            const newFile: FileItem = {
                uid: generateUID(),
                name: validFiles[0].name,
                size: validFiles[0].size,
                status: 'ready',
                percent: 0,
                file: validFiles[0],
            };
            setFileList([newFile]);
            onChange?.([newFile]);
            return;
        }

        // For multiple mode, add files
        const newFiles: FileItem[] = validFiles.map(file => ({
            uid: generateUID(),
            name: file.name,
            size: file.size,
            status: 'ready',
            percent: 0,
            file,
        }));

        const updatedFileList = [...fileList, ...newFiles];
        setFileList(updatedFileList);
        onChange?.(updatedFileList);
    };

    const uploadFile = (fileItem: FileItem): Promise<void> => {
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('file', fileItem.file);

            const xhr = new XMLHttpRequest();
            xhr.timeout = timeout;

            // Store xhr reference for potential cancellation
            fileItem.xhr = xhr;

            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    updateFileStatus(fileItem.uid, 'uploading', percent);
                    onProgress?.(fileItem, percent);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.response);
                        updateFileStatus(fileItem.uid, 'success', 100, response);
                        onSuccess?.(fileItem, response);
                        
                        message.success(
                            intl.formatMessage({
                                id: 'common.upload.success',
                                defaultMessage: 'Upload successful',
                            }) + `: ${fileItem.name}`
                        );

                        if (autoRemoveOnSuccess) {
                            setTimeout(() => removeFile(fileItem.uid), 2000);
                        }
                        resolve();
                    } catch (e) {
                        const error = new Error('Server response error');
                        updateFileStatus(fileItem.uid, 'error', fileItem.percent, undefined, error);
                        onError?.(fileItem, error);
                        reject(error);
                    }
                } else {
                    const error = new Error(`HTTP ${xhr.status}: Upload failed`);
                    updateFileStatus(fileItem.uid, 'error', fileItem.percent, undefined, error);
                    onError?.(fileItem, error);
                    reject(error);
                }
            });

            xhr.addEventListener('error', () => {
                const error = new Error('Network error');
                updateFileStatus(fileItem.uid, 'error', fileItem.percent, undefined, error);
                onError?.(fileItem, error);
                reject(error);
            });

            xhr.addEventListener('timeout', () => {
                const error = new Error('Upload timeout');
                updateFileStatus(fileItem.uid, 'error', fileItem.percent, undefined, error);
                onError?.(fileItem, error);
                reject(error);
            });

            xhr.open('POST', action);
            
            const requestHeaders = getDefaultHeaders();
            Object.keys(requestHeaders).forEach(key => {
                xhr.setRequestHeader(key, requestHeaders[key]);
            });

            updateFileStatus(fileItem.uid, 'uploading', 0);
            xhr.send(formData);
        });
    };

    const updateFileStatus = (
        uid: string, 
        status: FileItem['status'], 
        percent?: number, 
        response?: any, 
        error?: any
    ) => {
        setFileList(prev => {
            const updated = prev.map(file => {
                if (file.uid === uid) {
                    return {
                        ...file,
                        status,
                        percent: percent !== undefined ? percent : file.percent,
                        response: response !== undefined ? response : file.response,
                        error: error !== undefined ? error : file.error,
                    };
                }
                return file;
            });
            onChange?.(updated);
            return updated;
        });
    };

    const removeFile = (uid: string) => {
        setFileList(prev => {
            const file = prev.find(f => f.uid === uid);
            if (file?.xhr) {
                file.xhr.abort();
            }
            const updated = prev.filter(f => f.uid !== uid);
            onChange?.(updated);
            return updated;
        });
    };

    const pauseUpload = (uid: string) => {
        const file = fileList.find(f => f.uid === uid);
        if (file?.xhr) {
            file.xhr.abort();
            updateFileStatus(uid, 'paused');
        }
    };

    const resumeUpload = (uid: string) => {
        const file = fileList.find(f => f.uid === uid);
        if (file && file.status === 'paused') {
            uploadFile(file);
        }
    };

    const retryUpload = (uid: string) => {
        const file = fileList.find(f => f.uid === uid);
        if (file) {
            uploadFile(file);
        }
    };

    const uploadAll = () => {
        const readyFiles = fileList.filter(f => f.status === 'ready' || f.status === 'error');
        readyFiles.forEach(file => uploadFile(file));
    };

    const pauseAll = () => {
        const uploadingFiles = fileList.filter(f => f.status === 'uploading');
        uploadingFiles.forEach(file => pauseUpload(file.uid));
    };

    const clearAll = () => {
        fileList.forEach(file => {
            if (file.xhr) {
                file.xhr.abort();
            }
        });
        setFileList([]);
        onChange?.([]);
    };

    // Ref methods
    useImperativeHandle(ref, () => ({
        reset: clearAll,
        upload: uploadAll,
        pause: pauseAll,
        resume: () => {
            const pausedFiles = fileList.filter(f => f.status === 'paused');
            pausedFiles.forEach(file => resumeUpload(file.uid));
        },
        getFileList: () => fileList,
    }));

    // Event handlers
    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        
        if (disabled) return;
        
        const files = e.dataTransfer.files;
        handleFileSelect(files);
    };

    const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files) {
            handleFileSelect(files);
        }
        // Reset input value to allow selecting the same file again
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleClick = () => {
        if (!disabled && fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const getStatusIcon = (status: FileItem['status']) => {
        switch (status) {
            case 'success':
                return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
            case 'error':
                return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
            case 'uploading':
                return <CloudUploadOutlined style={{ color: '#1890ff' }} />;
            default:
                return null;
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const defaultDragText = dragText || intl.formatMessage({
        id: 'common.upload.dragText',
        defaultMessage: 'Click or drag files here to upload',
    });

    const defaultHintText = hintText || intl.formatMessage({
        id: 'common.upload.hintText',
        defaultMessage: `Support ${mode === 'single' ? 'single file' : 'multiple files'}, max ${maxSize}MB per file`,
    }, { mode: mode === 'single' ? 'single file' : 'multiple files', maxSize });

    return (
        <div className={`file-upload-with-progress ${className}`}>
            {/* Upload Area */}
            <div
                className={`upload-area ${isDragging ? 'dragging' : ''} ${disabled ? 'disabled' : ''}`}
                style={{ height }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={handleClick}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple={mode === 'multiple'}
                    accept={accept}
                    onChange={handleFileInputChange}
                    style={{ display: 'none' }}
                    disabled={disabled}
                />
                
                {children || (
                    <div className="upload-content">
                        <CloudUploadOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                        <div className="upload-text">{defaultDragText}</div>
                        <div className="upload-hint">{defaultHintText}</div>
                    </div>
                )}
            </div>

            {/* File List */}
            {fileList.length > 0 && (
                <div className="file-list mt-4">
                    <div className="file-list-header">
                        <Space>
                            <Text strong>
                                {intl.formatMessage({
                                    id: 'common.upload.fileList',
                                    defaultMessage: 'File List',
                                })} ({fileList.length})
                            </Text>
                            <Button size="small" onClick={uploadAll} disabled={disabled}>
                                {intl.formatMessage({
                                    id: 'common.upload.uploadAll',
                                    defaultMessage: 'Upload All',
                                })}
                            </Button>
                            <Button size="small" onClick={clearAll} disabled={disabled}>
                                {intl.formatMessage({
                                    id: 'common.upload.clearAll',
                                    defaultMessage: 'Clear All',
                                })}
                            </Button>
                        </Space>
                    </div>

                    <div className="file-items mt-2">
                        {fileList.map(file => (
                            <Card key={file.uid} size="small" className="file-item mb-2">
                                <div className="file-info">
                                    <div className="file-header">
                                        <Space>
                                            {getStatusIcon(file.status)}
                                            <Text strong>{file.name}</Text>
                                            <Text type="secondary">{formatFileSize(file.size)}</Text>
                                        </Space>
                                        
                                        <Space>
                                            {file.status === 'uploading' && (
                                                <Button
                                                    size="small"
                                                    icon={<PauseCircleOutlined />}
                                                    onClick={() => pauseUpload(file.uid)}
                                                />
                                            )}
                                            {file.status === 'paused' && (
                                                <Button
                                                    size="small"
                                                    icon={<PlayCircleOutlined />}
                                                    onClick={() => resumeUpload(file.uid)}
                                                />
                                            )}
                                            {file.status === 'error' && (
                                                <Button
                                                    size="small"
                                                    icon={<ReloadOutlined />}
                                                    onClick={() => retryUpload(file.uid)}
                                                />
                                            )}
                                            <Button
                                                size="small"
                                                danger
                                                icon={<DeleteOutlined />}
                                                onClick={() => removeFile(file.uid)}
                                            />
                                        </Space>
                                    </div>

                                    {(file.status === 'uploading' || file.status === 'success') && (
                                        <div className="progress-section mt-2">
                                            <Progress
                                                percent={file.percent}
                                                size="small"
                                                status={file.status === 'success' ? 'success' : 'active'}
                                                strokeColor="#1890ff"
                                                showInfo={showProgressDetails}
                                            />
                                            {showProgressDetails && file.status === 'uploading' && (
                                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                                    {intl.formatMessage({
                                                        id: 'common.upload.uploading',
                                                        defaultMessage: 'Uploading...',
                                                    })} {file.percent}%
                                                </Text>
                                            )}
                                        </div>
                                    )}

                                    {file.status === 'error' && file.error && (
                                        <div className="error-section mt-2">
                                            <Text type="danger" style={{ fontSize: '12px' }}>
                                                {file.error.message}
                                            </Text>
                                        </div>
                                    )}
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
});

FileUploadWithProgress.displayName = 'FileUploadWithProgress';

export default FileUploadWithProgress; 