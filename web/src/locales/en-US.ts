/*
 * @LastEditors: biz
 */
import agent from './en-US/agent';
import component from './en-US/component';
import createkb from './en-US/createkb';
import creation from './en-US/creation';
import globalHeader from './en-US/globalHeader';
import menu from './en-US/menu';
import pages from './en-US/pages';
import plaza from './en-US/plaza';
import pwa from './en-US/pwa';
import settingDrawer from './en-US/settingDrawer';
import settings from './en-US/settings';
import skill from './en-US/skill';
import user from './en-US/user';
import workflow from './en-US/workflow';

export default {
    'navBar.lang': 'Languages',
    'layout.user.link.help': 'Help',
    'layout.user.link.privacy': 'Privacy',
    'layout.user.link.terms': 'Terms',
    'app.preview.down.block': 'Download this page to your local project',
    'app.welcome.link.fetch-blocks': 'Get all block',
    'app.welcome.link.block-list': 'Quickly build standard, pages based on `block` development',
    ...globalHeader,
    ...menu,
    ...settingDrawer,
    ...settings,
    ...pwa,
    ...component,
    ...pages,
    ...workflow,
    ...creation,
    ...agent,
    ...createkb,
    ...user,
    ...skill,
    ...plaza,
    'skill.downloadFiles': 'Download Files',
    'skill.download': 'Download',
};
