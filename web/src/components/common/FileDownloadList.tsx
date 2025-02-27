/*
 * @LastEditors: biz
 */
import { DownloadOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import React from 'react';

interface FileItem {
  file_name: string;
  file_path: string;
}

interface FileDownloadListProps {
  files: FileItem[];
  title?: string;
  className?: string;
}

const FileDownloadList: React.FC<FileDownloadListProps> = ({ 
  files, 
  title, 
  className = '' 
}) => {
  const intl = useIntl();
  
  if (!files || files.length === 0) {
    return null;
  }

  return (
    <div className={`mt-4 ${className}`}>
      {title && (
        <div className="text-sm font-medium text-gray-700 mb-2">
          {title}
        </div>
      )}
      <div className="space-y-2">
        {files.map((file, index) => (
          <div
            key={index}
            className="flex items-center justify-between bg-white rounded-md p-2 gap-2"
          >
            <span className="text-sm text-gray-600 truncate flex-1">
              {file.file_name}
            </span>
            <a
              href={file.file_path}
              download={file.file_name}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-blue-600 hover:text-blue-800"
            >
              <DownloadOutlined className="w-4 h-4" />
              <span className="text-sm shrink-0">
                {intl.formatMessage({ id: 'skill.download' })}
              </span>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FileDownloadList; 