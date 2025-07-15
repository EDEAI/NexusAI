import { useIntl } from '@umijs/max';
import { message, Upload, UploadProps } from 'antd';
import { useRef, useImperativeHandle, forwardRef } from 'react';
import './index.css';

const { Dragger } = Upload;

export interface FileUploadProps {
    /** File upload success/failure callback function */
    onChange?: (info: any) => void;
    /** Current file list */
    fileList?: any[];
    /** Upload URL */
    action?: string;
    /** Request headers */
    headers?: Record<string, string>;
    /** Whether to disable */
    disabled?: boolean;
    /** Whether to support multiple selection */
    multiple?: boolean;
    /** Accepted file types */
    accept?: string;
    /** Maximum file size (MB) */
    maxSize?: number;
    /** Whether to show upload list */
    showUploadList?: boolean;
    /** Custom CSS class name */
    className?: string;
    /** Component height */
    height?: string | number;
    /** Timeout duration (milliseconds) */
    timeout?: number;
    /** File type icon configuration */
    fileTypeIcons?: {
        src: string;
        alt?: string;
    }[];
    /** Custom upload area content */
    children?: React.ReactNode;
    /** Custom drag text */
    dragText?: string;
    /** Custom upload limit text */
    limitText?: string;
}

export interface FileUploadRef {
    reset: () => void;
}

const FileUpload = forwardRef<FileUploadRef, FileUploadProps>(({
    onChange,
    fileList = [],
    action,
    headers,
    disabled = false,
    multiple = true,
    accept = ".txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv",
    maxSize = 15,
    showUploadList = false,
    className = '',
    height = '200px',
    timeout = 300000,
    fileTypeIcons = [
        { src: "/icons/word.svg", alt: "Word" },
        { src: "/icons/txt.svg", alt: "TXT" },
        { src: "/icons/pdf.svg", alt: "PDF" },
        { src: "/icons/xlsx.svg", alt: "Excel" },
        { src: "/icons/md.svg", alt: "Markdown" }
    ],
    children,
    dragText,
    limitText,
    ...restProps
}, ref) => {
    const intl = useIntl();
    const uploadRef = useRef<any>(null);
    
    console.log('FileUpload component received fileList:', fileList.length, 'files');
    console.log('FileUpload fileList names:', fileList.map(f => f.name));
    
    const resetUpload = () => {
        if (uploadRef.current) {
            // Clear the internal file list
            uploadRef.current.fileList = [];
            
            // Clear any pending uploads
            if (uploadRef.current.upload) {
                uploadRef.current.upload.fileList = [];
            }
            
            // Force component to re-render
            if (uploadRef.current.forceUpdate) {
                uploadRef.current.forceUpdate();
            }
            
            console.log('FileUpload component reset completed');
        }
    };
    
    useImperativeHandle(ref, () => ({
        reset: resetUpload
    }));

    const getDefaultHeaders = () => {
        return headers || {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        };
    };
    
    const uploadProps: UploadProps = {
        action: action || '',
        headers: getDefaultHeaders(),
        fileList,
        onChange(info) {
            const { status } = info.file;
            
            if (status === 'uploading') {
                console.log('Upload progress:', info.file.percent);
            }
            
            if (status === 'done') {
                message.success(`${info.file.name} ${intl.formatMessage({ 
                    id: 'common.upload.success',
                    defaultMessage: 'Upload successful'
                })}`);
            } else if (status === 'error') {
                message.error(`${info.file.name} ${intl.formatMessage({ 
                    id: 'common.upload.error',
                    defaultMessage: 'Upload failed'
                })}`);
            }
            
            // Call parent onChange function
            onChange?.(info);
        },
        beforeUpload(file) {
            const isLtMaxSize = file.size / 1024 / 1024 < maxSize;
            if (!isLtMaxSize) {
                message.error(
                    intl.formatMessage({
                        id: 'common.upload.error.fileSize',
                        defaultMessage: `File size cannot exceed ${maxSize}MB`,
                    }, { maxSize }),
                );
                return false;
            }
            
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            const startMessage = `${intl.formatMessage({ 
                id: 'common.upload.starting',
                defaultMessage: 'Starting upload'
            })} ${file.name}, ${intl.formatMessage({ 
                id: 'common.upload.fileSize',
                defaultMessage: 'File size'
            })}: ${fileSize}MB`;
            message.info(startMessage);
            return isLtMaxSize;
        },
        customRequest(options) {
            const { action, file, onError, onProgress, onSuccess, headers } = options;
            const formData = new FormData();
            formData.append('file', file);
            
            const xhr = new XMLHttpRequest();
            xhr.timeout = timeout;
            
            xhr.open('post', action, true);
            
            if (headers) {
                Object.keys(headers).forEach(key => {
                    xhr.setRequestHeader(key, headers[key]);
                });
            }
            
            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    onProgress({ percent }, file);
                }
            });
            
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.response);
                        onSuccess(response, file);
                    } catch (e) {
                        const errorMessage = intl.formatMessage({ 
                            id: 'common.upload.error.serverResponse',
                            defaultMessage: 'Server response error'
                        });
                        onError(new Error(errorMessage), file);
                    }
                } else {
                    const errorMessage = `${intl.formatMessage({ 
                        id: 'common.upload.error.httpStatus',
                        defaultMessage: 'HTTP status error'
                    })} ${xhr.status}`;
                    onError(new Error(errorMessage), file);
                }
            });
            
            xhr.addEventListener('error', () => {
                const errorMessage = intl.formatMessage({ 
                    id: 'common.upload.error.network',
                    defaultMessage: 'Network error'
                });
                onError(new Error(errorMessage), file);
            });
            
            xhr.addEventListener('timeout', () => {
                const errorMessage = intl.formatMessage({ 
                    id: 'common.upload.error.timeout',
                    defaultMessage: 'Upload timeout'
                });
                onError(new Error(errorMessage), file);
            });
            
            xhr.addEventListener('abort', () => {
                const errorMessage = intl.formatMessage({ 
                    id: 'common.upload.error.cancelled',
                    defaultMessage: 'Upload cancelled'
                });
                onError(new Error(errorMessage), file);
            });
            
            xhr.send(formData);
            
            return {
                abort() {
                    xhr.abort();
                }
            };
        }
    };

    const defaultDragText = dragText || intl.formatMessage({
        id: 'common.upload.instruction.dragOrClick',
        defaultMessage: 'Drag files here or click to upload',
    });

    const defaultLimitText = limitText || intl.formatMessage({
        id: 'common.upload.instruction.uploadLimit',
        defaultMessage: `Supports batch upload, single file no more than ${maxSize}MB`,
    }, { maxSize });

    const renderDefaultContent = () => (
        <div className="upload-content p-[4px]">
            <div className="flex items-center w-full justify-center">
                {fileTypeIcons.map((icon, index) => (
                    <img 
                        key={index}
                        src={icon.src} 
                        alt={icon.alt}
                        className="w-[42px] h-[42px] mx-3" 
                    />
                ))}
            </div>
            <div className="mt-[10px] text-[#213044] text-sm">
                {defaultDragText}
            </div>
            <div className="mt-[10px] text-[#999999] text-sm">
                {defaultLimitText}
            </div>
        </div>
    );
    
    const props = {
        ...uploadProps,
        ...restProps,
        name: 'file',
        multiple,
        className: `${className} flex flex-col items-center justify-center`,
        showUploadList,
        accept,
        disabled,
        style: { height },
    };
    
    return (
        <Dragger
            {...props}
            ref={uploadRef}
            listType="picture"
        >
            {children || renderDefaultContent()}
        </Dragger>
    );
});

FileUpload.displayName = 'FileUpload';

export default FileUpload; 