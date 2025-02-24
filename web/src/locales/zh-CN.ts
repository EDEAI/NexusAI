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
    'skill.downloadFiles': '下载文件',
    'skill.download': '下载',
};
