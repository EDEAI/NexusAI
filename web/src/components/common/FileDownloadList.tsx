/*
 * @LastEditors: biz
 */
import { DownloadOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import React from 'react';

interface FileItem {
  file_name: string;
  file_path: string;
  variable_name?: string;
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
            className="flex items-center justify-between p-2 gap-2 border-l-4 border-gray-300 bg-gray-50"
          >
            <div className="flex flex-col flex-1 min-w-0">
              <span className="text-sm text-gray-600 truncate">
                {file.file_name}
              </span>
              {file.variable_name && (
                <span className="text-xs text-gray-500">
                  {intl.formatMessage({ id: 'agent.file.variable' })}: {file.variable_name}
                </span>
              )}
            </div>
            <a
              href={file.file_path}
              download={file.file_name}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-blue-600 hover:text-blue-800"
            >
              <DownloadOutlined className="w-4 h-4" />
              <span className="text-sm shrink-0">
                {intl.formatMessage({ id: 'agent.file.download' })}
              </span>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FileDownloadList; 