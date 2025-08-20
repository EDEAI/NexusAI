import aniRequest from './request';
import { getRolesList, RoleListResponse } from './index';

// Get team list
export const getTeamList = async (params?: { keyword?: string }) => {
    return await aniRequest<any>(`/v1/auth/team_member_list`, { 
        method: 'GET', 
        data: params?.keyword ? { keyword: params.keyword } : {} 
    });
};

// Generate invitation link
export const postInviteUser = async (data: any) => {
    return await aniRequest<any>(`/v1/auth/invite_user`, { method: 'POST', data: data });
};

// Register invited user account
export const postRegisterUser = async (data: any) => {
    return await aniRequest<any>(`/v1/auth/register_user`, { method: 'POST', data: data });
};

// Get role list
export const getRoleList = async (): Promise<RoleListResponse> => {
    return await getRolesList({ status: 2 });
};

// Get user teams list
export const getUserTeams = async () => {
    return await aniRequest<any>(`/v1/auth/user_teams`, { method: 'GET', data: { platform: 1 } });
};

// Switch user team
export const switchUserTeam = async (teamId: number) => {
    return await aniRequest<any>(`/v1/auth/switch_team`, { method: 'POST', data: { team_id: teamId } });
};