export interface AgentSkill {
    skill: string;
    description: string;
    output_format: 'json' | string;
}

export interface AgentFormData {
    name: string;
    description: string;
    prompt: string;
    skill_list: AgentSkill[];
}

export interface BatchCreateFormData {
    count: number;
    prompts: string;
    additionalPrompt?: string;
} 