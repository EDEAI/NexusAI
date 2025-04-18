/*
 * @LastEditors: biz
 */
import { DownloadOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Button, Empty, List, Typography } from 'antd';
import { memo } from 'react';

interface FileDownloadListProps {
  files?: Record<string, string>;
}

const FileDownloadList = memo(({ files }: FileDownloadListProps) => {
  const intl = useIntl();
  
  if (!files || Object.keys(files).length === 0) {
    return (
      <Empty 
        description={intl.formatMessage({ id: 'workflow.noFiles' })} 
        image={Empty.PRESENTED_IMAGE_SIMPLE} 
      />
    );
  }

  return (
    <List
      size="small"
      bordered
      dataSource={Object.entries(files)}
      renderItem={([filename, url]) => (
        <List.Item 
          extra={
            <Button 
              type="link" 
              href={url} 
              download={filename}
              icon={<DownloadOutlined />}
              target="_blank"
            >
              {intl.formatMessage({ id: 'workflow.download' })}
            </Button>
          }
        >
          <Typography.Text ellipsis title={filename}>
            {filename}
          </Typography.Text>
        </List.Item>
      )}
    />
  );
});

export default FileDownloadList; 