
import { SearchOutlined } from '@ant-design/icons';
import { Button, Input, Switch, Table, TableColumnsType,Modal } from 'antd';
import { useEffect, useState } from 'react';
import UploadView from './Upload/upload';

import {
    addDocument,
    deleteDocument,
    disableDocument,
    documentList,
    enableDocument,
} from '@/api/createkb';
import { getLocale, useIntl } from '@umijs/max';
import Fileset from '../Fileset';
let listPageNum = 1;
let timer;
let inputText = '';
let sortscontent = null;


//
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

    const onChange = async (checked: boolean, text: String, record: Object , index: Number) => {
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
              onOk :async function() {
                    let res = await deleteDocument(id);
                    if (res.code == 0) {
                        getDocumentList(listPageNum);
                        togglePopoverVisibility(index);
                    }
              },
              onCancel() {

              },
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
                            className={record.status == 2?'':'bg-[#1B64F3]'}
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
        loadingfun(true);

        if (e.file.status == 'done') {

            await addDocument({
                app_id: createkbInfo.app_id * 1,
                file_ids: [e.file.response.data.file_id * 1],
                process_rule_id: 1,
                data_source_type: 1,
            });

            getDocumentList(listPageNum);
        }
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
                            ? intl.formatMessage({ id: 'createkb.normal'})
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

    return (
        <>
            {handoffPage ? (
                datacontent != null ? (
                    <div className="h-full bg-white w-full">
                        <div className="w-full py-[30px] flex items-center ">
                            <img src="/icons/flag.svg" className="w-4 h-4" />
                            <span className="ml-[10px] text-[#213044] text-[18px] leading-[25px] font-medium">
                                {appType == 2
                                    ? getLocale()=='zh-CN'?datacontent.dataset_detail.nickname +intl.formatMessage({ id: 'createkb.knowledge.base.of', }) :intl.formatMessage({ id: 'createkb.knowledge.base.of', })+datacontent.dataset_detail.nickname 
                                    
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
                        <UploadView fun={getList} createkbInfo={createkbInfo}></UploadView>

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
