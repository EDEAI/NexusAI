import { PostappsCreate } from '@/api/creation';
import { Card, Input, message, Modal } from 'antd';
import React, { memo, useEffect, useState } from 'react';
import { history } from 'umi';
import { BASE_URL } from '@/api/request';
import { importWorkflow } from '@/api/workflow';
import { ConsoleSqlOutlined, ImportOutlined, InboxOutlined } from '@ant-design/icons';
import { ProFormUploadDragger, ProFormUploadDraggerProps } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';
import { useLocation } from 'umi';
import CreationModal from '../../../../components/creationModal';
import { usePermissions } from '@/hooks/usePermissions';
import { PERMISSION_IDS } from '@/utils/permissions';
interface ChildProps {
    optionsModalId: any;
}

const AddCreation: React.FC<ChildProps> = ({ optionsModalId }) => {
    const intl = useIntl();
    const location = useLocation();
    const { hasPermission } = usePermissions();
    
    // Define permissions at component level
    const canCreateAgent = hasPermission(PERMISSION_IDS.CREATE_AGENT);
    const canCreateWorkflow = hasPermission(PERMISSION_IDS.CREATE_WORKFLOW);
    const canCreateSkill = hasPermission(PERMISSION_IDS.CREATE_SKILL);
    const canCreateKnowledgeBase = hasPermission(PERMISSION_IDS.CREATE_KNOWLEDGE_BASE);
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
        
        // If specific type is requested and user has permission, use it
        if (newtype[0]) {
            const selectedType = newtype[0];
            const hasPermissionForType = 
                (selectedType.apps_mode === 1 && canCreateAgent) ||
                (selectedType.apps_mode === 2 && canCreateWorkflow) ||
                (selectedType.apps_mode === 3 && canCreateKnowledgeBase) ||
                (selectedType.apps_mode === 4 && canCreateSkill);
            
            if (hasPermissionForType) {
                setcreationType(selectedType);
                return;
            }
        }
        
        // Find the first type user has permission for
        const availableTypes = [
            { apps_mode: 1, permission: canCreateAgent },
            { apps_mode: 2, permission: canCreateWorkflow },
            { apps_mode: 4, permission: canCreateSkill },
            { apps_mode: 3, permission: canCreateKnowledgeBase }
        ];
        
        const firstAvailableType = availableTypes.find(type => type.permission);
        
        if (firstAvailableType) {
            const typeConfig = transformData.find(option => option.apps_mode === firstAvailableType.apps_mode);
            setcreationType(typeConfig || {
                name: 'Agent',
                path: 'Agents',
                icon: '/icons/creation/agent.svg',
                pitchicon: '/icons/creation/pitchagent.svg',
                signicon: '/icons/creation/pitchagent.svg',
                apps_mode: 1,
            });
        } else {
            // Fallback to Agent if no permissions (shouldn't happen in normal flow)
            setcreationType({
                name: 'Agent',
                path: 'Agents',
                icon: '/icons/creation/agent.svg',
                pitchicon: '/icons/creation/pitchagent.svg',
                signicon: '/icons/creation/pitchagent.svg',
                apps_mode: 1,
            });
        }
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
                            // Check permission for each creation type
                            let hasPermission = false;
                            if (item.apps_mode === 1) {
                                hasPermission = canCreateAgent;
                            } else if (item.apps_mode === 2) {
                                hasPermission = canCreateWorkflow;
                            } else if (item.apps_mode === 3) {
                                hasPermission = canCreateKnowledgeBase;
                            } else if (item.apps_mode === 4) {
                                hasPermission = canCreateSkill;
                            }
                            
                            return (
                                <div
                                    key={i}
                                    className={`w-full rounded-lg h-8 flex items-center ${
                                        hasPermission 
                                            ? 'hover:bg-[#fff] cursor-pointer' 
                                            : 'cursor-not-allowed opacity-50'
                                    }`}
                                    onClick={hasPermission ? () => showModal(item.apps_mode) : undefined}
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
                                    <div style={{ color: hasPermission ? '#213044' : '#CCCCCC' }}>
                                        {intl.formatMessage({ id: 'creation.new' })}
                                        {item.name}
                                    </div>
                                </div>
                            );
                        })}
                        <div
                            onClick={canCreateWorkflow ? () => setIsImportModalOpen(true) : undefined}
                            className={`w-full rounded-lg h-8 flex items-center ${
                                canCreateWorkflow 
                                    ? 'hover:bg-[#fff] cursor-pointer text-[#213044]' 
                                    : 'cursor-not-allowed opacity-50 text-[#CCCCCC]'
                            }`}
                        >
                            <ImportOutlined className="size-4  mr-[5px] ml-[10px]" />{' '}
                            {intl.formatMessage({ id: 'creation.importWorkflow' })}
                        </div>
                    </div>
                ) :null}
                {/* Check permissions for creation buttons */}
                {(() => {
                    // Check permissions based on current route and optionsModalId
                    let hasPermission = false;
                    
                    if (location.pathname === '/knowledgebase') {
                        // For knowledge base route, only allow knowledge base creation
                        if (optionsModalId === 3) {
                            hasPermission = canCreateKnowledgeBase;
                        } else if (optionsModalId === 6) {
                            // For "All" option in knowledge base route, only check knowledge base permission
                            hasPermission = canCreateKnowledgeBase;
                        }
                    } else {
                        // For creation route, allow agent, workflow, and skill creation
                        if (optionsModalId === 1) {
                            hasPermission = canCreateAgent;
                        } else if (optionsModalId === 2) {
                            hasPermission = canCreateWorkflow;
                        } else if (optionsModalId === 4) {
                            hasPermission = canCreateSkill;
                        } else if (optionsModalId === 6) {
                            // For "All" option in creation route, check agent, workflow, and skill permissions
                            hasPermission = canCreateAgent || canCreateWorkflow || canCreateSkill;
                        }
                    }
                    
                    return (
                        <div
                            className={`flex-wrap h-full text-[12px] ${
                                hasPermission 
                                    ? 'text-[#999] cursor-pointer' 
                                    : 'text-[#CCCCCC] cursor-not-allowed opacity-50'
                            }`}
                            style={{ width: optionsModalId === 6 ? '50%' : '100%' }}
                            onClick={hasPermission ? () => showModal(optionsModalId) : undefined}>
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
                                // Filter based on current route and optionsModalId
                                if (optionsModalId === 6) {
                                    // For "All" option, filter based on current route
                                    if (location.pathname === '/knowledgebase') {
                                        // Only show knowledge base creation in knowledge base route
                                        return item.apps_mode === 3 && canCreateKnowledgeBase;
                                    } else {
                                        // Only show agent, workflow, and skill creation in creation route
                                        if (item.apps_mode === 1) return canCreateAgent;
                                        if (item.apps_mode === 2) return canCreateWorkflow;
                                        if (item.apps_mode === 4) return canCreateSkill;
                                        return false;
                                    }
                                }
                                return item.apps_mode == optionsModalId;
                            })
                            .map((item: any, index: any) => {
                                return (
                                    <div className="mt-[50px]" key={index}>
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
                    );
                })()}
            </div>

            <CreationModal
                setIsModalOpen={setIsModalOpen} // Toggle modal switch
                isModalOpen={isModalOpen} // Toggle modal switch
                ModalType={location.pathname!='/knowledgebase'} // Toggle button display
                CreationType={CreationType} // Card creation type { name: "Agent", path: "Agents", id: 1, }
                setcreationType={setcreationType} // Toggle card button type (optional)
                transformData={transformData} // Button switch type total type (optional)
            />
        </Card>
    );
};

export default AddCreation;
