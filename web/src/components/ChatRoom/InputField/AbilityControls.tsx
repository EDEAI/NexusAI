/*
 * @LastEditors: biz
 */
import React, { FC } from 'react';
import { ClearOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { ProFormSelect } from '@ant-design/pro-components';
import { useIntl } from '@umijs/max';

interface AbilityControlsProps {
    agentChatRoomId?: any;
    abilitiesList?: any[];
    abilityId: any;
    setAbilityId: (value: any) => void;
    clearContext: () => void;
}

export const AbilityControls: FC<AbilityControlsProps> = props => {
    const { agentChatRoomId, abilitiesList, abilityId, setAbilityId, clearContext } = props;
    const intl = useIntl();

    if (!agentChatRoomId) {
        return null;
    }

    return (
        <div className="flex flex-wrap gap-2 items-center mb-2">
            {abilitiesList?.length > 0 && (
                <ProFormSelect
                    label={intl.formatMessage({ id: 'agent.selectivepower' })}
                    name="ability_id"
                    options={abilitiesList}
                    initialValue={abilityId}
                    fieldProps={{
                        placeholder: intl.formatMessage({
                            id: 'agent.pleaseselect',
                        }),
                        allowClear: false,
                        size: 'small',
                        onChange: (value: any) => {
                            setAbilityId(value);
                        },
                    }}
                    formItemProps={{
                        className: 'm-0',
                    }}
                />
            )}

            <Button
                size="small"
                color="danger"
                variant="outlined"
                onClick={clearContext}
                icon={<ClearOutlined />}
            >
                {intl.formatMessage({ id: 'app.chatroom.sidebar.agent_button' })}
            </Button>
        </div>
    );
}; 