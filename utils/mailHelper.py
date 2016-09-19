# coding:utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header


class MailHelper:
    # 第三方 SMTP 服务
    mail_host = "smtp.mxhichina.com"  # 设置服务器
    mail_user = "developer@vomoho.com"  # 用户名
    mail_pass = "dt@1234567"  # 口令
    sender = 'developer@vomoho.com'
    # receivers = ['zhouyong.shi@vomoho.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    content = ''
    title = ''
    message = ''
    subject = ''

    def __init__(self, content, title):
        self.content = content
        self.title = title
        self.message = MIMEText(content, 'plain', 'utf-8')
        self.message['From'] = Header("梦虎管理运维系统", 'utf-8')
        self.message['To'] = Header("测试", 'utf-8')
        self.subject = title
        self.message['Subject'] = Header(self.subject, 'utf-8')

    def send(self, receivers):
        smtpObj = smtplib.SMTP()
        smtpObj.connect(self.mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(self.mail_user, self.mail_pass)
        smtpObj.sendmail(self.sender, receivers, self.message.as_string())
        print(receivers)
        print(self.message.as_string())
        print("邮件发送成功")
        smtpObj.close()



