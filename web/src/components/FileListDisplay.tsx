import { FC } from 'react';
import { Button, Image } from 'antd';
import { DownloadOutlined, FileOutlined } from '@ant-design/icons';
import { isImageFile } from '@/hooks/useFileUpload';

interface FileItem {
    name: string;
    url: string;
    path_show?: string;
    uid?: string;
    file_id?: string;
}

interface FileListDisplayProps {
    fileList: FileItem[];
    onDownload?: (url: string, filename: string) => void;
    className?: string;
    showInGrid?: boolean;
    maxHeight?: string;
}


const defaultDownloadFile = (url: string, filename: string) => {
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
    }
};

const FileListDisplay: FC<FileListDisplayProps> = ({
    fileList,
    onDownload = defaultDownloadFile,
    className = '',
    showInGrid = false,
    maxHeight,
}) => {
    if (!fileList || fileList.length === 0) {
        return null;
    }

    return (
        <div className={`mb-2 ${className}`} style={{ maxHeight, overflow: maxHeight ? 'auto' : 'visible' }}>
            <Image.PreviewGroup>
                <div className={`${showInGrid ? 'grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4' : 'flex flex-col'}`}>
                    {fileList.map((file, index) => {
                        const fileUrl = file.path_show || file.url;
                        const isImg = isImageFile(file.name);
                        
                        return (
                            <div key={`${file.uid || file.file_id || index}`} className={`${showInGrid ? '' : 'mb-2'}`}>
                                {isImg ? (
                                    <div className="rounded-md overflow-hidden relative group">
                                        <Image 
                                            src={fileUrl} 
                                            alt={file.name} 
                                            className="max-w-full max-h-40 h-auto rounded-md"
                                        />
                                        <div className="absolute top-0 right-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <Button 
                                                type="primary" 
                                                size="small" 
                                                icon={<DownloadOutlined />} 
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    onDownload(fileUrl, file.name);
                                                }}
                                            />
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex items-center bg-white rounded-md p-2 text-blue-600 justify-between">
                                        <div className="flex items-center overflow-hidden">
                                            <FileOutlined className="mr-2 flex-shrink-0" />
                                            <span className="text-sm truncate">{file.name}</span>
                                        </div>
                                        <Button 
                                            type="text" 
                                            size="small" 
                                            icon={<DownloadOutlined />}
                                            onClick={() => onDownload(fileUrl, file.name)}
                                            className="ml-2 flex-shrink-0"
                                        />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </Image.PreviewGroup>
        </div>
    );
};

export default FileListDisplay; 