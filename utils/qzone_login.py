#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
info:
author:CriseLYJ
github:https://github.com/CriseLYJ/
update_time:2019-3-7
"""

# import time  # 用来延时
from selenium import webdriver


def login(QQ_NUMBER, QQ_PASSWORD):
    driver = webdriver.Chrome()
    driver.get('http://i.qq.com/')
    driver.switch_to.frame('login_frame')
    driver.find_element_by_id('switcher_plogin').click()

    driver.find_element_by_name('u').clear()
    driver.find_element_by_name('u').send_keys(QQ_NUMBER)  # 此处输入你的QQ号
    driver.find_element_by_name('p').clear()
    driver.find_element_by_name('p').send_keys(QQ_PASSWORD)  # 此处输入你的QQ密码

    driver.execute_script(
        "document.getElementById('login_button').parentNode.hidefocus=false;")

    driver.find_element_by_xpath('//*[@id="loginform"]/div[4]/a').click()
    driver.find_element_by_id('login_button').click()

    # time.sleep(10)  # 因为我曾经是QQ会员，所以每次登陆时都会提醒我要不要再续费的弹窗...

    # # 这个地方是我把那个弹窗给点击了，配合上面的延时用的，延时是等待那个弹窗出现，然后此处点击取消
    # driver.find_element_by_id('dialog_button_1').click()

    btns = driver.find_elements_by_css_selector(
        'a.item.qz_like_btn_v3')  # 此处是CSS选择器
    for btn in btns:
        btn.click()
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    driver.close()
    return cookies  # dict
