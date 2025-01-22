import { PostappsCreate } from '@/api/creation';
import useUserStore from '@/store/user';
import { createappdata } from '@/utils/useUser';
import { useIntl } from '@umijs/max';
import { Button, Input, Modal } from 'antd';
import React, { useEffect, useState } from 'react';
import { history } from 'umi';
import Profilephoto from '../pages/Creation/components/profilephoto';
const { TextArea } = Input;

interface ChildProps {
    setIsModalOpen: any;
    isModalOpen: boolean;
    CreationType: any;
    ModalType: Boolean;
    transformData?: any;
    setcreationType?: any;
}
const CreationModal: React.FC<ChildProps> = ({
    setIsModalOpen,
    isModalOpen,
    transformData,
    CreationType,
    setcreationType,
    ModalType,
}) => {
    // const [CreationType, setcreationType] = useState({
    //     name: "Agent",
    //     path: "Agents",
    //     id: 1,
    // },)
    const intl = useIntl();
    const [CreationName, setCreationName] = useState('');
    const [DescribeValue, setDescribeValue] = useState('');
    const [PitchOnPhone, setPitchOnPhone] = useState({
        id: 1,
        icon: '/icons/headportrait/Android.svg',
    });
    const { setAgentCreateOpen,setSkillCreateOpen } = useUserStore();
    useEffect(() => {}, []);

    const IconName = (e: any) => {
        setCreationName(e.target.value);
    };

    const CreationDescribe = (e: any) => {
        setDescribeValue(e.target.value);
    };

    const handleOk = async () => {
        const data = {
            name: CreationName,
            mode: CreationType.apps_mode,
            description: DescribeValue,
            icon: JSON.stringify(PitchOnPhone.id),
            icon_background: '',
        }; /* || CreationType.apps_mode == 4 */
        if (CreationType.apps_mode == 2) {
            let res = await PostappsCreate(data);
            if (res.code === 0) {
                setIsModalOpen(false);

                Createpage(res.data.app_id);
            }
        } else {
            createappdata('SET', { ...data, type: false });
            Createpage();
        }
    };

    const RadioChange = (value: any) => {
        transformData.map((item: any) => {
            if (item.name == value.name) {
                console.log(item, 'item');
                setcreationType(item);
            }
        });
    };

    const Createpage = (app_id?: any) => {
        if (app_id) {
            history.push(`/${CreationType.path}?app_id=${app_id}&&type=false`);
        } else {
            history.push(`/${CreationType.path}?type=false`);
        }
    };

    const Footer = () => {
        return (
            <div className="flex justify-between">
                <div className="flex items-center">
                    {CreationType.apps_mode == 1 && (
                        <Button
                            onClick={() => {
                                setAgentCreateOpen(true);
                                setIsModalOpen(false);
                            }}
                        >
                            {intl.formatMessage({ id: 'agent.creation.button.ai' })}
                        </Button>
                    )}
                    {CreationType.apps_mode == 4 && (
                        <Button
                            onClick={() => {
                                setSkillCreateOpen(true);
                                setIsModalOpen(false);
                            }}
                        >
                            {intl.formatMessage({ id: 'agent.creation.button.skill.ai' })}
                        </Button>
                    )}
                </div>
                <div className="flex gap-2">
                    <Button onClick={() => setIsModalOpen(false)}>
                        {intl.formatMessage({ id: 'agent.modal.button.cancel' })}
                    </Button>
                    <Button
                        disabled={CreationName !== '' ? false : true}
                        onClick={handleOk}
                        type="primary"
                    >
                        {intl.formatMessage({ id: 'creation' })}
                    </Button>
                </div>
            </div>
        );
    };
    return (
        <Modal
            title={intl.formatMessage({ id: 'creation.addnewapp' })}
            open={isModalOpen}
            okText={intl.formatMessage({ id: 'creation' })}
            onOk={handleOk}
            onCancel={() => setIsModalOpen(false)}
            okButtonProps={{ disabled: CreationName !== '' ? false : true }}
            width={820}
            footer={<Footer />}
        >
            <div className="pb-1">
                {ModalType ? (
                    <div>
                        <div className="font-medium text-xs mb-4 mt-8">
                            {intl.formatMessage({ id: 'creation.appntype' })}
                        </div>
                        <div className="flex items-center justify-around gap-y-[24px]">
                            {/* <Radio.Group onChange={RadioChange} value={CreationType && CreationType.name}>
                                    {
                                        transformData && transformData.map((item: any) => {
                                            return (
                                                <Radio.Button key={item.id} value={item.name}>{item.name}</Radio.Button>
                                            )
                                        })
                                    }
                                </Radio.Group> */}
                            {transformData &&
                                transformData.map((item: any) => {
                                    return (
                                        <div
                                            className="w-44 h-24 rounded-lg text-center bg-[url('/images/bg.png')] bg-[length:176px_96px] cursor-pointer"
                                            style={{
                                                border:
                                                    item.apps_mode === CreationType.apps_mode
                                                        ? '1px solid #1B64F3'
                                                        : '1px solid #eeeeee',
                                            }}
                                            onClick={() => {
                                                RadioChange(item);
                                            }}
                                        >
                                            <div className="flex items-center justify-center mt-5 mb-2.5">
                                                <img
                                                    className="w-6 h-6"
                                                    src={item.signicon}
                                                    alt=""
                                                />
                                            </div>
                                            <div className="text-p[#213044] text-base font-normal">
                                                {item.name}
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    </div>
                ) : null}

                <div className=" mt-5">
                    <div className="mb-5">
                        <p className="text-xs">
                            {CreationType.apps_mode == 1
                                ? intl.formatMessage({ id: 'creation.agent' })
                                : CreationType.apps_mode == 2
                                ? intl.formatMessage({ id: 'creation.workflow' })
                                : CreationType.apps_mode == 3
                                ? intl.formatMessage({ id: 'creation.repository' })
                                : intl.formatMessage({ id: 'creation.skill' })}
                            {intl.formatMessage({ id: 'creation.appiconname' })}
                        </p>
                        <div className="flex items-center justify-around">
                            <Profilephoto CardData={PitchOnPhone} setCardData={setPitchOnPhone} />
                            <Input
                                showCount
                                maxLength={20}
                                placeholder={intl.formatMessage({
                                    id: 'creation.placeholder.appname',
                                })}
                                onChange={IconName}
                            />
                        </div>
                    </div>
                    <div className="mb-5 text-xs">
                        <p>
                            {CreationType.apps_mode == 1
                                ? intl.formatMessage({ id: 'creation.agent' })
                                : CreationType.apps_mode == 2
                                ? intl.formatMessage({ id: 'creation.workflow' })
                                : CreationType.apps_mode == 3
                                ? intl.formatMessage({ id: 'creation.repository' })
                                : intl.formatMessage({ id: 'creation.skill' })}
                            {intl.formatMessage({ id: 'creation.appdescribe' })}
                        </p>
                        <TextArea
                            showCount
                            maxLength={100}
                            rows={4}
                            placeholder={intl.formatMessage({
                                id: 'creation.placeholder.appdescribe',
                            })}
                            onChange={CreationDescribe}
                        />
                    </div>
                </div>
            </div>
        </Modal>
    );
};
export default CreationModal;
