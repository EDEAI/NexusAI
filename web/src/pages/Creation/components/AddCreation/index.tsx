import { PostappsCreate } from '@/api/creation';
import { Card, Input, message, Modal } from 'antd';
import React, { memo, useEffect, useState } from 'react';
import { history } from 'umi';
import { BASE_URL } from '@/api/request';
import { importWorkflow } from '@/api/workflow';
import { ImportOutlined, InboxOutlined } from '@ant-design/icons';
import { ProFormUploadDragger, ProFormUploadDraggerProps } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useLocation } from 'umi';
import CreationModal from '../../../../components/creationModal';
interface ChildProps {
    optionsModalId: any;
}

const AddCreation: React.FC<ChildProps> = ({ optionsModalId }) => {
    const intl = useIntl();
    const [showPopupTop, showPopupTopFun] = useState(true); // Card image
    const { TextArea } = Input;
    const transformData = [
        {
            name: intl.formatMessage({ id: 'creation.agent' }),
            path: 'Agents',
            icon: '/icons/creation/agent.svg',
            pitchicon: '/icons/creation/pitchagent.svg',
            signicon: '/icons/creation/pitchagent.svg',
            unselected: '/icons/creation/unselectedrobot.svg',
            apps_mode: 1,
        },
        {
            name: intl.formatMessage({ id: 'creation.workflow' }),
            path: 'workspace/workflow',
            icon: '/icons/creation/gongzuoliu1.svg',
            pitchicon: '/icons/creation/pitchgongzuoliu.svg',
            signicon: '/icons/creation/signgongzuoliu.svg',
            unselected: '/icons/creation/unselectedprocess.svg',
            apps_mode: 2,
        },
        // {
        //     name: intl.formatMessage({ id: 'creation.repository' }),
        //     path: 'Createkb',
        //     icon: '/icons/creation/zhishik1.svg',
        //     pitchicon: '/icons/creation/pitchskill.svg',
        //     signicon: '/icons/creation/signskill.svg',
        //     unselected: '/icons/creation/unselectedskill.svg',
        //     apps_mode: 3,
        // },
       
        {
            name: intl.formatMessage({ id: 'creation.skill' }),
            path: 'Skill',
            icon: '/icons/creation/jienng1.svg',
            pitchicon: '/icons/creation/pitchzhishik.svg',
            signicon: '/icons/creation/signzhishik.svg',
            unselected: '/icons/creation/unselectedrepository.svg',
            apps_mode: 4,
        },
    ];
    if(location.pathname=='/knowledgebase'){
        transformData.push( {
            name: intl.formatMessage({ id: 'creation.repository' }),
            path: 'Createkb',
            icon: '/icons/creation/jienng1.svg',
            pitchicon: '/icons/creation/pitchzhishik.svg',
            signicon: '/icons/creation/signzhishik.svg',
            unselected: '/icons/creation/unselectedrepository.svg',
            apps_mode: 3,
        })
    }

   
    const [isModalOpen, setIsModalOpen] = useState(false); // Create modal
    const [CreationType, setcreationType] = useState({
        name: intl.formatMessage({ id: 'creation.agent' }),
        path: 'Agents',
        icon: '/icons/creation/agent.svg',
        pitchicon: '/icons/creation/pitchagent.svg',
        signicon: '/icons/creation/pitchagent.svg',
        apps_mode: 1,
    }); // Card type 1: agent 2: workflow 3: dataset 4: custom tool
    const [CreationName, setCreationName] = useState(''); // Card name
    const [DescribeValue, setDescribeValue] = useState(''); // Card description
    const [PitchOnPhone, setPitchOnPhone] = useState({ id: 12, icon: '😒' }); // Card image

    // Card id
    useEffect(() => {
        if(location.pathname=='/knowledgebase'){
            showPopupTopFun(false)
        }
    });
    const showModal = (type: any) => {
        const newtype = transformData.filter((value: any) => {
            return value.apps_mode == type;
        });
        setIsModalOpen(true);
        setcreationType(
            newtype[0]
                ? newtype[0]
                : {
                      name: 'Agent',
                      path: 'Agents',
                      icon: '/icons/creation/agent.svg',
                      pitchicon: '/icons/creation/pitchagent.svg',
                      signicon: '/icons/creation/pitchagent.svg',
                      apps_mode: 1,
                  },
        );
    };
    // Close modal
    const handleCancel = () => {
        setIsModalOpen(false);
    };
    // Jump to page
    const Createpage = (app_id: any) => {
        history.push(`/${CreationType.path}?app_id=${app_id}&type=false`);
    };
    // Switch internal type of modal
    const RadioChange = (e: any) => {
        transformData.map((item: any) => {
            if (item.name == e.target.value) {
                console.log(item, 'item');
                setcreationType(item);
            }
        });
    };
    // Name input box
    const IconName = (e: any) => {
        setCreationName(e.target.value);
    };
    // Description input box
    const CreationDescribe = (e: any) => {
        setDescribeValue(e.target.value);
    };
    // Create button 1: agent 2: workflow 3: dataset 4: custom tool
    const handleOk = async () => {
        let res = await PostappsCreate({
            name: CreationName,
            mode: CreationType.apps_mode,
            description: DescribeValue,
            icon: PitchOnPhone.icon,
            icon_background: '',
        });
        if (res.code === 0) {
            setIsModalOpen(false);
            // Call interface to jump page
            Createpage(res.data.app_id);
        }
    };
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);

    const handleImportCancel = () => {
        // Add cancel import logic here
        console.log('Import cancelled');
        setIsImportModalOpen(false);
    };

    const ImportFileDataPopup = memo(() => {
        const [fileList, setFileList] = useState<any[]>([]);
        const uploadProps: ProFormUploadDraggerProps = {
            icon: <InboxOutlined></InboxOutlined>,
            title: intl.formatMessage({
                id: 'workflow.uploadFileText',
                defaultMessage: 'Drag file here, or click to upload',
            }),
            description: 'Upload the exported workflow yml file',

            accept: '.yml,.yaml',
            fieldProps: {
                listType: 'text',
                name: 'file',
                multiple: true,
                maxCount: 1,
                // showUploadList: false,
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                },
                action: BASE_URL + `/v1/workflow/import`,
                beforeUpload: file => {
                    // Prevent automatic upload
                    setFileList([file]);
                    return false;
                },
            },
            onChange(info) {
                const status = info.file.status;

                if (status === 'done') {
                    if (info?.file?.response?.code === 0) {
                        message.success(intl.formatMessage({ id: 'workflow.importSuccess' }));
                        setIsImportModalOpen(false);
                    } else {
                        message.error(intl.formatMessage({ id: 'workflow.importFailed' }));
                    }
                } else if (status === 'error') {
                    message.error(`${info.file.name} file upload failed.`);
                }
            },
        };

        const handleImportOk = () => {
      
            if (fileList.length > 0) {
                const formData = new FormData();
                formData.append('file', fileList[0]);
                importWorkflow(formData).then(res => {
                    if (res?.code == 0) {
                        history.push(`/workspace/workflow?app_id=${res?.data?.app_id}&type=false`);
                    }
                });
            }
            setIsImportModalOpen(false);
        };
        return (
            <Modal
                title={intl.formatMessage({ id: 'creation.importWorkflow' })}
                open={isImportModalOpen}
                onOk={handleImportOk}
                okButtonProps={{
                    loading: false,
                }}
                okText={intl.formatMessage({ id: 'workflow.import' })}
                onCancel={handleImportCancel}
            >
                <ProFormUploadDragger
                    // required={true}
                    // rules={[{ required: true, message: '' }]}
                    name="file"
                    {...uploadProps}
                ></ProFormUploadDragger>
            </Modal>
        );
    });
    return (
        <Card
            style={{ minWidth: 300, marginTop: 10, backgroundColor: '#EFF0F2' }}
            bodyStyle={{ height: '100%' }}
            hoverable={false}
        >
            <ImportFileDataPopup></ImportFileDataPopup>
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '194px',
                }}
            >
                {optionsModalId === 6 ? (
                    <div
                        className="flex justify-around items-start h-full w-full "
                        style={{ flexDirection: 'column', height: 'calc(100% + 24px)' }}
                    >
                        {transformData.map((item: any, i: any) => {
                            return (
                                <div
                                    className="hover:bg-[#fff] w-full rounded-lg h-8 cursor-pointer flex items-center"
                                    onClick={() => showModal(item.apps_mode)}
                                >
                                    <img
                                        src={item.icon}
                                        style={{
                                            width: '16px',
                                            height: '16px',
                                            margin: '0 5px 0 10px',
                                        }}
                                        alt=""
                                    />
                                    <div style={{ color: '#213044' }}>
                                        {intl.formatMessage({ id: 'creation.new' })}
                                        {item.name}
                                    </div>
                                </div>
                            );
                        })}
                        <div
                            onClick={() => setIsImportModalOpen(true)}
                            className="hover:bg-[#fff] w-full rounded-lg h-8 cursor-pointer flex items-center text-[#213044]"
                        >
                            <ImportOutlined className="size-4  mr-[5px] ml-[10px]" />{' '}
                            {intl.formatMessage({ id: 'creation.importWorkflow' })}
                        </div>
                    </div>
                ) :null}
                <div
                    className=" flex-wrap h-full text-[#999] text-[12px] cursor-pointer"
                    style={{ width: optionsModalId === 6 ? '50%' : '100%' }}
                    onClick={() => showModal(optionsModalId)}>
                    {optionsModalId === 6 ? (
                        <div className="mt-[62px]">
                            <div className="h-[42px] flex justify-center">
                                <img src="/icons/creation/add.svg" alt="" />
                            </div>
                            <div className="svg-container w-full text-center">
                                {' '}
                                {intl.formatMessage({ id: 'creation.addcreation' })}
                            </div>
                        </div>
                    ) : (
                        transformData
                            .filter((item: any, index: any) => {
                                return item.apps_mode == optionsModalId;
                            })
                            .map((item: any, index: any) => {
                                return (
                                    <div className="mt-[50px]">
                                        <div className="h-[42px] flex justify-center mb-[10px]">
                                            <img
                                                src={
                                                    item.unselected
                                                        ? item.unselected
                                                        : '/icons/creation/add.svg'
                                                }
                                                alt=""
                                            />
                                        </div>
                                        <div className="svg-container w-full text-center">
                                            {intl.formatMessage({ id: 'creation.new' })}
                                            {item.name
                                                ? item.name
                                                : intl.formatMessage({ id: 'creation.adhibition' })}
                                        </div>
                                    </div>
                                );
                            })
                    )}
                </div>
            </div>

            <CreationModal
                setIsModalOpen={setIsModalOpen} // Toggle modal switch
                isModalOpen={isModalOpen} // Toggle modal switch
                ModalType={showPopupTop} // Toggle button display
                CreationType={CreationType} // Card creation type { name: "Agent", path: "Agents", id: 1, }
                setcreationType={setcreationType} // Toggle card button type (optional)
                transformData={transformData} // Button switch type total type (optional)
            />
        </Card>
    );
};

export default AddCreation;
