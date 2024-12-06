/*
 * @
 */
import { disableSegment, documentSegmentsList, enableSegment } from '@/api/createkb';
import { SearchOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Divider, Flex, Input, List, Radio, Select, Switch } from 'antd';
import { useEffect, useState } from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';

let content_status = '0';
let sort = 'hit_count asc';
let page_number = 1;
let inputText = '';
let timer;

let wordData;

const Fileset = ({ item, fun, createkbInfo }: any) => {
    const intl = useIntl();
    let sz = [
        {
            title:
                intl.formatMessage({ id: 'createkb.charLimit', defaultMessage: '' }) +
                '：',
            value: '',
        },
        {
            title:
                intl.formatMessage({ id: 'createkb.avgChar', defaultMessage: '' }) +
                '：',
            value: '',
        },
        {
            title:
                intl.formatMessage({ id: 'createkb.sectionNum', defaultMessage: '' }) +
                '：',
            value: '',
        },
        {
            title:
                intl.formatMessage({ id: 'createkb.totalRecall', defaultMessage: '' }) +
                '：',
            value: '',
        },
        {
            title:
                intl.formatMessage({ id: 'createkb.embedTime', defaultMessage: '' }) + '：',
            value: '',
        },
        {
            title:
                intl.formatMessage({ id: 'createkb.embedCost', defaultMessage: '' }) + '：',
            value: '',
        },
    ];

    const [loading, setLoading] = useState(false);

    const [data, setData] = useState([]);

    const [content, contentfun] = useState(null);

    const returnpage = () => {
        fun('return');
    };
    function wordDatafuns() {
        return sz.map(x => {
            return (
                <div className="mr-[40px]" key={`${x.title}`}>
                    <div className="flex items-center grow shrink-0">
                        <div className="text-[#666666] text-[12px] leading-[17px] font-normal">
                            {x.title}
                        </div>
                        <div className="text-[#213044] text-[12px] leading-[17px] font-medium">
                            {x.value}
                        </div>
                    </div>
                </div>
            );
        });
    }


    const inputOnChange = e => {
        let text = e.target.value;

        clearTimeout(timer);

        timer = setTimeout(() => {
            setData([]);
            inputText = text;
            loadMoreData(1);
        }, 500);
    };

    const scrollBottom = () => {
        page_number += 1;
        loadMoreData(page_number);
    };

    const switchChange = async (type, item) => {
        let res;
        if (type) {

            res = enableSegment(item.id);
        } else {

            res = disableSegment(item.id);
        }
    };

    const loadMoreData = async (page = 1) => {
        page_number = page;
        let res = await documentSegmentsList({
            document_id: item.id,
            page,
            page_size: 10,
            hit_count: sort,
            content: inputText,
            status: content_status,
        });
        contentfun(res.data);
        if (content == null) {
            sz[0].value = res.data.seg_set.seg_Len; //Seg Len
            sz[1].value = res.data.seg_set.seg_Avg; //Seg Avg
            sz[2].value = res.data.seg_set.seg_Num; //Seg Num
            sz[3].value = res.data.seg_set.hit_Num; //Hit Num
            sz[4].value = res.data.seg_set.Embedding_Time; //Embedding Time
            sz[5].value = res.data.seg_set.Embedding_Token; //Seg Token
            wordData = wordDatafuns();
        }

        setData(praveData => [...praveData, ...res.data.data]);
    };

    useEffect(() => {
        loadMoreData();
    }, []);
    return (
        <>
            <div className="py-[30px] bg-white overflow-hidden w-full h-full flex flex-col">
                <div>

                    <div className="border-b  flex items-center pb-[30px]">
                        <div
                            className="border-r mr-[10px] pr-[10px] cursor-pointer"
                            onClick={returnpage}
                        >
                            <img src="/icons/return.svg" className="w-4 h-4" />
                        </div>
                        <div className="flex items-center">
                            <img src="/icons/textIcon.svg" className="w-4 h-4" />
                            <span className="text-[#213044] leading-[25px] text-[18px] font-medium ml-[5px]">
                                {item.name}
                            </span>
                        </div>
                    </div>

                    <div className="pt-[20px] pb-[15px] text-[#555555]  text-[14px] leading-[20px] font-medium">
                        {intl.formatMessage({
                            id: 'createkb.docParams',
                            defaultMessage: '',
                        })}
                    </div>
                    <div className="w-full border border-[#EEEEEE] rounded-lg p-[15px] bg-[#F7F7F7]">
                        <Flex wrap gap="middle" align="center">
                            {wordData}
                        </Flex>
                    </div>

                    <div className="pt-[20px] pb-[15px] text-[#555555] text-[14px] leading-[20px] font-medium">
                        {intl.formatMessage({ id: 'createkb.docPara', defaultMessage: '' })}{' '}
                        {content != null ? content.paging_information.total_count : ''}
                    </div>
                    <div className="w-full flex justify-between items-center">
                        <div className="sticky-0 flex items-center">
                            <Select
                                defaultValue={`${content_status}`}
                                style={{ width: 114, height: 32, background: '#F7F7F7' }}
                                onSelect={e => {
                                    content_status = e;
                                    setData([]);
                                    loadMoreData(1);
                                }}
                                options={[
                                    {
                                        value: '0',
                                        label: intl.formatMessage({
                                            id: 'createkb.all',
                                            defaultMessage: '',
                                        }),
                                    },
                                    {
                                        value: '1',
                                        label: intl.formatMessage({
                                            id: 'createkb.enabled',
                                            defaultMessage: '',
                                        }),
                                    },
                                    {
                                        value: '2',
                                        label: intl.formatMessage({
                                            id: 'createkb.disabled',
                                            defaultMessage: '',
                                        }),
                                    },
                                ]}
                            />
                            <Input
                                size="large"
                                placeholder={intl.formatMessage({
                                    id: 'createkb.search',
                                    defaultMessage: '',
                                })}
                                prefix={<SearchOutlined className="text-[#213044] opacity-30" />}
                                onChange={inputOnChange}
                                className="w-[300px] text-sm h-8 ml-5"
                            />
                        </div>
                        <div className="flex-1 justify-end flex items-center">

                            <div className="flex items-center text-[#555555] text-[14px] leading-[20px] font-normal">
                                <span>
                                    {intl.formatMessage({
                                        id: 'createkb.recallSort'
                                    })}
                                    ：
                                </span>
                                <Radio.Group
                                    defaultValue={sort}
                                    onChange={e => {
                                        sort = e.target.value;
                                        setData([]);
                                        loadMoreData(1);
                                    }}
                                    size="small"
                                >
                                    <Radio value={'hit_count asc'}>
                                        {intl.formatMessage({
                                            id: 'createkb.highToLow',

                                        })}
                                    </Radio>
                                    <Radio value={'hit_count desc'}>
                                        {intl.formatMessage({
                                            id: 'createkb.lowToHigh',

                                        })}
                                    </Radio>
                                </Radio.Group>
                            </div>
                        </div>
                    </div>
                </div>

                {content != null ? (
                    <div className="overflow-y-auto flex-1 mt-4" id="lists">
                        <InfiniteScroll
                            dataLength={data.length}
                            next={scrollBottom}
                            hasMore={data.length < content.paging_information.total_count}
                            loader={false}
                            endMessage={
                                data.length <= 0 ? (
                                    ''
                                ) : (
                                    <Divider plain>
                                        {intl.formatMessage({
                                            id: 'createkb.bottom',

                                        })}
                                    </Divider>
                                )
                            }
                            scrollableTarget="lists"
                        >
                            <List
                                dataSource={data}
                                split={false}
                                renderItem={item => (
                                    <List.Item key={item.id} style={{ padding: '0px' }}>
                                        <div className="w-full rounded-lg bg-[#F7F7F7] p-[15px] mb-[15px]">
                                            <div className="w-full flex items-center">
                                                <div className="py-1 rounded-md px-2 border border-[#D8D8D8] flex items-center justify-center text-[#213044] text-sm">
                                                    #
                                                    {item.segnum <= 9
                                                        ? '00' + item.segnum
                                                        : item.segnum <= 99
                                                        ? '0' + item.segnum
                                                        : item.segnum}
                                                </div>
                                                <div className="flex items-center ml-8">
                                                    <img
                                                        src="/icons/zishu.svg"
                                                        className="w-4 h-4"
                                                    />
                                                    <div className="ml-[5px] text-[#213044] text-sm">
                                                        {item.word_count}
                                                    </div>
                                                </div>
                                                <div className="flex items-center ml-8">
                                                    <img src="/icons/zh.svg" className="w-4 h-4" />
                                                    <div className="ml-[5px] text-[#213044] text-sm">
                                                        {item.hit_count}
                                                    </div>
                                                </div>
                                                <div className="ml-8 ">
                                                    <Switch
                                                        defaultChecked={
                                                            item.status == 2 ? false : true
                                                        }
                                                        onChange={checked =>
                                                            switchChange(checked, item)
                                                        }
                                                        disabled={createkbInfo.type}
                                                        key={item.id}
                                                        size="small"
                                                    />
                                                </div>
                                            </div>
                                            <div className="pt-5">
                                                <span className="text-[#213044] text-sm">
                                                    {item.content}
                                                </span>
                                                {/* <Input.TextArea
                                                    rows={4}
                                                    variant="filled"
                                                    autoSize={true}
                                                    defaultValue={item.content}
                                                /> */}
                                            </div>
                                        </div>
                                    </List.Item>
                                )}
                            />
                        </InfiniteScroll>
                    </div>
                ) : (
                    ''
                )}
            </div>
        </>
    );
};

export default Fileset;
