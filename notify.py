#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

mail_host = "smtp.exmail.qq.com" # 邮箱smtp地址
mail_user = "邮箱地址"
mail_pass = "邮箱密码"

def mail(to_email, content, title, to_name='Onns'):
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = formataddr(["Onns", mail_user])
    message['To'] = formataddr([to_name, to_email])
    message['Subject'] = Header(title, 'utf-8')

    try:
        server = smtplib.SMTP_SSL(mail_host, 465)
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, [to_email], message.as_string())
        server.quit()
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

if __name__ == "__main__":
    mail(u'onns@onns.xyz', u'测试一下', '打卡结果', 'Onns')
