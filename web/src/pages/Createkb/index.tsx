
import { createappdata } from '@/utils/useUser';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { history, useIntl } from '@umijs/max';
import type { MenuProps } from 'antd';
import { Button, Menu } from 'antd';
import { useState } from 'react';
import Kbtext from './Kbtext';
import Setup from './Setup';
import UploadList from './UploadContent/index';
type MenuItem = Required<MenuProps>['items'][number];


const returnList = () => {
    history.back();
};
const Createkb = () => {
    const intl = useIntl();
    const [pageKey, pageKeyfun] = useState('1');

    const [createkb, createkbfun] = useState(createappdata('GET'));

    const items: MenuItem[] = [
        {
            key: '1',
            icon: (
                <>
                    {pageKey == '1' ? (
                        <img src="/icons/kb_setting_select.svg" className="w-4 h-4 mr-[10px]" />
                    ) : (
                        <img src="/icons/kb_setting.svg" className="w-4 h-4 mr-[10px]" />
                    )}
                </>
            ),
            label: intl.formatMessage({ id: 'createkb.settings', defaultMessage: '' }),
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '1' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '2',
            icon: (
                <>
                    {pageKey == '2' ? (
                        <img src="/icons/uptxt_select.svg" className="w-4 h-4 mr-[10px]" />
                    ) : (
                        <img
                            src="/icons/uptxt.svg"
                            className="w-4 h-4 mr-[10px]"
                            style={{ opacity: !createkb.app_id ? '0.4' : '1' }}
                        />
                    )}
                </>
            ),
            label: intl.formatMessage({
                id: 'createkb.documentSettings',
                defaultMessage: '',
            }),
            disabled: !createkb.app_id,
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '2' ? '#1B64F3' : '#213044',
            },
        },
        {
            key: '3',
            icon: (
                <>
                    {pageKey == '3' ? (
                        <img src="/icons/recall_test_select.svg" className="w-4 h-4 mr-[10px]" />
                    ) : (
                        <img
                            src="/icons/recall_test.svg"
                            className="w-4 h-4 mr-[10px]"
                            style={{ opacity: !createkb.app_id ? '0.4' : '1' }}
                        />
                    )}
                </>
            ),
            label: intl.formatMessage({ id: 'createkb.recallTest', defaultMessage: '' }),
            disabled: !createkb.app_id,
            style: {
                padding: '15px',
                width: '100%',
                margin: '0px',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '500',
                color: pageKey == '3' ? '#1B64F3' : '#213044',
            },
        },
    ];
    const notifyStateChange = data => {

        if (data.type == 'set') {
            createkb.app_id = data.data;
            createkbfun(createkb);
        }

        if (data.type == 'return') {
            returnList();
        }

        if (data.type == 'next') {
            pageKeyfun(data.data);
        }
    };
    function StepsBox() {
        const onClick: MenuProps['onClick'] = e => {
            pageKeyfun(e.key);
        };
        return (
            <>
                <div className="flex flex-col bg-white h-full">
                    <div className=" bg-white pl-[30px] pt-[30px] border-[#e5e7eb] border-solid border-r">
                        <div className="w-full flex  justify-start">
                            <div className="cursor-pointer flex items-center" onClick={returnList}>
                                <Button type="link" danger className="p-0">
                                    <ArrowLeftOutlined className="text-[#1B64F3] w-4 h-4" />
                                </Button>
                                <span className="ml-[5px] text-[#213044] text-sm">
                                    {intl.formatMessage({
                                        id: 'createkb.back',
                                        defaultMessage: '',
                                    })}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div className="w-full flex-1 px-[30px] py-[30px] bg-white border-[#e5e7eb] border-solid border-r">
                        <Menu
                            onClick={onClick}
                            style={{ width: '100%', borderInlineEnd: '1px solid rgba(0,0,0,0)' }}
                            defaultSelectedKeys={[pageKey]}
                            mode="inline"
                            items={items}
                        />
                    </div>
                </div>
            </>
        );
    }
    return (
        <div className="w-full flex bg-white" style={{ height: 'calc(100vh - 56px)' }}>
            <div className="w-[300px] shrink-0">
                <StepsBox></StepsBox>
            </div>
            <div
                className="shrink-0 h-full overflow-y-auto bg-white overflow-x-auto"
                style={{ width: 'calc(100% - 300px)' }}
            >
                <div className="w-full h-full flex xl:justify-center justify-start flex-1">
                    <div className="w-[900px] xl:px-0 px-[30px]">
                        {pageKey == '1' ? (
                            <Setup createkbInfo={createkb} fun={notifyStateChange}></Setup>
                        ) : pageKey == '2' ? (
                            <UploadList
                                createkbInfo={createkb}
                                fun={notifyStateChange}
                            ></UploadList>
                        ) : (
                            <Kbtext createkbInfo={createkb} fun={notifyStateChange}></Kbtext>
                        )}
                    </div>
                </div>
            </div>
            {/* <Footer className={'bg-[#F7F7F7]'}></Footer> */}
        </div>
    );
};

export default Createkb;
