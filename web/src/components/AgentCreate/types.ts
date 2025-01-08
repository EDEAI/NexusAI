/*
 * @LastEditors: biz
 */
export interface AgentSkill {
    skill: string;
    description: string;
    output_format: 'json' | string;
}

export interface AgentFormData {
    name: string;
    description: string;
    prompt?: string;
    obligations: string;
    abilities: Array<{
        name: string;
        content: string;
        output_format: number;
    }>;
    skill_list?: AgentSkill[];
    tags?: string[];
}

export interface BatchCreateFormData {
    count: number;
    prompts: string;
    additionalPrompt?: string;
}

interface AgentOutput {
    name: string;
    description: string;
    obligations: string;
    abilities: Array<{
        name: string;
        content: string;
        output_format: number;
    }>;
}

interface ExecData {
    exec_id: number;
    status: number;
    error: string;
    outputs: {
        name: string;
        type: string;
        value: AgentOutput;
        max_length: number;
    };
    elapsed_time: number;
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
}

export interface AgentResult {
    app_run_id: number;
    status: number;
    error: string;
    elapsed_time: number;
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    created_time: string;
    finished_time: string;
    exec_data: ExecData;
} 