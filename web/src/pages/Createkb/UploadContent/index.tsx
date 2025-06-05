import { DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { Button, Input, Modal, Progress, Switch, Table, TableColumnsType, message } from 'antd';
import { useEffect, useRef, useState, memo, useCallback } from 'react';
import UploadView from './Upload/upload';

import {
    addDocument,
    deleteDocument,
    disableDocument,
    documentList,
    enableDocument,
} from '@/api/createkb';
import { ProForm, ProFormDigit, ProFormRadio, ProFormSwitch } from '@ant-design/pro-components';
import { getLocale, useIntl } from '@umijs/max';
import Fileset from '../Fileset';

// Define IntlShape type to avoid external dependencies
interface IntlShape {
    formatMessage: (descriptor: { id: string; defaultMessage?: string }) => string;
}

let listPageNum = 1;
let timer;
let inputText = '';
let sortscontent = null;

const initValues = {
    split: true,
    split_mode: 'text',
    chunk_size: 4000,
    chunk_overlap: 200,
};

// Define UploadPrevForm component props type
interface UploadPrevFormProps {
    onFinish: (values: any) => Promise<void>;
    isUploading: boolean;
    formValuesRef: React.MutableRefObject<{
        split: boolean;
        split_mode: string;
        chunk_size: number;
        chunk_overlap: number;
    }>;
    intl: IntlShape;
}

// Extract UploadPrev component outside to prevent reloading during parent component re-renders
const UploadPrevForm = memo(({ onFinish, isUploading, formValuesRef, intl }: UploadPrevFormProps) => {
    // Use useCallback to wrap onFinish function to avoid unnecessary re-renders
    const handleFinish = useCallback((values) => {
        // Update values stored in ref
        formValuesRef.current = values;
        return onFinish(values);
    }, [onFinish, formValuesRef]);

    // Use useCallback to wrap onValuesChange function to avoid unnecessary re-renders
    const handleValuesChange = useCallback((_, allValues) => {
        // Update values stored in ref
        formValuesRef.current = allValues;
    }, [formValuesRef]);

    return (
        <ProForm
            submitter={{
                resetButtonProps: false,
                searchConfig: {
                    submitText: intl.formatMessage({
                        id: 'createkb.uploadToKnowledgeBase',
                        defaultMessage: '',
                    }),
                },
            }}
            onFinish={handleFinish}
            layout="horizontal"
            initialValues={formValuesRef.current}
            disabled={isUploading}
            onValuesChange={handleValuesChange}
            preserve={false} // Prevent form from being cached
        >
            <ProFormSwitch
                name="split"
                label={intl.formatMessage({ id: 'createkb.splitContent', defaultMessage: '' })}
            ></ProFormSwitch>
            <ProForm.Item noStyle dependencies={['split']}>
                {({ getFieldValue }) => {
                    return getFieldValue('split') ? (
                        <>
                            <ProFormRadio.Group
                                label={intl.formatMessage({
                                    id: 'createkb.splitType',
                                    defaultMessage: '',
                                })}
                                name="split_mode"
                                radioType="button"
                                fieldProps={{
                                    options: [
                                        {
                                            label: 'text',
                                            value: 'text',
                                        },
                                        {
                                            label: 'markdown',
                                            value: 'markdown',
                                        },
                                    ],
                                }}
                            />
                            <ProForm.Item noStyle dependencies={['split_mode']}>
                                {({ getFieldValue }) => {
                                    return getFieldValue('split_mode') === 'text' ? (
                                        <>
                                            <ProFormDigit
                                                label={intl.formatMessage({
                                                    id: 'createkb.chunkSize',
                                                    defaultMessage: '',
                                                })}
                                                name="chunk_size"
                                                min={200}
                                                max={8000}
                                            />
                                            <ProFormDigit
                                                label={intl.formatMessage({
                                                    id: 'createkb.chunkOverlap',
                                                    defaultMessage: '',
                                                })}
                                                name="chunk_overlap"
                                                min={0}
                                                max={8000}
                                            />
                                        </>
                                    ) : null;
                                }}
                            </ProForm.Item>
                        </>
                    ) : null;
                }}
            </ProForm.Item>
        </ProForm>
    );
});

const UploadList = ({ fun, createkbInfo }: any) => {
    const { confirm } = Modal;
    const intl = useIntl();
    const wordList = (
        columns,
        loadingType,
        dataList,
        pagination,
        onclickList,
        handleTableChange,
    ) => {
        return (
            <div className="mt-[10px] border border-[#EEEEEE] rounded-lg">
                <Table
                    columns={columns}
                    loading={loadingType}
                    dataSource={dataList}
                    size="middle"
                    pagination={pagination}
                    locale={{
                        emptyText: (
                            <div className="text-[#666666] text-[14px] leading-[20px] font-normal">
                                <span>
                                    {intl.formatMessage({
                                        id: 'createkb.no.data.available',
                                        defaultMessage: '',
                                    })}
                                </span>
                            </div>
                        ),
                    }}
                    onRow={(record, i) => {
                        return {
                            onClick: () => onclickList(record, i),
                            style: { cursor: 'pointer' },
                        };
                    }}
                    onChange={handleTableChange}
                    rowKey="id"
                />
            </div>
        );
    };

    const [open, setOpen] = useState([]);

    const [dataList, setCount] = useState([]);

    const [datacontent, setData] = useState(null);

    const [loadingType, loadingfun] = useState(true);

    const [handoffPage, handoffPagefun] = useState(true);

    const [itemData, itemDatafun] = useState(null);
    const [appType, appTypefun] = useState(1);

    const [uploadFileList, setUploadFileList] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    
    // Use useRef to store form values to prevent component re-rendering
    const formValuesRef = useRef(initValues);

    const uploadViewRef = useRef(null);

    const next = () => {
        fun({
            type: 'next',
            data: '3',
        });
    };

    const filesetThen = e => {
        handoffPagefun(true);
    };

    const togglePopoverVisibility = index => {
        const newOpen = [...open];
        newOpen[index] = !newOpen[index];
        setOpen(newOpen);
    };

    const onChange = async (checked: boolean, text: String, record: any, index: Number) => {
        let res = null;
        if (!checked) {
            res = await disableDocument(record.id);
        } else {
            res = await enableDocument(record.id);
        }
        if (res.code == 0) {
            const list = dataList.map((item, i) => {
                if (index == i) {
                    item.status = !checked ? 2 : 1;
                }
                return {
                    ...item,
                    statusText:
                        item.status == 1
                            ? intl.formatMessage({ id: 'createkb.normal', defaultMessage: '' })
                            : item.status == 2
                            ? intl.formatMessage({
                                  id: 'createkb.disabled',
                                  defaultMessage: '',
                              })
                            : intl.formatMessage({
                                  id: 'createkb.deleted',
                                  defaultMessage: '',
                              }),
                };
            });
            setCount(list);
        }
    };

    const deleteList = async (id: number, index: number) => {
        confirm({
            title: intl.formatMessage({ id: 'createkb.deleteOperation', defaultMessage: '' }),
            content: intl.formatMessage({ id: 'createkb.confirmDelete', defaultMessage: '?' }),
            onOk: async function () {
                let res = await deleteDocument(id);
                if (res.code == 0) {
                    getDocumentList(listPageNum);
                    togglePopoverVisibility(index);
                }
            },
            onCancel() {},
        });
    };

    const inputOnChange = e => {
        let text = e.target.value;

        clearTimeout(timer);

        timer = setTimeout(() => {
            inputText = text;
            listPageNum = 1;
            getDocumentList();
        }, 500);
    };

    const onclickList = (e, i) => {
        itemDatafun(e);
        handoffPagefun(false);
    };
    const popoverClick = event => {
        if (event && event.stopPropagation) {
            event.stopPropagation();
        }
    };

    const columns: TableColumnsType = [
        // {
        //     title: '#',
        //     dataIndex: 'id',
        //     className: 'max-w-60 w-12 text-[#213044] text-xs py-[15px]',
        // },
        {
            title: intl.formatMessage({ id: 'createkb.filename', defaultMessage: '' }),
            dataIndex: 'name',
            key: 'name',
            ellipsis: true,
            className: 'max-w-48 text-[#213044] text-xs py-[15px]',
        },
        {
            title: intl.formatMessage({ id: 'createkb.charCount', defaultMessage: '' }),
            dataIndex: 'word_count',
            key: 'word_count',
            className: 'max-w-48 w-24 text-[#213044] text-xs py-[15px]',
        },
        {
            title: intl.formatMessage({ id: 'createkb.recallNum', defaultMessage: '' }),
            dataIndex: 'hit_count', //paging_information
            key: 'hit_count',
            className: 'max-w-48 w-20 text-[#213044] text-xs py-[15px]',
        },
        {
            title: intl.formatMessage({ id: 'createkb.uploadTime', defaultMessage: '' }),
            dataIndex: 'created_time',
            key: 'created_time',
            className: 'max-w-48 w-44 text-[#213044] text-xs py-[15px]',
            sorter: true,
        },
        {
            title: intl.formatMessage({ id: 'createkb.status', defaultMessage: '' }),
            dataIndex: 'statusText',
            key: 'statusText',
            className: 'max-w-48 w-28 text-[#213044] text-xs py-[15px]',
            render: (text, record, index) => {
                return (
                    <div onClick={popoverClick}>
                        <Switch
                            className={record.status == 2 ? '' : 'bg-[#1B64F3]'}
                            key={text}
                            defaultChecked={record.status == 2 ? false : true}
                            onChange={checked => onChange(checked, text, record, index)}
                            size="small"
                        />
                    </div>
                );
            },
        },
        {
            title: intl.formatMessage({ id: 'createkb.action' }),
            dataIndex: 'id',
            key: 'id',
            className: 'max-w-48 w-20 text-[#213044] text-xs py-[15px]',
            render: (text, record, index) => {
                return (
                    <div onClick={popoverClick}>
                        <img
                            src="/icons/delete.svg"
                            className="w-4 h-4"
                            onClick={() => {
                                deleteList(text, index);
                            }}
                        />
                    </div>
                );
            },
        },
    ];

    const getList = async e => {
        // Update file list with current upload state
        console.log('getList called with:', e.fileList.length, 'files');
        console.log(
            'File names:',
            e.fileList.map(f => f.name),
        );
        console.log(
            'File statuses:',
            e.fileList.map(f => `${f.name}: ${f.status}`),
        );
  
        const hasUploading = e.fileList.some(file => file.status === 'uploading');
        setIsUploading(hasUploading);
     
        const hasError = e.fileList.some(file => file.status === 'error');
        if (hasError && !hasUploading) {
        
            setIsUploading(false);
        }
        
        setUploadFileList(e.fileList);
    };

    const getDocumentList = async (page = 1, sorts = sortscontent) => {
        loadingfun(true);
        let data = {
            app_id: createkbInfo.app_id,
            page,
            page_size: 10,
            name: inputText,
        };
        let res = await documentList(data);
        if (res.code == 0) {
            const list = res.data.data.map((item, i) => {
                return {
                    ...item,
                    statusText:
                        item.status == 1
                            ? intl.formatMessage({ id: 'createkb.normal' })
                            : item.status == 2
                            ? intl.formatMessage({
                                  id: 'createkb.disabled',
                              })
                            : intl.formatMessage({
                                  id: 'createkb.deleted',
                              }),
                };
            });
            setCount(list);
            setData(res.data);
        }
        loadingfun(false);
    };

    const handleTableChange = (pagination, filters, sorter) => {
        sortscontent = sorter.order == 'ascend' ? 'asc' : sorter.order == 'descend' ? 'desc' : null;
        listPageNum = pagination.current;
        getDocumentList(listPageNum, sortscontent);
    };

    const pagination = {
        total: datacontent != null ? datacontent.paging_information.total_count : 0,
        current: listPageNum,
        hideOnSinglePage: true,
    };

    useEffect(() => {
        if (createkbInfo.app_id) {
            appTypefun(!createkbInfo.type ? 1 : 2);
            getDocumentList();
        }
    }, []);

    // Use useCallback to wrap onFinish function to avoid unnecessary re-renders
    const onFinish = useCallback(async (values) => {
        const completedFiles = uploadFileList.filter(
            item => item.status === 'done' && item.response,
        );

        if (completedFiles.length === 0) {
            message.warning(intl.formatMessage({ id: 'createkb.upload.selectFileFirst' }));
            return;
        }

        try {
            let res = await addDocument({
                app_id: createkbInfo.app_id * 1,
                file_ids: completedFiles.map(item => item.response.data.file_id * 1),
                process_rule_id: 1,
                data_source_type: 1,
                text_split_config: {
                    ...initValues,
                    ...values,
                },
            });

            if (res.code == 0) {
                // Clear upload file list completely
                setUploadFileList([]);
                
                // Reset form values to initial values
                formValuesRef.current = initValues;

                // Reset upload component with a slight delay to ensure state is updated
                setTimeout(() => {
                    uploadViewRef.current?.reset();
                }, 100);

                // Refresh document list
                getDocumentList(listPageNum);

                // Show success message
                message.success(
                    intl.formatMessage({
                        id: 'createkb.upload.addToKbSuccess',
                        defaultMessage: 'Files successfully added to knowledge base',
                    }),
                );

                console.log('Files cleared and component reset');
            } else {
                message.error(
                    intl.formatMessage({
                        id: 'createkb.upload.addToKbFailed',
                        defaultMessage: 'Failed to add files to knowledge base',
                    }),
                );
            }
        } catch (error) {
            console.error('Add document error:', error);
            message.error(
                intl.formatMessage({
                    id: 'createkb.upload.addToKbFailed',
                    defaultMessage: 'Failed to add files to knowledge base',
                }),
            );
        }
    }, [uploadFileList, createkbInfo.app_id, intl]);

    const handleDeleteUploadedFile = (indexToDelete: number) => {
        setUploadFileList(prevList => {
            const fileToDelete = prevList[indexToDelete];
            const newList = prevList.filter((_, index) => index !== indexToDelete);
            console.log(`File deleted: ${fileToDelete?.name} at index ${indexToDelete}`);
            console.log(
                `Remaining files:`,
                newList.map(f => f.name),
            );
            console.log(`File list length changed from ${prevList.length} to ${newList.length}`);
            
            const stillUploading = newList.some(file => file.status === 'uploading');
            setIsUploading(stillUploading);
            
            return newList;
        });
    };

    const handleClearAllFiles = () => {
        // Clear the parent component state first
        setUploadFileList([]);
     
        setIsUploading(false);

        // Reset upload component with a delay to ensure state synchronization
        setTimeout(() => {
            uploadViewRef.current?.reset();
        }, 100);

        // Show confirmation message
        message.info(
            intl.formatMessage({
                id: 'createkb.upload.allFilesCleared',
                defaultMessage: 'All files cleared',
            }),
        );

        console.log('All files manually cleared');
    };

    return (
        <>
            {handoffPage ? (
                datacontent != null ? (
                    <div className="h-full bg-white w-full">
                        <div className="w-full py-[30px] flex items-center ">
                            <img src="/icons/flag.svg" className="w-4 h-4" />
                            <span className="ml-[10px] text-[#213044] text-[18px] leading-[25px] font-medium">
                                {appType == 2
                                    ? getLocale() == 'zh-CN'
                                        ? datacontent.dataset_detail.nickname +
                                          intl.formatMessage({ id: 'createkb.knowledge.base.of' })
                                        : intl.formatMessage({ id: 'createkb.knowledge.base.of' }) +
                                          datacontent.dataset_detail.nickname
                                    : appType == 1
                                    ? intl.formatMessage({
                                          id: 'createkb.editKB',
                                      })
                                    : intl.formatMessage({
                                          id: 'createkb.createKnowledgeBase',
                                      })}
                            </span>
                        </div>
                        <div className="text-[#333333] text-[16px] leading-[22px] font-medium">
                            {intl.formatMessage({
                                id: 'createkb.documentSettings',
                            })}
                        </div>
                        <div className="text-[#555555] text-[12px] leading-[17px] font-medium pt-[30px]">
                            {intl.formatMessage({
                                id: 'createkb.uploadDoc',
                            })}
                        </div>

                        <UploadView
                            ref={uploadViewRef}
                            fun={getList}
                            createkbInfo={createkbInfo}
                            fileList={uploadFileList}
                        ></UploadView>
                        {uploadFileList.length > 0 && (
                            <div className="mt-4 p-4 border border-gray-200 rounded-lg ">
                                <div className="flex justify-between items-center mb-2">
                                    <h4 className="text-base font-medium text-gray-700">
                                        {intl.formatMessage({
                                            id: 'createkb.fileList',
                                            defaultMessage: '',
                                        })}
                                    </h4>
                                    <button
                                        onClick={handleClearAllFiles}
                                        className="text-xs text-red-500 hover:text-red-700 transition-colors px-2 py-1 border border-red-200 rounded hover:border-red-300"
                                    >
                                        {intl.formatMessage({
                                            id: 'createkb.upload.clearAll',
                                            defaultMessage: 'Clear All',
                                        })}
                                    </button>
                                </div>
                                <ul className="space-y-1">
                                    {uploadFileList.map((item, index) => {
                                        return (
                                            <li
                                                key={item.uid || index}
                                                className="flex items-center justify-between text-sm text-gray-600 bg-gray-50 p-3 rounded"
                                            >
                                                <div className="flex-1 mr-2">
                                                    <div className="flex justify-between items-center mb-2">
                                                        <span className="truncate font-medium">
                                                            {item.name}
                                                        </span>
                                                        <div className="flex items-center space-x-2">
                                                            {item.status === 'uploading' && (
                                                                <button
                                                                    onClick={() => {
                                                                        if (item.xhr) {
                                                                            item.xhr.abort();
                                                                        }
                                                                        handleDeleteUploadedFile(
                                                                            index,
                                                                        );
                                                                    }}
                                                                    className="text-gray-500 hover:text-gray-700 transition-colors text-xs"
                                                                >
                                                                    {intl.formatMessage({
                                                                        id: 'createkb.upload.cancel',
                                                                    })}
                                                                </button>
                                                            )}
                                                            <button
                                                                onClick={() =>
                                                                    handleDeleteUploadedFile(index)
                                                                }
                                                                className="text-red-500 hover:text-red-700 transition-colors"
                                                                aria-label={`${intl.formatMessage({
                                                                    id: 'createkb.deleteFile',
                                                                })} ${item.name}`}
                                                                title={`${intl.formatMessage({
                                                                    id: 'createkb.deleteFile',
                                                                })} ${item.name}`}
                                                            >
                                                                <DeleteOutlined />
                                                            </button>
                                                        </div>
                                                    </div>

                                                    {item.status === 'uploading' && (
                                                        <div className="space-y-1">
                                                            <Progress
                                                                percent={Math.round(
                                                                    item.percent || 0,
                                                                )}
                                                                size="small"
                                                                status="active"
                                                                strokeColor="#1B64F3"
                                                            />
                                                            <div className="text-xs text-blue-500 font-medium">
                                                                {intl.formatMessage({
                                                                    id: 'createkb.upload.progress',
                                                                })}{' '}
                                                                {Math.round(item.percent || 0)}%
                                                                {item.size && (
                                                                    <span className="text-gray-400 ml-2">
                                                                        (
                                                                        {(
                                                                            item.size /
                                                                            1024 /
                                                                            1024
                                                                        ).toFixed(2)}
                                                                        MB)
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {item.status === 'done' && (
                                                        <div className="flex items-center space-x-2">
                                                            <div className="w-full bg-green-100 rounded-full h-2">
                                                                <div className="bg-green-500 h-2 rounded-full w-full"></div>
                                                            </div>
                                                            <div className="text-xs text-green-600 font-medium whitespace-nowrap">
                                                                {intl.formatMessage({
                                                                    id: 'createkb.upload.complete',
                                                                })}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {item.status === 'error' && (
                                                        <div className="space-y-1">
                                                            <div className="flex items-center space-x-2">
                                                                <div className="w-full bg-red-100 rounded-full h-2">
                                                                    <div className="bg-red-500 h-2 rounded-full w-full"></div>
                                                                </div>
                                                                <div className="text-xs text-red-600 font-medium whitespace-nowrap">
                                                                    {intl.formatMessage({
                                                                        id: 'createkb.upload.failed',
                                                                    })}
                                                                </div>
                                                            </div>
                                                            {item.error && (
                                                                <div className="text-xs text-red-500 mt-1">
                                                                    {item.error.message ||
                                                                        intl.formatMessage({
                                                                            id: 'createkb.error.unknown',
                                                                        })}
                                                                </div>
                                                            )}
                                                            <button
                                                                onClick={() => {
                                                                    message.info(
                                                                        intl.formatMessage({
                                                                            id: 'createkb.instruction.retryUpload',
                                                                        }),
                                                                    );
                                                                }}
                                                                className="text-xs text-blue-500 hover:text-blue-700"
                                                            >
                                                                {intl.formatMessage({
                                                                    id: 'createkb.upload.retry',
                                                                })}
                                                            </button>
                                                        </div>
                                                    )}
                                                </div>
                                            </li>
                                        );
                                    })}
                                </ul>
                               
                                {/* Use the externally extracted form component with necessary props */}
                                <UploadPrevForm 
                                    onFinish={onFinish} 
                                    isUploading={isUploading} 
                                    formValuesRef={formValuesRef}
                                    intl={intl}
                                />
                            </div>
                        )}
                        <div className="flex justify-between pt-[30px]">
                            <span className="text-[#213044] text-xs font-medium">
                                {intl.formatMessage({
                                    id: 'createkb.documentList',
                                })}
                            </span>
                        </div>
                        <div className="flex items-center w-full pt-[10px]">
                            <Input
                                placeholder={intl.formatMessage({
                                    id: 'createkb.searchDoc',
                                })}
                                onChange={inputOnChange}
                                className="w-[782px] h-10 mr-5"
                                prefix={<SearchOutlined />}
                            />
                        </div>
                        {wordList(
                            columns,
                            loadingType,
                            dataList,
                            pagination,
                            onclickList,
                            handleTableChange,
                        )}
                        <div className="mt-[30px]">
                            <Button
                                type="primary"
                                className="py-[10px] h-[40px] px-[15px] bg-[#1B64F3] text-white text-[14px] leading-[20px] font-medium"
                                onClick={next}
                            >
                                {intl.formatMessage({
                                    id: 'createkb.enterRecallTest',
                                })}
                            </Button>
                        </div>
                    </div>
                ) : (
                    ''
                )
            ) : (
                <Fileset fun={filesetThen} item={itemData} createkbInfo={createkbInfo}></Fileset>
            )}
        </>
    );
};

export default UploadList;
