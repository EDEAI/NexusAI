from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import datetime
from datetime import timedelta
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage, AssistantPromptMessage



def extract_ret_string(text:str) -> dict:
    import re
    pattern = r"\b(\d{4}-\d{2}-\d{2}#\d{4}-\d{2}-\d{2})\b"
    dates=re.findall(pattern, text)[0]
    dates=dates.split('#')
    if len(dates)==2:
        st,ed=dates
    else:
        st=dates[0]
        ed=''
    return {
        "start_date":st,
        "end_date":ed
    }


def get_date_range():
    date_mapping={
        1:"一",
        2:"二",
        3:"三",
        4:"四",
        5:"五",
        6:"六",
        7:"天",
        }
    now_date=datetime.datetime.now()
    ret=[]
    for x in range(-20,21):
        delta=datetime.timedelta(days=x)
        temp_date=now_date+delta
        weekday=temp_date.weekday()+1
        weekday=f"星期{date_mapping[weekday]}"
        temp_date=temp_date.strftime("%Y-%m-%d")
        ret.append(f"{temp_date}:{weekday}")
    ret="\n".join(ret)
    today=datetime.datetime.now()
    now_time_hms=today.strftime("%H:%M")
    today_date=today.strftime("%Y-%m-%d")
    week_day=today.weekday()+1
    week_day=date_mapping[week_day]
    today_weekday=f"星期{week_day}"
    return {
        "today_date": today_date,
        "today_weekday":today_weekday,
        "date_range":ret,
        "now_time":str(datetime.datetime.now())
    }

def get_week_range():
    now = datetime.datetime.now()
    this_week_start = now - timedelta(days=now.weekday())
    this_week_end = now + timedelta(days=6 - now.weekday())
    
    last_week_start = now - timedelta(days=now.weekday() + 7)
    last_week_end = now - timedelta(days=now.weekday() + 1)
    
    this_month_start = datetime.datetime(now.year, now.month, 1)
    this_month_end = datetime.datetime(now.year, now.month + 1, 1) - timedelta(days=1)
    
    last_month_end = this_month_start - timedelta(days=1)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)

    this_month_start=this_month_start.strftime("%Y-%m-%d")
    this_month_end=this_month_end.strftime("%Y-%m-%d")

    last_month_end=last_month_end.strftime("%Y-%m-%d")
    last_month_start=last_month_start.strftime("%Y-%m-%d")

    last_week_start=last_week_start.strftime("%Y-%m-%d")
    last_week_end=last_week_end.strftime("%Y-%m-%d")

    this_week_start=this_week_start.strftime("%Y-%m-%d")
    this_week_end=this_week_end.strftime("%Y-%m-%d")

    return {'this_week_start':this_week_start,"this_week_end":this_week_end,"last_week_start":last_week_start,"last_week_end":last_week_end,'this_month_start':this_month_start,"this_month_end":this_month_end,"last_month_end":last_month_end,"last_month_start":last_month_start}


def get_week_day():
    today = datetime.date.today()  # 获取今天的日期
    weekday_today = today.weekday()  # 获取今天是星期几
    days_to_wednesday = 2 - weekday_today  # 计算距离上周三相差的天数
    #if days_to_wednesday > 0:  # 如果days_to_wednesday>0，即今天是周一、二或三
    days_to_wednesday -= 7  # 则减去一周的天数，从而获取到上周三的日期
    last_wednesday = (today + datetime.timedelta(days=days_to_wednesday)).strftime("%Y-%m-%d")  # 计算上周三的日期
    days_to_wednesday = 2 - weekday_today  # 计算距离上周三相差的天数
    #if days_to_wednesday > 0:  # 如果days_to_wednesday>0，即今天是周一、二或三
    days_to_wednesday += 7  # 则减去一周的天数，从而获取到上周三的日期
    next_wednesday = (today + datetime.timedelta(days=days_to_wednesday)).strftime("%Y-%m-%d")  # 计算上周三的日期
    days_to_wednesday = 2 - weekday_today  # 计算距离上周三相差的天数
    #if days_to_wednesday > 0:  # 如果days_to_wednesday>0，即今天是周一、二或三
    #days_to_wednesday += 7  # 则减去一周的天数，从而获取到上周三的日期
    this_wednesday = (today + datetime.timedelta(days=days_to_wednesday)).strftime("%Y-%m-%d")  # 计算上周三的日期
    return {"last_wednesday":last_wednesday,"next_wednesday":next_wednesday,"this_wednesday":this_wednesday}


class NlpTimeTransTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        tz=tool_parameters["TZ"]
        import os
        os.environ['TZ'] = tz
        import time
        time.tzset()
        out_pattern="{开始时间}#{结束时间}"
        date_range_info=get_date_range()
        system_prompt=f"""请识别用户输入中事件的开始和结束时间，按照%Y-%m-%d的形式输出。
输出格式为：
{out_pattern}

另外提供给你一些参考信息：
一周是指周一到周日
今天日期是{date_range_info['today_date']}
今天是{date_range_info['today_weekday']}

近期日历为：
{date_range_info['date_range']}

请严格按照输出格式进行输出，参照对话样例
"""

        week_day_info=get_week_day()
        week_range_info=get_week_range()

        response = self.session.model.llm.invoke(
            model_config=tool_parameters.get('model'),
            prompt_messages=[
                SystemPromptMessage(
                    content=system_prompt
                ),
                UserPromptMessage(
                    content="今天"
                ),
                AssistantPromptMessage(
                    content=f"{date_range_info['today_date']}#{date_range_info['today_date']}"
                ),
                UserPromptMessage(
                    content="上周"
                ),
                AssistantPromptMessage(
                    content=f"{week_range_info['last_week_start']}#{week_range_info['last_week_end']}"
                ),
                UserPromptMessage(
                    content="这个月"
                ),
                AssistantPromptMessage(
                    content=f"{week_range_info['this_month_start']}#{week_range_info['this_month_end']}"
                ),
                UserPromptMessage(
                    content="这周"
                ),
                AssistantPromptMessage(
                    content=f"{week_range_info['this_week_start']}#{week_range_info['this_week_end']}"
                ),
                UserPromptMessage(
                    content="上周三"
                ),
                AssistantPromptMessage(
                    content=f"{week_day_info['last_wednesday']}#{week_day_info['last_wednesday']}"
                ),
                UserPromptMessage(
                    content="这周三"
                ),
                AssistantPromptMessage(
                    content=f"{week_day_info['this_wednesday']}#{week_day_info['this_wednesday']}"
                ),
                UserPromptMessage(
                    content="下周三"
                ),
                AssistantPromptMessage(
                    content=f"{week_day_info['next_wednesday']}#{week_day_info['next_wednesday']}"
                ),
                UserPromptMessage(
                    content="上个月"
                ),
                AssistantPromptMessage(
                    content=f"{week_range_info['last_month_start']}#{week_range_info['last_month_end']}"
                ),
                UserPromptMessage(
                    content=tool_parameters.get('query')
                )
            ],
            stream=False
        )

        ret=response.message.content
        ret=extract_ret_string(ret)

        #yield self.create_json_message(ret)
        yield self.create_variable_message("start_date",ret['start_date'])
        yield self.create_variable_message("end_date",ret['end_date'])
