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
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-800 mb-3">
          <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {title}
        </div>
      )}
      <div className="space-y-3">
        {files.map((file, index) => (
          <div
            key={index}
            className="group relative bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-blue-300 transition-all duration-200"
          >
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-start gap-3 flex-1 min-w-0">
                <div className="flex-shrink-0 w-14 h-14  rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex flex-col flex-1 min-w-0">
                  <span className="text-sm font-medium text-gray-900 truncate mb-1">
                    {file.file_name}
                  </span>
                  {file.variable_name && (
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                        {intl.formatMessage({ id: 'agent.file.variable' })}: {file.variable_name}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <a
                href={file.file_path}
                download={file.file_name}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 hover:text-blue-700 rounded-lg transition-colors duration-200 group-hover:shadow-sm"
              >
                <DownloadOutlined className="w-4 h-4" />
                <span className="shrink-0">
                  {intl.formatMessage({ id: 'agent.file.download' })}
                </span>
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FileDownloadList; 