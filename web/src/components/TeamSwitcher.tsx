import React, { useState, useCallback } from 'react';
import { useIntl } from '@umijs/max';
import { Modal, Select, Button, Space, Tag, Typography } from 'antd';
import { DownOutlined } from '@ant-design/icons';

const { Text } = Typography;
const { Option } = Select;

interface Team {
  id: string;
  name: string;
  role: number;
  roleName: string;
  position: string;
  memberCount: number;
}

interface TeamSwitcherProps {
  currentTeam: Team | null;
  teams: Team[];
  onTeamChange: (team: Team) => void;
  loading?: boolean;
}

const TeamSwitcher: React.FC<TeamSwitcherProps> = ({
  currentTeam,
  teams,
  onTeamChange,
  loading
}) => {
  const intl = useIntl();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(currentTeam);

  const handleOpenModal = useCallback(() => {
    setIsModalOpen(true);
    setSelectedTeam(currentTeam);
  }, [currentTeam]);

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
  }, []);

  const handleTeamChange = useCallback(() => {
    if (selectedTeam) {
      onTeamChange(selectedTeam);
      setIsModalOpen(false);
    }
  }, [selectedTeam, onTeamChange]);

  const handleSelectChange = useCallback((teamId: string) => {
    const team = teams.find(t => t.id === teamId);
    if (team) {
      setSelectedTeam(team);
    }
  }, [teams]);

  if (loading) {
    return (
      <div className="w-64 h-8 bg-gray-100 rounded animate-pulse" />
    );
  }

  if (!currentTeam || teams.length === 0) {
    return (
      <div className="h-8 flex items-center text-gray-500 text-sm">
        {intl.formatMessage({ id: 'component.team.noTeams' })}
      </div>
    );
  }

  return (
    <div>
      <Button 
        type="text" 
        size="small" 
        onClick={handleOpenModal}
        className="flex items-center gap-1 px-2 py-1 hover:bg-gray-100 rounded transition-colors cursor-pointer group"
      >
        <Text className="text-gray-800 text-sm truncate max-w-[180px] group-hover:text-blue-600 transition-colors font-medium" title={intl.formatMessage({ id: 'component.team.currentTeam' }, { name: currentTeam.name })}>
           {intl.formatMessage({ id: 'component.team.currentTeam' }, { name: currentTeam.name })}
          </Text>
        <DownOutlined className="text-gray-600 text-xs group-hover:text-blue-600 transition-colors" />
      </Button>

      <Modal
        title={intl.formatMessage({ id: 'component.team.switchTeam' })}
        open={isModalOpen}
        onCancel={handleCloseModal}
        footer={[
          <Button key="cancel" onClick={handleCloseModal}>
            {intl.formatMessage({ id: 'component.team.cancel' })}
          </Button>,
          <Button 
            key="switch" 
            type="primary" 
            onClick={handleTeamChange}
            disabled={!selectedTeam || !currentTeam || selectedTeam.id === currentTeam.id}
          >
            {intl.formatMessage({ id: 'component.team.switchTeam' })}
          </Button>
        ]}
      >
        <div className="mb-4">
          <Text>{intl.formatMessage({ id: 'component.team.currentTeamLabel' })}</Text>
          <Tag color="blue" className="ml-2">
            {currentTeam.name}
          </Tag>
        </div>
        
        <div className="mb-4">
          <Text>{intl.formatMessage({ id: 'component.team.selectTeamToSwitch' })}</Text>
          <Select
            value={selectedTeam?.id}
            onChange={handleSelectChange}
            style={{ width: '100%', marginTop: 8 }}
            placeholder={intl.formatMessage({ id: 'component.team.selectTeam' })}
          >
            {teams.map(team => (
              <Option key={team.id} value={team.id}>
                <Space>
                  <span>{team.name}</span>
                  {team.position && (
                    <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium">
                      {team.position}
                    </span>
                  )}
                  <Tag color={team.role === 1 ? 'green' : 'default'}>
                    {team.role === 1 ? intl.formatMessage({ id: 'user.teamAdmin' }) : team.roleName}
                  </Tag>
                  <Text type="secondary">({intl.formatMessage({ id: 'component.team.memberCount' }, { count: team.memberCount })})</Text>
                </Space>
              </Option>
            ))}
          </Select>
        </div>
        
        {selectedTeam && currentTeam && selectedTeam.id !== currentTeam.id && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded">
            <Text type="secondary">
              {selectedTeam.position 
                ? intl.formatMessage({ id: 'component.team.switchConfirmWithPosition' }, { 
                    name: selectedTeam.name, 
                    position: selectedTeam.position,
                    role: selectedTeam.role === 1 ? intl.formatMessage({ id: 'user.teamAdmin' }) : selectedTeam.roleName
                  })
                : intl.formatMessage({ id: 'component.team.switchConfirmWithoutPosition' }, { 
                    name: selectedTeam.name, 
                    role: selectedTeam.role === 1 ? intl.formatMessage({ id: 'user.teamAdmin' }) : selectedTeam.roleName
                  })
              }
            </Text>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TeamSwitcher;