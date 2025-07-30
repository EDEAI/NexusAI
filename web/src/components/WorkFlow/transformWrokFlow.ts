import { Edge } from '@/py2js/edges.js';
import AgentNode from '@/py2js/nodes/agent.js';
import { Nodes } from '@/py2js/nodes/base.js';
import {
    ConditionBranchNode,
    LogicBranch,
    LogicBranches,
    LogicCondition,
} from '@/py2js/nodes/condition_branch.js';
import CustomCodeNode from '@/py2js/nodes/custom_code.js';
import EndNode from '@/py2js/nodes/end.js';
import HttpRequest from '@/py2js/nodes/http_request.js';
import HumanNode from '@/py2js/nodes/human.js';
import LLMNode from '@/py2js/nodes/llm.js';
import RecursiveTaskExecutionNode from '@/py2js/nodes/recursive_task_execution.js';
import RecursiveTaskGenerationNode from '@/py2js/nodes/recursive_task_generation.js';
import {
    RequirementCategory,
    RequirementCategoryNode,
} from '@/py2js/nodes/requirement_category.js';
import RetrieverNode from '@/py2js/nodes/retriever.js';
import SkillNode from '@/py2js/nodes/skill.js';
import StartNode from '@/py2js/nodes/start.js';
import TemplateConversionNode from '@/py2js/nodes/template_conversion.js';
import ToolNode from '@/py2js/nodes/tool.js';
import VariableAggregationNode from '@/py2js/nodes/variable_aggregation.js';
import { Prompt } from '@/py2js/prompt.js';
import { ObjectVariable, Variable, createVariableFromObject } from '@/py2js/variables.js';
import _, { cloneDeep } from 'lodash';
import useStore from './store';
import { AppNode, BlockEnum } from './types';

export function parseText(
    text: string,
): { identifier: string; ioType: string; fieldName: string }[] {
    const pattern = /<<([0-9a-fA-F\-]+)\.(inputs|outputs)\.([^>]+)>>/g;
    const results: { identifier: string; ioType: string; fieldName: string }[] = [];

    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
        const identifier = match[1];
        const ioType = match[2];
        const fieldName = match[3];
        results.push({ identifier, ioType, fieldName });
    }

    return results;
}

interface OriNode {
    title: string;
    desc: string;
    // position: { x: number; y: number };
    original_node_id: string;
}
function transformOrigData(node: AppNode): OriNode {
    return {
        title: node.data['title'] || '',
        desc: node.data['desc'] || '',
        // position: node.position,
        original_node_id: node.id || null,
    };
}

const serialize = nodes => {
    if (!Array.isArray(nodes)) {
        return nodes;
    }
    return nodes
        .map(node => {
            if (node.type === 'mention') {
                return node.id;
            } else if (node.children) {
                return serialize(node.children);
            } else {
                return node.text;
            }
        })
        .join('');
};

export const getVarFromData = (node, findKey) => {
    return Object.entries(node.data)
        .filter(([key, value]) => key.includes(findKey))
        .map(([key, value]) => {
            const keySplit = key.split('.');
            return {
                key: keySplit[1],
                output: keySplit[1] == 'output' && keySplit.length == 3 ? keySplit[2] : '',
                value: value,
            };
        });
};

const getDefaultModelId = () => {
    return useStore?.getState()?.modelOptionsData?.defaultValue;
};
export const transformer = {
    [BlockEnum.Start]: {
        handle(node) {
            console.log(node);

            const params = {
                ...transformOrigData(node),
                input: node.data['variables']?.free || {},
                output: node.data['output'] || {},
                import_to_knowledge_base: {
                    input: node.data['import_to_knowledge_base'] || false,
                    output: node.data['import_to_knowledge_base'] || false,
                },
                knowledge_base_mapping: {
                    input: {},
                    output: {},
                },
                requires_upload: node.data['requires_upload'] || false,
            };

            if (node.data['variables']?.value?.length) {
                node.data['variables'].value.forEach(x => {
                    if (node.data[`import_to_knowledge_base.${x.name}`]) {
                        params.knowledge_base_mapping.input[x.name] =
                            node.data[`import_to_knowledge_base.${x.name}`];
                        params.knowledge_base_mapping.output[x.name] =
                            node.data[`import_to_knowledge_base.${x.name}`];
                    }
                });
            }

            return new StartNode(params);
        },
        variables(data) {
            return data?.variables?.free?.properties || {};
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
    },
    [BlockEnum.LLM]: {
        handle(node) {
            const params = {
                ...transformOrigData(node),
                input: new ObjectVariable('input'),
                model_config_id: node.data['model_config_id'] || getDefaultModelId(),
                requires_upload: node.data['requires_upload'] || false,
                retrieval_task_datasets: node.data['retrieval_task_datasets'] || [],
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
                task_splitting: node.data['task_splitting'] || false,
                manual_confirmation: node.data['manual_confirmation'] || false,
                import_to_knowledge_base: {
                    input: node.data['import_to_knowledge_base'] || false,
                    output: node.data['import_to_knowledge_base'] || false,
                },
                knowledge_base_mapping: {
                    input: {},
                    output: {},
                },
                prompt: {},
            };

            getDefaultModelId();
            getVarFromData(node, 'import_to_knowledge_base.')?.forEach(({ key, value, output }) => {
                if (!value) return;
                if (output) {
                    params.knowledge_base_mapping.output[output] = value as number;
                    return;
                }
                params.knowledge_base_mapping.input[key] = value as number;
            });

            let system = '';
            let user = '';
            if (node?.data?.systemEditor) {
                system = serialize(node.data.systemEditor);
            }
            if (node?.data?.userEditor) {
                user = serialize(node.data.userEditor);
            }
            params.prompt = new Prompt(system, user, '');

            return new LLMNode(params);
        },
        context(freeNode) {
            const prompt = freeNode.data.prompt;
            let context = [];
            Object.values(prompt).forEach((x: object) => {
                if (!x?.value) return;
                const getVar = parseText(x.value);
                context = [...context, ...getVar];
            });
            return {
                context: _.uniqWith(
                    context,
                    (a, b) => a.identifier === b.identifier && a.fieldName === b.fieldName,
                ),
            };
        },
    },
    [BlockEnum.Agent]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: node.data['input'] || null,
                agent_id: node.data?.baseData?.agent_id || 0,
                ability_id: node.data['ability_id'] || 0,
                prompt: node.data['prompt'] || null,
                // requires_upload: node.data['requires_upload'] || false,
                retrieval_task_datasets: node.data['retrieval_task_datasets'] || [],
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
                task_splitting: node.data['task_splitting'] || false,
                manual_confirmation: node.data['manual_confirmation'] || false,
                import_to_knowledge_base: {
                    input: node.data['import_to_knowledge_base'] || false,
                    output: node.data['import_to_knowledge_base'] || false,
                },
                knowledge_base_mapping: {
                    input: {},
                    output: {},
                },
                flow_data: node.data['flow_data'] || {},
            };

            const getNodeVars = useStore.getState().getOutputVariables(node.id);

            const baseInput = node?.data?.infoData?.agent?.input_variables;

            const input = baseInput
                ? createVariableFromObject(baseInput)
                : new ObjectVariable('input');
            if (baseInput) {
                const properties = baseInput?.properties;
                Object.values(properties).forEach(value => {
                    const findVar = getVarFromData(node, 'variable.')?.find(
                        x => x.key == value.name,
                    );
                    if (findVar) {
                        console.log(findVar);

                        const type = getNodeVars.find(x => x.value == findVar.value)?.createVar
                            ?.type;
                        const variable = new Variable(
                            value.name,
                            type || 'string',
                            findVar?.value || '',
                        );
                        input.addProperty(value.name, variable);
                    } else {
                        input.addProperty(
                            value.name,
                            new Variable(value.name, value.type, value.value),
                        );
                    }
                });
            }
            // getVarFromData(node, 'variable.')?.forEach(({ key, value }) => {
            //     const type = getNodeVars.find((x) => x.value == value)?.createVar?.type;
            //     const variable = new Variable(key, type || 'string', value);
            //     input.addProperty(key, variable);
            // });
            params.input = input;

            params.ability_id = params.ability_id * 1;
            getVarFromData(node, 'import_to_knowledge_base.')?.forEach(({ key, value, output }) => {
                if (!value) return;
                if (output) {
                    params.knowledge_base_mapping.output[output] = value as number;
                    return;
                }
                params.knowledge_base_mapping.input[key] = value as number;
            });

            let system = '';
            let user = '';
            if (node?.data?.systemEditor) {
                system = serialize(node.data.systemEditor);
            }
            if (node?.data?.userEditor) {
                user = serialize(node.data.userEditor);
            }
            params.prompt = new Prompt(system, user, '');

            return new AgentNode(params);
        },
        context(freeNode) {
            const prompt = freeNode.data.prompt;
            let context = [];

            Object.values(prompt).forEach((x: object) => {
                if (!x?.value) return;
                const getVar = parseText(x.value);
                context = [...context, ...getVar];
            });
            return {
                inputs: freeNode.data.input,
                context: _.uniqWith(
                    context,
                    (a, b) => a.identifier === b.identifier && a.fieldName === b.fieldName,
                ),
            };
        },
    },
    [BlockEnum.HttpRequest]: {
        handle(node) {
            console.log(node);
            const input = new ObjectVariable('input');

            const method = new Variable('method', 'string', node.data['method']);
            input.addProperty('method', method);
            const url = new Variable('url', 'string', node.data['url']);
            input.addProperty('url', url);
            const getNodeVars = useStore.getState().getOutputVariables(node.id);
            const processItems = (items, name) => {
                const objVar = new ObjectVariable(name);
                if (items) {
                    items.forEach(item => {
                        const key = item.key.content || '';
                        const value = serialize(item.value.content);
                        const createVar = getNodeVars.find(x => x.value == value)?.createVar;
                        const variable = new Variable(key, createVar?.type || 'string', value);
                        objVar.addProperty(key, variable);
                    });
                }
                input.addProperty(name, objVar);
            };

            // const headers=new ObjectVariable('headers')
            // if(node.data['headers']){
            //     node.data['headers'].forEach((item) => {
            //         const key=item.key.content||'';
            //         const value=serialize(item.value.content)
            //         const vars=new Variable(key,'string',value)
            //         headers.addProperty(key,vars)
            //     });
            // }
            // input.addProperty('headers',headers)

            // const params=new ObjectVariable('params')
            // if(node.data['params']){
            //     node.data['params'].forEach((item) => {
            //         const key=item.key.content||'';
            //         const value=serialize(item.value.content)
            //         const vars=new Variable(key,'string',value)
            //         headers.addProperty(key,vars)
            //     });
            // }
            // input.addProperty('params',params)
            processItems(node.data['headers'], 'headers');
            processItems(node.data['params'], 'params');

            const bodyType = node.data['body_type'] || 'none';
            const body_type = new Variable('body_type', 'string', bodyType);
            input.addProperty('body_type', body_type);

            if (['form-data', 'x-www-form-urlencoded'].includes(bodyType)) {
                processItems(node.data['body_data'], 'body_data');
            } else if (['raw text', 'json'].includes(bodyType)) {
                const body = new Variable(
                    'body_data',
                    'string',
                    serialize(node.data['editor'] || []),
                );
                input.addProperty('body_data', body);
            }

            if (node.data['connect_timeout']) {
                const connect_timeout = new Variable(
                    'connect_timeout',
                    'number',
                    node.data['connect_timeout'],
                );
                input.addProperty('connect_timeout', connect_timeout);
            }
            if (node.data['read_timeout']) {
                const read_timeout = new Variable(
                    'read_timeout',
                    'number',
                    node.data['read_timeout'],
                );
                input.addProperty('read_timeout', read_timeout);
            }
            if (node.data['write_timeout']) {
                const write_timeout = new Variable(
                    'write_timeout',
                    'number',
                    node.data['write_timeout'],
                );
                input.addProperty('write_timeout', write_timeout);
            }

            console.log(input, input.toObject());

            const nodeParams = {
                title: node.data['title'] || '',
                desc: node.data['desc'] || '',
                input: input,
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
                manual_confirmation: node.data['manual_confirmation'] || false,
                flow_data: node.data['flow_data'] || {},
                original_node_id: node.id || null,
            };
            return new HttpRequest(nodeParams);
        },

        context(freeNode) {
            const prompt = freeNode.data.input;
            let context = [];
            Object.values(prompt.properties).forEach((x: object) => {
                if (x.properties) {
                    Object.values(x.properties).forEach((y: object) => {
                        const getVar = parseText(y.value);
                        context = [...context, ...getVar];
                    });
                }
                if (x.value) {
                    const getVar = parseText(x.value);
                    context = [...context, ...getVar];
                }
            });

            return {
                // inputs: freeNode.data.input,
                context: _.uniqWith(
                    context,
                    (a, b) => a.identifier === b.identifier && a.fieldName === b.fieldName,
                ),
            };
        },
    },

    [BlockEnum.Human]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: node.data['variables']?.free || new ObjectVariable('input'),
                output: node.data['variables']?.free || {},
                requires_upload: node.data['requires_upload'] || false,
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
                manual_confirmation: true,
                import_to_knowledge_base: {
                    input: node.data['import_to_knowledge_base'] || false,
                    output: node.data['import_to_knowledge_base'] || false,
                },
                knowledge_base_mapping: {
                    input: {},
                    output: {},
                },
            };
            if (node.data['variables']?.value?.length) {
                node.data['variables'].value.forEach(x => {
                    if (node.data[`import_to_knowledge_base.${x.name}`]) {
                        params.knowledge_base_mapping.input[x.name] =
                            node.data[`import_to_knowledge_base.${x.name}`];
                    }
                });
            }

            // const input=new ObjectVariable('input')

            return new HumanNode(params);
        },
        variables(data) {
            return data?.variables?.free?.properties || {};
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
    },

    [BlockEnum.CustomCode]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: {},
                code_dependencies: {
                    python3: node.data['code_dependencies'] || [],
                },
                custom_code: {
                    python3:
                        node.data['code'] ||
                        `def main(arg1: int) -> dict:
    return {
        "result": (arg1 + 2) * 3,
    }`,
                },
                output: {},
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
                manual_confirmation: node.data['manual_confirmation'] || false,
            };
            const input = new ObjectVariable('input');
            if (node.data?.input_variables?.length) {
                const getNodeVars = useStore.getState().getOutputVariables(node.id);
                node.data.input_variables.forEach(x => {
                    if (x.name && x.veriable) {
                        const createVar = getNodeVars.find(
                            item => item.value == x.veriable,
                        )?.createVar;
                        const vars = new Variable(x.name, createVar?.type || 'string', x.veriable);
                        input.addProperty(x.name, vars);
                    }
                });
            }
            params.input = input;

            const output = new ObjectVariable('output');
            if (node.data?.output_variables?.length) {
                node.data.output_variables.forEach(x => {
                    if (x.name && x.veriable) {
                        const vars = new Variable(x.name, x.veriable || 'string', null);
                        output.addProperty(x.name, vars);
                    }
                });
            }
            params.output = output;
            return new CustomCodeNode(params);
        },
        variables(data) {
            const output = new ObjectVariable('output');
            if (data?.output_variables?.length) {
                data.output_variables.forEach(x => {
                    if (x.name && x.veriable) {
                        const vars = new Variable(x.name, x.veriable || 'string', null);
                        output.addProperty(x.name, vars);
                    }
                });
            }
            return output?.properties || {};
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
    },

    [BlockEnum.Retriever]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: node.data['variable'] || new Variable('input', 'string', ''),
                datasets: node.data['datasets'] || [],
                manual_confirmation: node.data['manual_confirmation'] || false,
            };
            if (node.data['variable']) {
                // const getNodeVars = useStore.getState().getOutputVariables(node.id);
                // const type = getNodeVars.find((x) => x.value == node.data['variable'])?.createVar
                //     ?.type;
                params.input = new Variable('input', 'string', node.data['variable']);
            }
            console.log('params', params);
            return new RetrieverNode(params);
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
    },

    [BlockEnum.VariableAggregation]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: {},
            };
            const input = new ObjectVariable('input');
            if (node.data?.variables_list?.length) {
                const getNodeVars = useStore.getState().getOutputVariables(node.id);
                node.data.variables_list.forEach(item => {
                    const createVar = getNodeVars.find(x => x.value == item)?.createVar;
                    const vars = new Variable(
                        createVar?.name || '',
                        createVar?.type || 'string',
                        item,
                    );
                    input.addProperty(item, vars);
                });
            }
            // if (node.data?.variables?.length) {
            //     const getNodeVars = useStore.getState().getOutputVariables(node.id);
            //     node.data.variables.forEach((item) => {
            //         const createVar = getNodeVars.find((x) => x.value == item.variable)?.createVar;
            //         const vars = new Variable(
            //             createVar.name,
            //             createVar?.type || 'string',
            //             item.variable,
            //         );
            //         input.addProperty(createVar.name, vars);
            //     });
            // }
            params.input = input;
            return new VariableAggregationNode(params);
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
    },

    [BlockEnum.RequirementCategory]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: new Variable('input', 'string', node.data['variable'] || ''),
                model_config_id: node.data['model'] || getDefaultModelId(),
                manual_confirmation: node.data['manual_confirmation'] || false,
                requirement_category: null,
                prompt: new Prompt(node.data.prompt, '', ''),
            };
            const requirementCategory = new RequirementCategory();
            if (node.data['wrap_list']?.length) {
                node.data['wrap_list'].forEach((x, i) => {
                    requirementCategory.addCategory(x.que, `${node.id}-${i}`);
                });
            }
            if (node.data['variable']) {
                // const type = useStore
                //     .getState()
                //     .getOutputVariables(node.id)
                //     .find((x) => x.value == node.data['variable'])?.createVar;
                params.input = new Variable('input', 'string', node.data['variable']);
            }
            params.requirement_category = requirementCategory;

            return new RequirementCategoryNode(params);
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
    },

    [BlockEnum.TemplateConversion]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: new Variable('input', 'string', node.data['variable']),
                custom_code: {
                    jinja2: node.data['code'] || '',
                },
                manual_confirmation: node.data['manual_confirmation'] || false,
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
            };

            const input = new ObjectVariable('input');
            if (node.data?.input_variables?.length) {
                const getNodeVars = useStore.getState().getOutputVariables(node.id);
                node.data.input_variables.forEach(x => {
                    if (x.name && x.variable) {
                        const createVar = getNodeVars.find(
                            item => item.value == x.variable,
                        )?.createVar;
                        const vars = new Variable(x.name, createVar?.type || 'string', x.variable);
                        input.addProperty(x.name, vars);
                    }
                });
            }
            params.input = input;

            return new TemplateConversionNode(params);
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
    },
    [BlockEnum.Skill]: {
        handle(node) {
            const params = {
                ...transformOrigData(node),
                input: new Variable('input', 'string', node.data['variable']),
                output: {},
                custom_code: {
                    python3: node.data['code'] || '',
                },
                skill_id: node?.data?.baseData?.skill_id || 0,
                manual_confirmation: node.data['manual_confirmation'] || false,
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
            };

            // const getNodeVars = useStore.getState().getOutputVariables(node.id);

            // const input = new ObjectVariable('input');
            // getVarFromData(node, 'variable.')?.forEach(({ key, value }) => {
            //     const type = getNodeVars.find((x) => x.value == value)?.createVar?.type;
            //     const variable = new Variable(key, type || 'string', value);
            //     input.addProperty(key, variable);
            // });
            const input = node?.data?.infoData?.input_variables || new ObjectVariable('input');
            getVarFromData(node, 'variable.')?.forEach(({ key, value }) => {
                if (input.properties[key]) {
                    input.properties[key].value = value;
                }
            });
            params.input = input;
            if (node?.data?.infoData?.output_variables) {
                params.output = node?.data?.infoData?.output_variables;
            }
            // console.log(params, new SkillNode(params), node?.data?.infoData?.input_variables);

            return new SkillNode(params);
        },
        context(freeNode) {
            return {
                inputs: freeNode.data.input,
            };
        },
        variables(data) {
            // const output = new ObjectVariable('output');
            // if (data?.infoData?.output_variables?.length) {
            //     data.infoData.output_variables
            // }

            return data?.infoData?.output_variables?.properties || {};
        },
    },
    [BlockEnum.ConditionBranch]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                wait_for_all_predecessors: true,
                // manual_confirmation: node.data['manual_confirmation'] || false,
                logic_branches: {},
            };
            const logic_branches = new LogicBranches();

            if (node.data?.count?.length) {
                const getNodeVars = useStore.getState().getOutputVariables(node.id);
                node.data.count.forEach(x => {
                    if (x.labels?.length) {
                        const logic_branch = new LogicBranch(x.type ? 'and' : 'or');
                        x.labels.forEach(y => {
                            const createVar = getNodeVars.find(
                                x => x.value == y.variable,
                            )?.createVar;
                            console.log(createVar);
                            if (!createVar) return;
                            const variable = new Variable(
                                y.variable,
                                createVar?.type || 'string',
                                y.variable,
                            );
                            const condition = new LogicCondition(variable, y.count, y.target);
                            logic_branch.addCondition(condition);
                        });
                        logic_branches.addBranch(logic_branch);
                    }
                });
            }
            params.logic_branches = logic_branches;
            const obj = new ConditionBranchNode(params);
            return obj;
        },
        context(freeNode) {
            let context = [];
            freeNode.data.logic_branches.branches.forEach(element => {
                if (!element.conditions) return;
                element.conditions.forEach(e => {
                    if (!e.variable.name) return;
                    context = [...context, ...parseText(e.variable.name)];
                });
            });
            return {
                context: _.uniqWith(
                    context,
                    (a, b) => a.identifier === b.identifier && a.fieldName === b.fieldName,
                ),
            };
        },
    },
    [BlockEnum.TaskGeneration]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: new Variable('input', 'string', node.data['variable'] || ''),
                model_config_id: node.data['model'] || getDefaultModelId(),
                manual_confirmation: node.data['manual_confirmation'] || false,
                split_task_by_line: node.data['split_task_by_line'] || false,
                // category_purpose: node.data['category_purpose'] || 0,
                requirement_category: null,
                requires_upload: false,
                prompt: new Prompt(node.data.prompt, '', ''),
                import_to_knowledge_base: {
                    input: node.data['import_to_knowledge_base'] || false,
                    output: node.data['import_to_knowledge_base'] || false,
                },
                knowledge_base_mapping: {
                    input: {},
                    output: {},
                },
            };
            
            // params.category_purpose=parseInt(params.category_purpose)
            getVarFromData(node, 'import_to_knowledge_base.')?.forEach(({ key, value, output }) => {
                if (!value) return;
                if (output) {
                    params.knowledge_base_mapping.output[output] = value as number;
                    return;
                }
                params.knowledge_base_mapping.input[key] = value as number;
            });

            if (node.data['variable']) {
                // const type = useStore
                //     .getState()
                //     .getOutputVariables(node.id)
                //     .find((x) => x.value == node.data['variable'])?.createVar;
                params.input = new Variable('input', 'string', node.data['variable']);
            }

            return new RecursiveTaskGenerationNode(params);
        },
        context(freeNode) {
            console.log(freeNode);

            return {
                inputs: freeNode.data.input,
            };
        },
    },
    [BlockEnum.TaskExecution]: {
        handle(node) {
            console.log(node);

            const params = {
                ...transformOrigData(node),
                input: new Variable('input', 'string', node.data['variable'] || ''),
                model_config_id: node.data['model'] || getDefaultModelId(),
                manual_confirmation: node.data['manual_confirmation'] || false,
                // category_purpose: node.data['category_purpose'] || '',
                requirement_category: null,
                requires_upload: false,
                prompt: new Prompt(node.data.prompt, '', ''),
                import_to_knowledge_base: {
                    input: node.data['import_to_knowledge_base'] || false,
                    output: node.data['import_to_knowledge_base'] || false,
                },
                knowledge_base_mapping: {
                    input: {},
                    output: {},
                },
                executor_list: [],
            };
            getVarFromData(node, 'import_to_knowledge_base.')?.forEach(({ key, value, output }) => {
                if (!value) return;
                if (output) {
                    params.knowledge_base_mapping.output[output] = value as number;
                    return;
                }
                params.knowledge_base_mapping.input[key] = value as number;
            });

            if (node.data['variable']) {
                // const type = useStore
                //     .getState()
                //     .getOutputVariables(node.id)
                //     .find((x) => x.value == node.data['variable'])?.createVar;
                params.input = new Variable('input', 'string', node.data['variable']);
            }
            const freeNodes = new Nodes();
            node.data['executor_list']?.forEach(x => {
                const item = _.cloneDeep(x);
                const handle = transformer[item.type]?.handle;
                item.id = item.currentId;
                freeNodes.addNode(handle(item));
            });
            params.executor_list = freeNodes.toObject();
            return new RecursiveTaskExecutionNode(params);
        },
        context(freeNode) {
            console.log(freeNode);

            return {
                inputs: freeNode.data.input,
            };
        },
    },
    [BlockEnum.Tool]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                input: new Variable('input', 'string', node.data['variable']),
                tool: {},
                manual_confirmation: node.data['manual_confirmation'] || false,
                wait_for_all_predecessors: node.data['wait_for_all_predecessors'] || false,
            };

            const paramseters = node.data?.baseData?.parameters;
            const input = new ObjectVariable('input');
            if (paramseters) {
                paramseters.forEach(x => {
                    console.log(x, node);

                    let value = '';
                    if (node?.data?.form?.[x.name]) {
                        // debugger
                        value = serialize(node?.data?.form?.[x.name]);
                    } else if (x.default) {
                        value = x.default;
                    }
                    const vars = new Variable(
                        x.name,
                        x.type || 'string',
                        value,
                        x.label.zh_Hans,
                        x.required,
                    );

                    input.addProperty(x.name, vars);
                });
            }
            params.input = input;
            params.tool = {
                provider: node.data?.baseData?.groupName,
                tool_name: node.data?.baseData?.identity?.name,
            };
            
            params.output = node.data?.baseData?.output
            return new ToolNode(params);
        },
        context1(freeNode) {
            console.log(freeNode);
            debugger;
            const input = cloneDeep(freeNode.data.input);
            Object.values(input.properties).forEach(x => {
                if (!x.required) {
                    delete input.properties[x.name];
                }
            });
            return {
                inputs: input,
            };
        },
        variables(data) {
            // const output = new ObjectVariable('output');
            // if (data?.infoData?.output_variables?.length) {
            //     data.infoData.output_variables
            // }

            return data?.outputInfo?.properties || {};
        },
        context(freeNode) {
            const prompt = freeNode.data.input.properties;
            let context = [];

            Object.values(prompt).forEach((x: object) => {
                if (!x?.value) return;
                const getVar = parseText(x.value);
                context = [...context, ...getVar];
            });
            return {
                // inputs: freeNode.data.input,
                context: _.uniqWith(
                    context,
                    (a, b) => a.identifier === b.identifier && a.fieldName === b.fieldName,
                ),
            };
        },
    },
    [BlockEnum.End]: {
        handle(node) {
            console.log(node);
            const params = {
                ...transformOrigData(node),
                output: new Variable('input', 'string', node.data['variable']),
                manual_confirmation: node.data['manual_confirmation'] || false,
                wait_for_all_predecessors: true,
            };

            const output = new ObjectVariable('output');
            if (node.data?.input_variables?.length) {
                const getNodeVars = useStore.getState().getOutputVariables(node.id);

                node.data.input_variables.forEach(x => {
                    if (x.name && x.variable) {
                        const createVar = getNodeVars.find(
                            item => item.value == x.variable,
                        )?.createVar;
                        const vars = new Variable(x.name, createVar?.type || 'string', x.variable);
                        output.addProperty(x.name, vars);
                    }
                });
            }
            params.output = output;

            return new EndNode(params);
        },
    },
};
export function transformWorkFlow(nodes: AppNode[], edges) {
    const newNodes = nodes.map(node => {
        const handle = transformer[node.type]?.handle;
        if (!handle) {
            return node;
        }
        return handle(node);
    });
    console.log(newNodes);

    const newEdges = edges.map(item => {
        console.log('edge', item);
        const edge = new Edge(
            item.level,
            item.source,
            item.target,
            item.sourceType,
            item.targetType,
        );
    });
}
export function flowSetLevel(nodes: AppNode[], edges) {
    const nodeLevels = {};
    const incomingEdgesCount = {};

    nodes.forEach(node => {
        nodeLevels[node.id] = 0;
        incomingEdgesCount[node.id] = 0;
    });

    edges.forEach(edge => {
        if (incomingEdgesCount.hasOwnProperty(edge.target)) {
            incomingEdgesCount[edge.target]++;
        }
    });

    const roots = nodes.filter(node => incomingEdgesCount[node.id] === 0);
    const queue = [...roots];

    while (queue.length > 0) {
        const currentNode = queue.shift();
        const currentLevel = nodeLevels[currentNode.id];

        edges.forEach(edge => {
            if (edge.source === currentNode.id) {
                const targetNode = nodes.find(node => node.id === edge.target);
                const targetNodeId = targetNode.id;

                nodeLevels[targetNodeId] = currentLevel + 1;

                incomingEdgesCount[targetNodeId]--;

                if (incomingEdgesCount[targetNodeId] === 0) {
                    queue.push(targetNode);
                }
            }
        });
    }

    const newNodes = nodes.map(node => {
        const nodeLevel = nodeLevels[node.id] || 0;
        node.level = nodeLevel;

        return node;
    });

    const newEdges = edges.map(edge => {
        const sourceLevel = nodeLevels[edge.source] || 0;
        const targetLevel = nodeLevels[edge.target] || 0;
        const edgeLevel = Math.max(sourceLevel, targetLevel);

        return {
            ...edge,
            level: edgeLevel,
        };
    });

    console.log(newNodes, newEdges);

    return { nodes: newNodes, edges: newEdges };
}

export function cleanEdges(nodes: AppNode[], edges) {
    const nodeIds = new Set(nodes.map(node => node.id));
    const validEdges = edges
        .filter(edge => nodeIds.has(edge.source) && nodeIds.has(edge.target))

        .filter(
            (edge, index, self) =>
                !edges.some(
                    (e, i) =>
                        e.source == edge.source &&
                        e.target == edge.target &&
                        e.id != edge.id &&
                        e.sourceHandle == edge.sourceHandle &&
                        e.targetHandle == edge.targetHandle,
                ),
        );

    return validEdges;
}
