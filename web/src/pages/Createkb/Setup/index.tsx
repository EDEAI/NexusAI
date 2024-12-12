
import { datasetSet, documentList, getInforMation } from '@/api/createkb';
import { PostappsCreate } from '@/api/creation';
import { createappdata } from '@/utils/useUser';
import { useIntl } from '@umijs/max';
import { Button, Card, Col, Form, Row, Spin, Switch, message } from 'antd';
import { useEffect, useState } from 'react';
const Setup = ({ createkbInfo, fun }: any) => {
    const intl = useIntl();

    const [datacontent, setData] = useState(null);
    const [showSpin, showSpinfun] = useState(false);


    const [EmbeddingKey, EmbeddingKeyfun] = useState(1);
    const [ispublice, setispublice] = useState(1);
    const [suppliersdata, setSuppliersdata] = useState(null);

    const [appType, appTypefun] = useState(1);

    const switchEmbeddingKey = e => {
        if (!createkbInfo.type) {
            EmbeddingKeyfun(e);
        }
    };

    const selectClick = (e: any) => {
        setispublice(e == true ? 1 : 0);
    };

    const returnList = () => {
        fun({ type: 'return' });
    };

    const setJsonData = async () => {

        showSpinfun(true);
        if (!createkbInfo.app_id) {

            const data = await PostappsCreate(createappdata('GET'));
            if (data.code == 0) {
                fun({ type: 'set', data: data.data.app_id });
            } else {
                message.error(
                    intl.formatMessage({
                        id: 'createkb.creationFailed',
                        defaultMessage: '',
                    }),
                );
                return;
            }
        }
        let data = {
            app_id: createkbInfo.app_id, //id
            name: datacontent.name,
            description: datacontent.description,
            public: ispublice,
            mode: EmbeddingKey,
        };
        let res = await datasetSet(data);
        if (res.code == 0) {

            message.success(
                intl.formatMessage({ id: 'createkb.setupSuccess', defaultMessage: '' }),
            );
            setTimeout(() => {
                fun({ type: 'next', data: '2' });
                showSpinfun(false);
            }, 1000);
        } else {
            message.error(
                intl.formatMessage({ id: 'createkb.settingFailed', defaultMessage: '' }),
            );
            showSpinfun(false);
        }
    };

    const getDocumentList = async (page = 1) => {
        let res = await documentList({
            app_id: createkbInfo.app_id,
            page,
            page_size: 10,
            name: '',
        });
        if (res.code == 0) {
            setispublice(res.data.dataset_detail.is_public);
            EmbeddingKeyfun(res.data.dataset_detail.mode);
            setData({
                name: res.data.dataset_detail.name,
                description: res.data.dataset_detail.description,
                nickname: res.data.dataset_detail.nickname,
            });
        }
    };

    const getInformation = async () => {
        let res = await getInforMation();
        if (res.code == 0) {
            setSuppliersdata(res.data.data);
        }
    };


    useEffect(() => {

        if (createkbInfo.app_id) {

            appTypefun(!createkbInfo.type ? 1 : 2);
            getDocumentList();
        } else {

            setData({
                name: createkbInfo.name,
                description: createkbInfo.description,
            });

            appTypefun(3);
        }
        getInformation();
    }, []);

    return (
        <>
            {datacontent != null ? (
                <div className="bg-white h-full flex flex-col w-full relative">
                    <div className="w-full py-[30px] flex items-center ">
                        <img src="/icons/flag.svg" className="w-4 h-4" />
                        <span className="ml-[10px] text-[#213044] text-[18px] leading-[25px] font-medium">
                            {appType == 2
                                ? intl.formatMessage({
                                      id: 'createkb.knowledge.base.of',
                                      defaultMessage: '',
                                  }) +' '+ datacontent.nickname
                                : appType == 1
                                ? intl.formatMessage({
                                      id: 'createkb.editKB',
                                      defaultMessage: '',
                                  })
                                : intl.formatMessage({
                                      id: 'createkb.createKnowledgeBase',
                                      defaultMessage: '',
                                  })}
                        </span>
                    </div>
                    <div className=" pb-[30px] bg-white flex-1">
                        <Row className="h-full">
                            <Col span={24} className="flex flex-col justify-between">
                                <div className="text-[#333333] text-[16px] leading-[22px] font-medium">
                                    {intl.formatMessage({
                                        id: 'createkb.settings',
                                        defaultMessage: '',
                                    })}
                                </div>
                                <div className="flex-1">
                                    <Form layout="vertical">
                                        <div className="pt-[30px] flex items-start text-[12px]">
                                            <span className="mr-[2px] text-[#E80000] leading-[17px] font-medium">
                                                *
                                            </span>
                                            <span className="text-[#555555] font-medium">
                                                {intl.formatMessage({
                                                    id: 'createkb.name',
                                                    defaultMessage: '',
                                                })}
                                            </span>
                                        </div>
                                        <div className="w-full mt-[15px] p-[15px] bg-[#F7F7F7] border border-[#EEEEEE] rounded-lg text-[12px] text-[#213044] font-normal leading-[17px]">
                                            {datacontent.name}
                                        </div>
                                        <div className="pt-[30px] flex items-start text-[12px]">
                                            <span className="mr-[2px] text-[#E80000] leading-[17px] font-medium">
                                                *
                                            </span>
                                            <span className="text-[#555555] font-medium">
                                                {intl.formatMessage({
                                                    id: 'createkb.desc',
                                                    defaultMessage: '',
                                                })}
                                            </span>
                                        </div>
                                        <div className="w-full mt-[15px] p-[15px] bg-[#F7F7F7] border border-[#EEEEEE] rounded-lg text-[12px] text-[#213044] font-normal leading-[17px]">
                                            {datacontent.description}
                                        </div>
                                        <div className="pt-[30px] flex items-start text-[12px]">
                                            <span className="mr-[2px] text-[#E80000] leading-[17px] font-medium">
                                                *
                                            </span>
                                            <span className="text-[#555555] font-medium">
                                                {intl.formatMessage({
                                                    id: 'createkb.teamVisible',
                                                    defaultMessage: '',
                                                })}
                                            </span>
                                        </div>
                                        <div className="w-full mt-[15px]">
                                            <Switch
                                                onChange={selectClick}
                                                checked={ispublice === 1 ? true : false}
                                                size="small"
                                                disabled={createkbInfo.type}
                                            />
                                        </div>
                                        <div className="pt-[30px] flex items-start text-[12px]">
                                            <span className="mr-[2px] text-[#E80000] leading-[17px] font-medium">
                                                *
                                            </span>
                                            <span className="text-[#555555] font-medium">
                                                {intl.formatMessage({
                                                    id: 'createkb.modelSelect',

                                                })}
                                            </span>
                                        </div>
                                        <div className="flex items-center mt-[15px]">
                                            <div className="flex">
                                                <Card
                                                    onClick={() => {
                                                        switchEmbeddingKey(1);
                                                    }}
                                                    size="small"
                                                    className={
                                                        EmbeddingKey == 1
                                                            ? 'bg-[#FFFFFF]'
                                                            : 'bg-[#F7F7F7]'
                                                    }
                                                    style={{
                                                        minWidth: '440px',
                                                        cursor: createkbInfo.type
                                                            ? 'not-allowed'
                                                            : 'pointer',
                                                        borderColor:
                                                            EmbeddingKey == 1 ? '#1B64F3' : '',
                                                    }}
                                                    styles={{
                                                        body: { padding: '15px' },
                                                    }}
                                                >
                                                    <>
                                                        <p className="pb-[15px] border-b border-[#EEEEEE] flex items-center">
                                                            <img
                                                                src={
                                                                    EmbeddingKey == 1
                                                                        ? '/icons/online_select.svg'
                                                                        : '/icons/online.svg'
                                                                }
                                                                className="w-4 h-4 "
                                                            />
                                                            <span
                                                                className={
                                                                    EmbeddingKey == 1
                                                                        ? 'text-[#1B64F3] text-xs ml-[10px]'
                                                                        : 'text-[#213044] text-xs ml-[10px]'
                                                                }
                                                            >
                                                                {intl.formatMessage({
                                                                    id: 'createkb.apiEmbed',

                                                                })}
                                                            </span>
                                                        </p>
                                                        <p className="text-[#999999] mb-[10px]">
                                                            {intl.formatMessage({
                                                                id: 'createkb.vendor',

                                                            })}
                                                            : {suppliersdata?.online.suppliers_name}
                                                        </p>
                                                        <p className="mb-0 text-[#999999]">
                                                            {intl.formatMessage({
                                                                id: 'createkb.modelName',

                                                            })}
                                                            : {suppliersdata?.online.name}
                                                        </p>
                                                    </>
                                                </Card>
                                                <Card
                                                    onClick={() => {
                                                        switchEmbeddingKey(2);
                                                    }}
                                                    size="small"
                                                    className={
                                                        EmbeddingKey == 2
                                                            ? 'bg-[#FFFFFF] ml-5'
                                                            : 'bg-[#F7F7F7] ml-5'
                                                    }
                                                    style={{
                                                        minWidth: '440px',
                                                        cursor: createkbInfo.type
                                                            ? 'not-allowed'
                                                            : 'pointer',
                                                        borderColor:
                                                            EmbeddingKey == 2 ? '#1B64F3' : '',
                                                    }}
                                                    styles={{
                                                        body: { padding: '15px' },
                                                    }}
                                                >
                                                    <>
                                                        <p className="pb-[15px] border-b border-[#EEEEEE] flex items-center">
                                                            <img
                                                                src={
                                                                    EmbeddingKey == 2
                                                                        ? '/icons/local_select.svg'
                                                                        : '/icons/local.svg'
                                                                }
                                                                className="w-4 h-4 "
                                                            />
                                                            <span
                                                                className={
                                                                    EmbeddingKey == 2
                                                                        ? 'text-[#1B64F3] text-xs ml-[10px]'
                                                                        : 'text-[#213044] text-xs ml-[10px]'
                                                                }
                                                            >
                                                                {intl.formatMessage({
                                                                    id: 'createkb.localEmbed',

                                                                })}
                                                            </span>
                                                        </p>
                                                        <p className="text-[#999999] mb-[10px]">
                                                            {intl.formatMessage({
                                                                id: 'createkb.vendor',

                                                            })}
                                                            ： -
                                                        </p>
                                                        <p className="mb-0 text-[#999999]">
                                                            {intl.formatMessage({
                                                                id: 'createkb.modelName',

                                                            })}
                                                            : {suppliersdata?.local.name}
                                                        </p>
                                                    </>
                                                </Card>
                                            </div>
                                        </div>
                                    </Form>
                                    <div className="flex items-center mt-[60px]">
                                        <Button
                                            type="primary"
                                            onClick={setJsonData}
                                            className="py-[10px] h-[40px] px-[15px] bg-[#1B64F3] text-white text-[14px] leading-[20px] font-medium"
                                            disabled={createkbInfo.type}
                                            style={{
                                                cursor: createkbInfo.type ? 'not-allowed' : '',
                                            }}
                                        >
                                            {intl.formatMessage({
                                                id: 'createkb.save.and.upload.document',

                                            })}
                                        </Button>
                                        <Button
                                            type="primary"
                                            onClick={returnList}
                                            className="ml-[20px] py-[10px] h-[40px] px-[15px] bg-[#ffffff] text-[#213044] text-[14px] leading-[20px] font-medium border border-[#979797]"
                                        >
                                            {intl.formatMessage({
                                                id: 'createkb.cancel',

                                            })}
                                        </Button>
                                    </div>
                                </div>
                            </Col>
                        </Row>
                    </div>
                    {showSpin ? (
                        <div className=" absolute w-full h-full t-0 l-0 z-10 flex justify-center items-center">
                            <Spin size="large" />
                        </div>
                    ) : (
                        ''
                    )}
                </div>
            ) : (
                ''
            )}
        </>
    );
};

export default Setup;
