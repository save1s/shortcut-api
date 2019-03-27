#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from selenium import webdriver
SELENIUM_SERVER_ADDRESS = os.environ['SELENIUM_SERVER_ADDRESS']


def login(qq_number, qq_password):

    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--no-sandbox')

    # 这里由于leancloud无法安装chrome，所以使用了外部的一台selenium server主机
    driver = webdriver.Remote(command_executor='http://{}/wd/hub'.format(SELENIUM_SERVER_ADDRESS),
                              desired_capabilities=option.to_capabilities())
    # driver.set_window_size(1920, 1080)
    driver.get('http://i.qq.com/')
    driver.switch_to.frame('login_frame')
    driver.find_element_by_id('switcher_plogin').click()
    driver.find_element_by_name('u').clear()
    driver.find_element_by_name('u').send_keys(qq_number)
    driver.find_element_by_name('p').clear()
    driver.find_element_by_name('p').send_keys(qq_password)
    driver.find_element_by_id('login_button').click()
    time.sleep(120)
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    driver.close()
    return cookies
