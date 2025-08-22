/*
 * @LastEditors: biz
 */
import agent from './zh-CN/agent';
import component from './zh-CN/component';
import createkb from './zh-CN/createkb';
import creation from './zh-CN/creation';
import globalHeader from './zh-CN/globalHeader';
import menu from './zh-CN/menu';
import pages from './zh-CN/pages';
import plaza from './zh-CN/plaza';
import pwa from './zh-CN/pwa';
import settingDrawer from './zh-CN/settingDrawer';
import settings from './zh-CN/settings';
import skill from './zh-CN/skill';
import user from './zh-CN/user';
import workflow from './zh-CN/workflow';
import chatroom from './zh-CN/chatroom';
import role from './zh-CN/role';

export default {
    'navBar.lang': '语言',
    'layout.user.link.help': '帮助',
    'layout.user.link.privacy': '隐私',
    'layout.user.link.terms': '条款',
    'app.preview.down.block': '下载此页面到本地项目',
    'app.welcome.link.fetch-blocks': '获取全部区块',
    'app.welcome.link.block-list': '基于 block 开发，快速构建标准页面',
    ...pages,
    ...globalHeader,
    ...menu,
    ...settingDrawer,
    ...settings,
    ...pwa,
    ...component,
    ...workflow,
    ...creation,
    ...agent,
    ...skill,
    ...createkb,
    ...user,
    ...plaza,
    ...chatroom,
    ...role,
    'skill.downloadFiles': '输出文件',
    'skill.download': '下载',
    'app.workflow.log.filter.all': '全部日志',
    'app.workflow.log.filter.roundtable': '圆桌导向',
    'app.workflow.log.filter.agent': '智能体',
    'app.workflow.log.filter.workflow': '工作流',
    'app.workflow.log.output.files': '输出文件',
    'app.workflow.log.type.roundtable': '圆桌导向',
    'app.workflow.log.type.agent': '智能体',
    'app.workflow.log.type.workflow': '工作流',
    'app.workflow.log.type.agent.simple': '智能体',
    'app.workflow.log.type.workflow.simple': '工作流',
    'app.workflow.log.roundtable.guidance': '圆桌:{name} 导向执行',
    'app.workflow.log.guidance.execution': '导向执行{type}：{name}',
    'app.workflow.log.empty': '暂无日志记录',
    'app.chatroom.log.title': '导向日志',
    'app.chatroom.log.name': '导向名称',
    'workflow.created_time': '创建时间',
    'workflow.finished_time': '完成时间',
    'workflow.elapsed_time': '耗时',
    'workflow.status': '状态',
    'workflow.running': '运行中',
    'workflow.runSc': '已完成',
    'workflow.runF': '失败',
    'agent.log.output': '输出结果',
    'agent.log.error': '错误信息',
    'agent.log.run.failed': '运行失败',
    'agent.log.no.output': '暂无输出',
    'agent.log.corrections': '修正记录',
    'app.workflow.log.title': '应用日志',
    'workflow.resetRun': '重新运行',
    'workflow.resetRunSuccess': '重新运行成功',
};
