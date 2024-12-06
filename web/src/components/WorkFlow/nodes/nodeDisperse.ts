/*
 * @LastEditors: biz
 */
import { getLocale } from 'umi';
import { Node } from '.';
import { BlockEnum } from '../types';
import Agent from './Agent';
import AgentPanel from './Agent/panel';
import ConditionBranch from './ConditionBranch';
import ConditionBranchPanel from './ConditionBranch/panel';
import CustomCode from './CustomCode';
import CustomCodePanel from './CustomCode/panel';
import End from './End';
import EndPanel from './End/panel';
import HttpRequest from './Http';
import HttpRequestPanel from './Http/panel';
import Human from './Human';
import HumanPanel from './Human/panel';
import LLM from './LLM';
import LLMPanel from './LLM/panel';
import RequirementCategory from './RequirementCategory';
import RequirementCategoryPanel from './RequirementCategory/panel';
import Retriever from './Retriever';
import RetrieverPanel from './Retriever/panel';
import Skill from './Skill';
import SkillPanel from './Skill/panel';
import Start from './Start';
import StartPanel from './Start/panel';
import TemplateConversion from './TemplateConversion';
import TemplateConversionPanel from './TemplateConversion/panel';
import ToolNode from './ToolNode';
import ToolNodePanel from './ToolNode/panel';
import VariableAggregation from './VariableAggregation';
import VariableAggregationPanel from './VariableAggregation/panel';

import _ from 'lodash';
import TaskExecution from './TaskExecution';
import TaskExecutionPanel from './TaskExecution/panel';
import TaskGeneration from './TaskGeneration';
import TaskGenerationPanel from './TaskGeneration/panel';

export const NodeCustom = {
  [BlockEnum.Start]: {
    node: Start,
    panel: StartPanel,
    icon: BlockEnum.Start,
    title: '开始',
    entitle: 'Start',
    base: {
      type: BlockEnum.Start,
      position: {
        x: 100,
        y: 100,
      },
      data: {
        title: '开始节点',
        entitle: 'Start Node',
        desc: '',
        descTools: '这是一个初始化开始节点描述',
        endescTools: 'This is an initial start node description',
        outputInfo: {
          key: 'output',
          type: 'object',
          base: false,
        },
      },
    },
  },
  [BlockEnum.Agent]: {
    node: Agent,
    panel: AgentPanel,
    icon: BlockEnum.Agent,
    title: 'Agent',
    entitle: 'Agent',
    base: {
      type: BlockEnum.Agent,
      data: {
        title: 'Agent',
        entitle: 'Agent',
        desc: '',
        descTools: '这是一个初始化Agent节点描述',
        endescTools: 'This is an initial Agent node description',
        outputInfo: {
          key: 'text',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.LLM]: {
    node: LLM,
    icon: BlockEnum.LLM,
    panel: LLMPanel,
    title: 'LLM',
    entitle: 'LLM',
    base: {
      type: BlockEnum.LLM,
      data: {
        title: 'LLM',
        entitle: 'LLM',
        desc: '',
        descTools: '调用大语言模型回答问题或者处理任务',
        endescTools: 'Invoke large language models to answer questions or handle tasks',
        outputInfo: {
          key: 'text',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.HttpRequest]: {
    node: HttpRequest,
    icon: BlockEnum.HttpRequest,
    panel: HttpRequestPanel,
    title: 'Http',
    entitle: 'Http',
    base: {
      type: BlockEnum.HttpRequest,
      data: {
        title: 'Http请求',
        entitle: 'Http Request',
        desc: '',
        descTools: '通过http协议的请求获取响应结果数据',
        endescTools: 'Obtain response data through HTTP protocol requests',
        outputInfo: {
          key: 'output',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.Human]: {
    node: Human,
    icon: BlockEnum.Human,
    panel: HumanPanel,
    title: '人工确认',
    entitle: 'Human Confirmation',
    base: {
      type: BlockEnum.Human,
      data: {
        title: '人工确认',
        entitle: 'Human Confirmation',
        desc: '',
        descTools: '允许在工作流运行过程中人工介入补充数据',
        endescTools:
          'Allow manual intervention to supplement data during workflow execution',
        outputInfo: {
          key: 'output',
          type: 'object',
          base: false,
        },
      },
    },
  },
  [BlockEnum.CustomCode]: {
    node: CustomCode,
    icon: BlockEnum.CustomCode,
    panel: CustomCodePanel,
    title: '自定义代码',
    entitle: 'Custom Code',
    base: {
      type: BlockEnum.CustomCode,
      data: {
        title: '自定义代码',
        entitle: 'Custom Code',
        desc: '',
        descTools: '定义一段Python代码实现执行自定义逻辑',
        endescTools: 'Define a piece of Python code to execute custom logic',
        outputInfo: {
          key: 'output',
          type: 'object',
          base: false,
        },
      },
    },
  },
  [BlockEnum.Skill]: {
    node: Skill,
    icon: BlockEnum.Skill,
    panel: SkillPanel,
    title: '技能',
    entitle: 'Skill',
    base: {
      type: BlockEnum.Skill,
      data: {
        title: '技能',
        entitle: 'Skill',
        desc: '',
        descTools: '这是一个初始化技能节点描述',
        endescTools: 'This is an initial skill node description',
        outputInfo: {
          key: 'output',
          type: 'object',
          base: false,
        },
      },
    },
  },
  [BlockEnum.Retriever]: {
    node: Retriever,
    icon: BlockEnum.Retriever,
    panel: RetrieverPanel,
    title: '检索器',
    entitle: 'Retriever',
    base: {
      type: BlockEnum.Retriever,
      data: {
        title: '检索器',
        entitle: 'Retriever',
        desc: '',
        descTools: '从知识库中查询与用户的问题相关的文本内容',
        endescTools: 'Query text content related to user questions from the knowledge base',
        outputInfo: {
          key: 'output',
          type: 'object',
          base: true,
        },
      },
    },
  },
  [BlockEnum.VariableAggregation]: {
    node: VariableAggregation,
    icon: BlockEnum.VariableAggregation,
    panel: VariableAggregationPanel,
    title: '变量聚合器',
    entitle: 'Variable Aggregator',
    base: {
      type: BlockEnum.VariableAggregation,
      data: {
        title: '变量聚合器',
        entitle: 'Variable Aggregator',
        desc: '',
        descTools:
          '将多路条件分支（问题分类器/条件分支节点产生的分支）的变量聚合成一个变量，以便下游节点统一配置使用',
        endescTools:
          'Aggregate variables from multiple conditional branches into one for unified configuration by downstream nodes',
        outputInfo: {
          key: 'output',
          type: 'object',
          base: true,
        },
      },
    },
  },
  [BlockEnum.ConditionBranch]: {
    node: ConditionBranch,
    icon: BlockEnum.ConditionBranch,
    panel: ConditionBranchPanel,
    title: '条件分支',
    entitle: 'Conditional Branch',
    base: {
      type: BlockEnum.ConditionBranch,
      data: {
        title: '条件分支',
        entitle: 'Conditional Branch',
        desc: '',
        descTools: '根据定义的 if-elif-else 条件将工作流拆分成多个分支',
        endescTools:
          'Split the workflow into multiple branches based on defined if-elif-else conditions',
      },
    },
  },
  [BlockEnum.RequirementCategory]: {
    node: RequirementCategory,
    icon: BlockEnum.RequirementCategory,
    panel: RequirementCategoryPanel,
    title: '问题分类器',
    entitle: 'Requirement Classifier',
    base: {
      type: BlockEnum.RequirementCategory,
      data: {
        title: '问题分类器',
        entitle: 'Requirement Classifier',
        desc: '',
        descTools: '定义用户问题的分类条件，通过大语言模型分析出问题所属的分类',
        endescTools:
          'Define classification conditions for user questions and analyze the category using large language models',
        outputInfo: {
          key: 'category_name',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.TaskGeneration]: {
    node: TaskGeneration,
    icon: BlockEnum.TaskGeneration,
    panel: TaskGenerationPanel,
    title: '任务生成',
    entitle: 'Task Generation',
    base: {
      type: BlockEnum.TaskGeneration,
      data: {
        title: '任务生成',
        entitle: 'Task Generation',
        desc: '',
        descTools:
          '通过大语言模型将用户的需求进行补充和拆分，生成可递归结构的任务数据，以便下游的任务执行节点递归分配执行',
        endescTools:
          'Use large language models to supplement and split user requirements, generating recursive task data for downstream task execution nodes',
        outputInfo: {
          key: 'output',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.TaskExecution]: {
    node: TaskExecution,
    icon: BlockEnum.TaskExecution,
    panel: TaskExecutionPanel,
    title: '任务执行',
    entitle: 'Task Execution',
    base: {
      type: BlockEnum.TaskExecution,
      data: {
        title: '任务执行',
        entitle: 'Task Execution',
        desc: '',
        descTools:
          '将任务数据递归分配至执行器，最终生成带有任务执行结果的完整任务数据，仍然是原有可递归结构，以便下游的任务执行节点继续使用',
        endescTools:
          'Recursively assign task data to executors, ultimately generating complete task data with execution results, maintaining the original recursive structure for downstream nodes',
        outputInfo: {
          key: 'output',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.TemplateConversion]: {
    node: TemplateConversion,
    icon: BlockEnum.TemplateConversion,
    panel: TemplateConversionPanel,
    title: '模版转换',
    entitle: 'Template Conversion',
    base: {
      type: BlockEnum.TemplateConversion,
      data: {
        title: '模版转换',
        entitle: 'Template Conversion',
        desc: '',
        descTools: '定义jinja模板语法将数据转换为字符串',
        endescTools: 'Define Jinja template syntax to convert data into strings',
        outputInfo: {
          key: 'output',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.Tool]: {
    node: ToolNode,
    icon: BlockEnum.Tool,
    panel: ToolNodePanel,
    title: '工具',
    entitle: 'Tool',
    base: {
      type: BlockEnum.Tool,
      data: {
        title: '工具',
        entitle: 'Tool',
        desc: '',
        descTools: '这是一个初始化工具节点描述',
        endescTools: 'This is an initial tool node description',
        outputInfo: {
          key: 'output',
          type: 'string',
          base: true,
        },
      },
    },
  },
  [BlockEnum.End]: {
    node: End,
    icon: BlockEnum.End,
    panel: EndPanel,
    title: '结束节点',
    entitle: 'End Node',
    base: {
      type: BlockEnum.End,
      data: {
        title: '结束节点',
        entitle: 'End Node',
        desc: '',
        descTools: '定义一个工作流的流程结束和输出结果内容',
        endescTools: 'Define the end of a workflow process and output result content',
      },
    },
  },
};
export const getBaseNode = (type?: BlockEnum) => {
  const processNode = node => {
    if (getLocale() === 'en-US') {
      function replaceEnPrefix(obj) {
        return Object.keys(obj).reduce((acc, key) => {
          const enKey = `en${key.charAt(0) + key.slice(1)}`;
          if (obj[enKey]) {
            acc[key] = obj[enKey];
          } else {
            acc[key] = obj[key];
          }
          if (typeof obj[key] === 'object') {
            acc[key] = replaceEnPrefix(obj[key]);
          }
          return acc;
        }, {});
      }
      node.base.data = replaceEnPrefix(node.base.data);
      node.title = node.entitle;
    }
    return node;
  };

  if (type) {
    const node = _.cloneDeep(NodeCustom[type]);
    return processNode(node);
  } else {
    return Object.keys(NodeCustom).reduce((acc, key) => {
      acc[key] = processNode(_.cloneDeep(NodeCustom[key]));
      return acc;
    }, {});
  }
};

export const NodeTypes = () => {
  const types = {};
  Object.keys(NodeCustom).forEach(key => {
    types[key] = Node;
  });
  return types;
};
