/*
 * @
 */
import {
    documentList,
    retrievalHistoryDetail,
    retrievalHistoryList,
    retrievalTest,
} from '@/api/createkb';
import { useIntl } from '@umijs/max';
import { Button, Card, Col, Input, message, Row, Table } from 'antd';
import React, { useEffect, useRef, useState } from 'react';

interface DataType {
    key: React.Key;
    name: string;
    age: number;
    address: string;
}

let pageNum = 1;
const Kbtext = ({ createkbInfo }: any) => {
    const intl = useIntl();
    const columns = [
        // {
        //     title: 'id',
        //     dataIndex: 'id',
        //     width: '15%',
        // },
        {
            title: intl.formatMessage({ id: 'createkb.text', defaultMessage: '' }),
            dataIndex: 'input',
            ellipsis: true,
        },
        {
            title: intl.formatMessage({
                id: 'createkb.recallParagraph',
                defaultMessage: '',
            }),
            dataIndex: 'document_segment_num',
            width: '15%',
        },
        {
            title: intl.formatMessage({ id: 'createkb.time', defaultMessage: '' }),
            dataIndex: 'created_time',
            width: '25%',
        },
    ];
    let [data, setData] = useState([]);
    let [userData, userDatafun] = useState(null);
    let [jsoncontent, jsoncontentfun] = useState(null);
    let [testList, testListfun] = useState([]);
    let [showSkeleton, showSkeletonfun] = useState(false);
    let [inputText, inputTextfun] = useState('');
    const divRef = useRef(null);
    const [tabHeight, tabHeightfun] = useState(0);

    const testBtn = async () => {
        if (inputText != '') {
            showSkeletonfun(true);
            testListfun([]);
            let res = await retrievalTest(
                {
                    user_input: inputText,
                },
                createkbInfo.app_id,
            );
            if (res.code == 0) {
                if (res.data.data.length <= 0) {
                    message.error(
                        intl.formatMessage({
                            id: 'createkb.saveSuccess',
                            defaultMessage: '',
                        }),
                    );
                    // return
                }
                testListfun(res.data.data);
            } else {
                message.error(res.detail);
            }
            showSkeletonfun(false);
            getretrieval_history_list();
        } else {
            showSkeletonfun(false);
            testListfun([]);
            message.error(
                intl.formatMessage({ id: 'createkb.testInput', defaultMessage: '' }),
            );
        }
    };

    const inputChange = async e => {
        inputTextfun(e.target.value);
    };

    const paginationChange = e => {
        pageNum = e;
        getretrieval_history_list();
    };

    const onclickList = async e => {
        showSkeletonfun(true);
        let res = await retrievalHistoryDetail(e.id);
        if (res.code == 0) {
            testListfun(res.data.data);
        } else {
            message.error(res.detail);
        }
        showSkeletonfun(false);
        inputTextfun(e.input);
    };

    const getretrieval_history_list = async (page = pageNum) => {
        let res = await retrievalHistoryList(
            {
                page,
            },
            createkbInfo.app_id,
        );
        if (res.code == 0) {
            setData(res.data.data);
            jsoncontentfun(res.data);
        }
    };

    const getDocumentList = async (page = 1) => {
        let data = { app_id: createkbInfo.app_id };
        let res = await documentList(data);
        if (res.code == 0) {
            const list = res.data.data.map((item, i) => {
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
            userDatafun(res.data);
        }
    };

    useEffect(() => {
        getretrieval_history_list();
        getDocumentList();
        setTimeout(() => {
            if (divRef.current) {
                tabHeightfun(divRef.current.offsetHeight - 55 - 82);
            }
        }, 200);
    }, []);
    return (
        <>
            {jsoncontent != null ? (
                <div className="h-full pb-[30px]">
                    <div className="w-full py-[30px] flex items-center ">
                        <img src="/icons/flag.svg" className="w-4 h-4" />
                        <span className="ml-[10px] text-[#213044] text-base font-medium">
                            {!createkbInfo.type && userData != null
                                ? userData.dataset_detail.nickname +
                                  intl.formatMessage({
                                      id: 'createkb.knowledge.base.of',
                                      defaultMessage: '',
                                  })
                                : intl.formatMessage({
                                      id: 'createkb.editKB',
                                      defaultMessage: '',
                                  })}
                        </span>
                    </div>
                    <div className="flex w-full" style={{ height: 'calc(100% - 84px)' }}>
                        <Row gutter={0} style={{ marginRight: '0px', marginLeft: '0px' }}>
                            <Col className="pb-[30px] h-2/4" span={24}>
                                <div className="w-full h-full flex flex-col">
                                    <div className="mb-5 text-[#555555] text-sm font-medium">
                                        {intl.formatMessage({
                                            id: 'createkb.recallTest',
                                            defaultMessage: '',
                                        })}
                                    </div>
                                    <div className="w-full px-[15px] py-[15px] border-[#EEEEEE] rounded-lg bg-[#F7F7F7] flex-1 min-h-0">
                                        <div
                                            className=" overflow-y-auto"
                                            style={{ height: 'calc(100% - 65px)' }}
                                        >
                                            <Row gutter={[15, 15]} className="w-full">
                                                {testList.map((x, i) => {
                                                    let score = (x.score*1).toFixed(4)
                                                    let reranking_score = x.reranking_score>0?(x.reranking_score*1).toFixed(4):0
                                                    return (
                                                        <Col
                                                            className="gutter-row w-full"
                                                            span={24}
                                                            key={x.id}
                                                        >
                                                            <Card activeTabKey={x.id} size="small">
                                                                <div className="w-full bg-white  font-normal text-[12px] rounded-lg">
                                                                    <div className="break-all text-[#213044] leading-[17px]">
                                                                        {x.content}
                                                                    </div>
                                                                    <div className="text-[#BBBBBB] mt-[15px] leading-[17px]">
                                                                        {' '}
                                                                        {intl.formatMessage({id: 'createkb.source',defaultMessage: ''})}： { x.name}
                                                                    </div>
                                                                    <div className="text-[#BBBBBB] mt-[15px]  leading-[17px]">
                                                                        {' '}
                                                                        {intl.formatMessage({
                                                                            id: 'createkb.matchScore',

                                                                        })}
                                                                        ： {score}
                                                                    </div>
                                                                    {
                                                                        reranking_score==0?'':<div className="text-[#BBBBBB] mt-[15px] leading-[17px]">
                                                                        {' '}
                                                                        {intl.formatMessage({
                                                                            id: 'createkb.sortScore',

                                                                        })}
                                                                        ： {reranking_score}
                                                                    </div>
                                                                    }

                                                                </div>
                                                            </Card>
                                                        </Col>
                                                    );
                                                })}
                                            </Row>
                                        </div>

                                        <div className="bg-white flex items-center rounded-lg mt-[15px] p-[10px]">
                                            <Input
                                                className=" custom-textarea"
                                                onChange={inputChange}
                                                variant="borderless"
                                                placeholder={intl.formatMessage({
                                                    id: 'createkb.briefText',

                                                })}
                                                maxLength={200}
                                                showCount
                                                value={inputText}
                                                onPressEnter={testBtn}
                                            />
                                            <div className="flex justify-end">
                                                <Button
                                                    type="primary"
                                                    loading={showSkeleton}
                                                    onClick={testBtn}
                                                    style={{ background: 'rgba(27,100,243,.1)' }}
                                                    className="w-[30px] h-[30px] rounded-md flex justify-center items-center p-0"
                                                >
                                                    {showSkeleton ? (
                                                        ''
                                                    ) : (
                                                        <img
                                                            src="/icons/fs.svg"
                                                            className="w-4 h-4"
                                                        />
                                                    )}
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </Col>
                            <div className="h-2/4" ref={divRef}>
                                <Col span={24}>
                                    <div className="w-full h-full">
                                        <div className=" mb-[20px] text-[#555555] text-sm font-medium">
                                            {intl.formatMessage({
                                                id: 'createkb.recentQuery',

                                            })}
                                        </div>
                                        <div className="w-[900px] rounded-md border-[#eeeeee] border rounded-lg">
                                            <Table
                                                rowKey="id"
                                                columns={columns}
                                                dataSource={data}
                                                locale={{
                                                    emptyText: (
                                                        <div className="text-[#666666] text-[14px] leading-[20px] font-normal">
                                                            <span>
                                                                {intl.formatMessage({
                                                                    id: 'createkb.no.data.available',

                                                                })}
                                                            </span>
                                                        </div>
                                                    ),
                                                }}
                                                pagination={{
                                                    pageSize:
                                                        jsoncontent.paging_information.page_size,
                                                    total: jsoncontent.paging_information
                                                        .total_count,
                                                    onChange: paginationChange,
                                                    style: {
                                                        margin: '0px',
                                                        marginTop: '10px',
                                                    },

                                                    hideOnSinglePage: true,
                                                }}
                                                onRow={(record, i) => {
                                                    return {
                                                        onClick: () => onclickList(record),
                                                        style: { cursor: 'pointer' },
                                                    };
                                                }}
                                                scroll={tabHeight != 0 ? { y: tabHeight } : {}}
                                            />
                                        </div>
                                    </div>
                                </Col>
                            </div>
                        </Row>
                    </div>
                </div>
            ) : (
                ''
            )}
        </>
    );
};

export default Kbtext;
