/*
 * @LastEditors: biz
 */
import { getUploadUrl } from '@/api/createkb';
import { useIntl } from '@umijs/max';
import { message, Upload } from 'antd';
import { useRef, useImperativeHandle, forwardRef } from 'react';
import './upload.css';

const { Dragger } = Upload;
const UploadView = forwardRef(({ fun, createkbInfo, fileList = [] }: any, ref) => {
    const intl = useIntl();
    const uploadRef = useRef<any>(null);
    
    // Debug: log when fileList prop changes
    console.log('Upload component received fileList:', fileList.length, 'files');
    console.log('Upload fileList names:', fileList.map(f => f.name));
    
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
            
            console.log('Upload component reset completed');
        }
    };
    
    useImperativeHandle(ref, () => ({
        reset: resetUpload
    }));
    
    let uploads = {
        action: getUploadUrl,
        headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        timeout: 300000,
        // Controlled mode: fileList is managed by parent component
        fileList: fileList,
        onChange(info) {
            const { status } = info.file;
            
            if (status === 'uploading') {
                console.log('Upload progress:', info.file.percent);
            }
            
            if (status === 'done') {
                message.success(`${info.file.name} ${intl.formatMessage({ id: 'createkb.upload.success' })}`);
            } else if (status === 'error') {
                message.error(`${info.file.name} ${intl.formatMessage({ id: 'createkb.upload.error' })}`);
            }
            
            // Always call parent function to update state
            fun(info);
        },
        beforeUpload(file) {
            const isLt15M = file.size / 1024 / 1024 < 15;
            if (!isLt15M) {
                message.error(
                    intl.formatMessage({
                        id: 'createkb.error.fileSize',
                        defaultMessage: 'File size cannot exceed 15MB',
                    }),
                );
                return false;
            }
            
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            const startMessage = `${intl.formatMessage({ id: 'createkb.upload.starting' })} ${file.name}，${intl.formatMessage({ id: 'createkb.upload.fileSize' })}: ${fileSize}MB`;
            message.info(startMessage);
            return isLt15M;
        },
        customRequest(options) {
            const { action, file, onError, onProgress, onSuccess, headers } = options;
            const formData = new FormData();
            formData.append('file', file);
            
            const xhr = new XMLHttpRequest();
            xhr.timeout = 300000;
            
            xhr.open('post', typeof action === 'function' ? action(file) : action, true);
            
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
                        const errorMessage = intl.formatMessage({ id: 'createkb.error.serverResponse' });
                        onError(new Error(errorMessage), file);
                    }
                } else {
                    const errorMessage = `${intl.formatMessage({ id: 'createkb.error.httpStatus' })} ${xhr.status}`;
                    onError(new Error(errorMessage), file);
                }
            });
            
            xhr.addEventListener('error', () => {
                const errorMessage = intl.formatMessage({ id: 'createkb.error.network' });
                onError(new Error(errorMessage), file);
            });
            
            xhr.addEventListener('timeout', () => {
                const errorMessage = intl.formatMessage({ id: 'createkb.error.timeout' });
                onError(new Error(errorMessage), file);
            });
            
            xhr.addEventListener('abort', () => {
                const errorMessage = intl.formatMessage({ id: 'createkb.error.cancelled' });
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
    
    const props = {
        ...uploads,
        name: 'file',
        multiple: true,
        className: 'h-[200px]',
        showUploadList: false,
    };
    
    return (
        <>
            <Dragger
                {...props}
                ref={uploadRef}
                listType="picture"
                className="flex flex-col items-center justify-center custom-dragger mt-[15px]"
                accept=".txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv"
                disabled={createkbInfo.type}
            >
                <div className="update p-[4px]">
                    <div className="flex items-center w-full justify-center">
                        <img src="/icons/word.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/txt.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/pdf.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/xlsx.svg" className="w-[42px] h-[42px] mx-3" />
                        <img src="/icons/md.svg" className="w-[42px] h-[42px] mx-3" />
                    </div>
                    <div className="mt-[10px] text-[#213044] text-sm">
                        {intl.formatMessage({
                            id: 'createkb.instruction.dragOrClick',
                            defaultMessage: 'Drag files here or click to upload',
                        })}
                    </div>
                    <div className="mt-[10px] text-[#999999] text-sm">
                        {intl.formatMessage({
                            id: 'createkb.instruction.uploadLimit',
                            defaultMessage: 'Support batch upload, single file no more than 15MB',
                        })}
                    </div>
                </div>
            </Dragger>
        </>
    );
});

export default UploadView;
