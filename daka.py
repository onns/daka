#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
import time
import random
from notify import mail
import json
import datetime

print('VERSION: 20210606')

f = open('daka-config.json', 'r', encoding='utf-8')
data = json.loads(f.read())
f.close()

# 检查打卡结果，发送失败邮件
if datetime.datetime.now().hour >= 14:
    i = 0
    while True:
        if i >= len(data['people']):
            break
        if data['people'][i]['isDaka']:
            data['people'][i]['isDaka'] = False
        else:
            mail(data['people'][i]['email'], data['people'][i]['emailCheckText'],
                 data['people'][i]['emailTitle'], data['people'][i]['emailName'])
        i += 1
    f = open('daka-config.json', 'w', encoding='utf-8')
    f.write(json.dumps(data, ensure_ascii=False, indent=4))
    f.close()
    exit()

chromedriverAddress = data['chromedriverAddress']
people = data['people']

driver = webdriver.Chrome(executable_path=chromedriverAddress)


def ids_login(xmuid, password):
    driver.find_element_by_id('username').send_keys(xmuid)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_class_name('auth_login_btn').click()


def check_url():
    current_url = driver.current_url
    if current_url.find('platform') != -1:
        return 'platform'
    if current_url.find('ids.xmu.edu.cn/authserver') != -1:
        return 'auth'
    if current_url.find('xmuxg.xmu.edu.cn/app/214') != -1:
        return 'daka'
    if current_url.find('xmu/login') != -1:
        return 'login'


def logout():
    try:
        global driver
        driver.quit()
        driver = webdriver.Chrome(executable_path=chromedriverAddress)
        time.sleep(random.randint(3, 8))
    except Exception as e:
        print(e)
        exit()


def find_option(opts, str):
    for opt in opts:
        if opt.text.strip().find(str) > -1:
            if opt.get_attribute('class').find('active') == -1:
                opt.click()
                time.sleep(random.randint(1, 4))
                break


def scrollandset(eleid, elevalue):
    driver.execute_script(
        "arguments[0].scrollIntoView();", driver.find_element_by_id(eleid))
    time.sleep(random.randint(1, 4))
    for i, n in enumerate(elevalue):
        driver.find_element_by_id(
            eleid).find_elements_by_tag_name('div')[i].click()
        time.sleep(random.randint(1, 4))
        find_option(driver.find_elements_by_class_name('dropdown-items'), n)


def parseTime(hour, minute):
    return hour*60 + minute


def isAwake(time, isTheLastTime=False):
    if isTheLastTime:
        return True
    awakeTime = parseTime(int(time[:2]), int(time[3:]))
    nowTime = parseTime(datetime.datetime.now().hour,
                        datetime.datetime.now().minute)
    if (nowTime - 5) <= awakeTime and awakeTime <= (nowTime + 5):
        return True
    return False


i = 0
err = 0
isTheLastTime = False

# 12点之后一律不看时间只看打卡结果
if datetime.datetime.now().hour >= 12:
    isTheLastTime = True

while True:
    if err >= 3:
        err = 0
        i += 1
    if i >= len(people):
        break
    try:
        if (not isAwake(people[i]['time'], isTheLastTime)) or people[i]['isDaka']:
            i += 1
            err = 0
            continue
        xmuid = people[i]['xmuid']
        password = people[i]['password']
        url = 'https://xmuxg.xmu.edu.cn/xmu/login?app=214'
        driver.get(url)
        driver.find_element_by_xpath("//*[text()='统一身份认证']").click()
        time.sleep(random.randint(3, 8))
        if check_url() == 'auth':
            driver.find_element_by_id('username').send_keys(xmuid)
            time.sleep(random.randint(3, 8))
            driver.find_element_by_id('password').send_keys(password)
            time.sleep(random.randint(3, 8))
            driver.find_element_by_class_name('auth_login_btn').click()
            time.sleep(random.randint(1, 8))
        else:
            logout()
            continue

        name = driver.find_element_by_class_name(
            'account-name').get_attribute('textContent').strip()
        print(name)

        url = 'https://xmuxg.xmu.edu.cn/app/214'
        driver.get(url)
        time.sleep(random.randint(12, 18))
        if check_url() == 'daka':
            driver.find_element_by_xpath("//*[text()='我的表单']").click()
            time.sleep(random.randint(13, 18))
        else:
            logout()
            continue

        if driver.page_source.find(u'修改了表单') != -1:
            log_time = driver.find_element_by_class_name(
                'log-time').get_attribute('textContent')
            print(log_time)
            mail(people[i]['email'], people[i]['emailRepeatText'],
                 people[i]['emailTitle'], people[i]['emailName'])
            print("Already Done!")
        else:
            driver.execute_script("arguments[0].scrollIntoView();",
                                  driver.find_element_by_id('select_1582538939790'))
            driver.find_element_by_id(
                'select_1582538939790').find_elements_by_tag_name('div')[0].click()
            driver.find_element_by_class_name('dropdown-items').click()
            driver.find_element_by_class_name('form-save').click()
            driver.switch_to_alert().accept()
            mail(people[i]['email'], people[i]['emailSuccessText'],
                 people[i]['emailTitle'], people[i]['emailName'])
            print("Done!")
        people[i]['isDaka'] = True
        logout()
        i += 1
    except Exception as e:
        print(e)
        err += 1
        print(err)
        mail(people[i]['email'], people[i]['emailFailText'] +
             str(err), people[i]['emailTitle'], people[i]['emailName'])
        logout()
driver.quit()

data['people'] = people

f = open('daka-config.json', 'w', encoding='utf-8')
f.write(json.dumps(data, ensure_ascii=False, indent=4))
f.close()
