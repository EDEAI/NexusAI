/*
 * @LastEditors: biz
 */
import React, { useEffect } from 'react';
import useFileUpload from '@/hooks/useFileUpload';
import { FileToUpload, FileUploadData } from '../types/fileUpload';
import { Button, Progress } from 'antd';

interface FileUploadItemProps {
  fileConfig: FileToUpload;
  value?: FileUploadData | null;
  onChange: (fileData: FileUploadData | null) => void;
}

const FileUploadItem: React.FC<FileUploadItemProps> = ({ fileConfig, value, onChange }) => {
  const {
    uploadedFiles,
    handleUpload,
    removeFile,
    clearFiles,
    isUploading
  } = useFileUpload({
    maxSizeMB: fileConfig.maxSize || 10,
    acceptedFileTypes: fileConfig.accepted_types?.join(',') || undefined,
    multiple: false
  });

 
  useEffect(() => {
    if (uploadedFiles.length > 0) {
      const file = uploadedFiles[uploadedFiles.length - 1];
      const fileData: FileUploadData = {
        file_name: file.name,
        file_path: file.path_show,
        size: 0, 
        type: '',
        id: file.file_id,
        status: 'done',
      };
      onChange(fileData);
    } else {
      onChange(null);
    }
    // eslint-disable-next-line
  }, [uploadedFiles]);

  return (
    <div className="mb-4">
      <div className="text-xs font-medium text-gray-700 mb-1">
        {fileConfig.name}
        {fileConfig.required !== false && <span className="text-red-500 ml-1">*</span>}
        {fileConfig.description && <span className="text-gray-500 ml-2">{fileConfig.description}</span>}
        {fileConfig.accepted_types && fileConfig.accepted_types.length > 0 && (
          <span className="text-gray-400 ml-2">({fileConfig.accepted_types.join(', ')})</span>
        )}
      </div>
      <div className="flex items-center gap-2">
        {uploadedFiles.length === 0 ? (
          <Button
            type="dashed"
            onClick={handleUpload}
            loading={isUploading}
            disabled={isUploading}
            className="w-48"
          >
            {isUploading ? 'Uploading...' : 'Upload File'}
          </Button>
        ) : (
          <>
            <span className="truncate flex-1 text-xs">{uploadedFiles[uploadedFiles.length - 1].name}</span>
            <Button
              type="link"
              danger
              size="small"
              onClick={() => removeFile(uploadedFiles[uploadedFiles.length - 1].uid)}
              disabled={isUploading}
            >
              Remove
            </Button>
          </>
        )}
      </div>
  
      {/* {isUploading && <Progress percent={50} size="small" />} */}
    </div>
  );
};

export default FileUploadItem; 