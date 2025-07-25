from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from collections.abc import Generator
from typing import Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SendMailTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        mailserver = "smtp.163.com"  # 邮箱服务器地址
        port = 465  # 邮箱服务器端口

        # 获取参数
        username_send = tool_parameters['username_send']
        authorization_code = tool_parameters['authorization_code']
        username_recv = tool_parameters['username_recv']
        subject = tool_parameters.get('subject', 'AI发送')  # 可选参数
        content = tool_parameters.get('content', 'This is the body of the email.')  # 可选参数

        # 将收件人字符串拆分成列表
        recipients = [recipient.strip() for recipient in username_recv.split(',')]

        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = username_send
        msg['To'] = ', '.join(recipients)  # 将收件人列表转换为字符串
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(content, 'plain'))

        try:
            # 连接到SMTP服务器并发送邮件
            with smtplib.SMTP_SSL(mailserver, port) as server:
                server.login(username_send, authorization_code)
                server.sendmail(username_send, recipients, msg.as_string())
            yield self.create_json_message({
                "result": "Email sent successfully!"
            })
        except Exception as e:
            yield self.create_json_message({
                "result": f"Failed to send email: {str(e)}"
            })
