/*
 * @LastEditors: biz
 */
import React, { FC, memo, useEffect, useState } from 'react';
import { ArrowDownOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import { Modal, message } from 'antd';
import { useIntl } from '@umijs/max';
import { throttle } from 'lodash';
import useChatroomStore from '@/store/chatroomstate';
import { useModelSelect } from '@/store/modelList';
import { useModelImageSupport } from '@/contexts/ModelImageSupportContext';
import useFileUpload from '@/hooks/useFileUpload';
import { FileUploadArea } from './FileUploadArea';
import { AbilityControls } from './AbilityControls';
import { MessageInput } from './MessageInput';
import { useChatRoomContext } from '../context/ChatRoomContext';

interface inputFieldParameters {
    messageApi?: any;
    isStop?: any;
    scrollDomRef?: any;
    upButtonDom?: any;
    abilitiesList?: any;
    agentChatRoomId?: any;
    agentList?: any;
    chatStatus?: any;
}

export const InputField: FC<inputFieldParameters> = memo(props => {
    const {
        messageApi,
        isStop,
        scrollDomRef,
        upButtonDom,
        agentList,
        abilitiesList,
        agentChatRoomId,
        chatStatus,
    } = props;
    
    // Use context for setInstruction
    const { setInstruction } = useChatRoomContext();
    
    const intl = useIntl();
    const disableInput = useChatroomStore(state => state.disableInput);
    const setDisableInput = useChatroomStore(state => state.setDisableInput);
    const setClearMemory = useChatroomStore(state => state.setClearMemory);
    const { options } = useModelSelect();
    const isImageSupportModel = agentChatRoomId ? useModelImageSupport().isImageSupportModel : () => false;
    
    const [abilityId, setAbilityId] = useState(null);
    const [userSendvalue, setUserSendvalue] = useState('');
    const [uploadFileTypes, setUploadFileTypes] = useState(
        '.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.jpeg',
    );

    const {
        uploadedFiles,
        handleUpload,
        removeFile: handleRemoveFile,
        clearFiles,
        isUploading,
    } = useFileUpload({
        maxSizeMB: 15,
        acceptedFileTypes: uploadFileTypes,
        multiple: true,
    });

    useEffect(() => {
     
        if (
            agentChatRoomId &&
            agentList?.current?.length > 0 &&
            agentList?.current[0]?.agent?.m_config_id
        ) {
            const modelConfigId = agentList?.current[0]?.agent?.m_config_id;
            const supportsImage = isImageSupportModel(modelConfigId);
            const newFileTypes = `.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv${
                supportsImage ? ',.jpg,.png,.jpeg' : ''
            }`;

       

            setUploadFileTypes(newFileTypes);
        }
    }, [agentList, options, agentList?.current?.[0]?.agent?.m_config_id, isImageSupportModel]);

    const clearContext = () => {
        const { confirm } = Modal;
        confirm({
            title: intl.formatMessage({ id: 'app.chatroom.clear.title' }),
            icon: <ExclamationCircleFilled />,
            content: intl.formatMessage({ id: 'app.chatroom.clear.tips' }),
            okText: intl.formatMessage({ id: 'app.chatroom.clear.confirm' }),
            okType: 'danger',
            cancelText: intl.formatMessage({ id: 'app.chatroom.clear.cancel' }),
            onOk() {
                setClearMemory(['TRUNCATE', '0']);
            },
        });
    };

    const sendInstructionQueue = (instructions, finalCallback) => {
        if (instructions.length === 0) {
            if (finalCallback) finalCallback();
            return;
        }

        const [currentInstruction, ...remainingInstructions] = instructions;
        setInstruction(currentInstruction);

        setTimeout(() => {
            sendInstructionQueue(remainingInstructions, finalCallback);
        }, 100);
    };

    const sendMessageUseFile = message => {
        const instructions = [];

        if (uploadedFiles?.length > 0) {
            instructions.push(['FILELIST', uploadedFiles.map(file => file.file_id)]);
        }
        const ability = abilityId || 0;
        instructions.push(['SETABILITY', ability]);
        instructions.push(['INPUT', message]);

        sendInstructionQueue(instructions, () => {
            if (uploadedFiles?.length > 0) {
                clearFiles();
            }
        });
    };

    const userSendmessage = (e: any) => {
        if (!e.shiftKey && e.target.value == '') {
            messageApi.open({
                type: 'warning',
                content: intl.formatMessage({ id: 'app.chatroom.content.input' }),
                duration: 10,
            });
            setUserSendvalue('');
            e.preventDefault();
        }
        if (!e.shiftKey && e.keyCode == 13 && e.target.value != '') {
            setDisableInput(true);
            setUserSendvalue('');
            sendMessageUseFile(e.target.value);
            e.preventDefault();
        }
    };

    const stopChatRoom = throttle(() => {
        setInstruction(['STOP', null]);
    }, 300);

    const handleFileUpload = () => {
        if (disableInput) return;
        handleUpload();
    };

    const sendMessage = (message: string) => {
        if (!message) {
            messageApi.open({
                type: 'warning',
                content: intl.formatMessage({
                    id: 'app.chatroom.content.input',
                }),
                duration: 10,
            });
            return;
        }
        setDisableInput(true);
        sendMessageUseFile(message);
        setUserSendvalue('');
    };

    return (
        <div className="max-w-[920px] w-full min-h-[60px] mt-[20px] mb-[20px] mx-auto relative">
            <div
                ref={upButtonDom}
                className="w-[40px] h-[40px] rounded-[6px]  bg-[#fff] border border-[#ddd] cursor-pointer absolute top-[-67px] left-2/4 flex items-center justify-center hidden"
                onClick={(e: any) => {
                    scrollDomRef.current.scrollTo({
                        top: 0,
                        behavior: 'smooth',
                    });
                }}
            >
                <ArrowDownOutlined className="text-[16px]" />
            </div>

            <FileUploadArea
                uploadedFiles={uploadedFiles}
                handleRemoveFile={handleRemoveFile}
            />
            
            <div
                className={`border  px-[12px] py-2 border-[#ccc] bg-[#fff]  ${
                    uploadedFiles.length > 0 ? 'rounded-b-[8px]' : 'rounded-[8px]'
                }`}
            >
                <AbilityControls
                    agentChatRoomId={agentChatRoomId}
                    abilitiesList={abilitiesList}
                    abilityId={abilityId}
                    setAbilityId={setAbilityId}
                    clearContext={clearContext}
                />
                
                <MessageInput
                    userSendvalue={userSendvalue}
                    setUserSendvalue={setUserSendvalue}
                    disableInput={disableInput}
                    isUploading={isUploading}
                    isStop={isStop}
                    userSendmessage={userSendmessage}
                    handleFileUpload={handleFileUpload}
                    sendMessage={sendMessage}
                    stopChatRoom={stopChatRoom}
                />
            </div>
        </div>
    );
}); 