#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'John Tang'

from sdk.weibo_simple_sdk import Client

API_KEY = ''            # app key
API_SECRET = ''      # app secret
REDIRECT_URI = 'http://hitangjun.com'
WEIBO_USERNAME = ''
WEIBO_PASSWORD = ''

class weibo_api:
    def check(self):
        c = Client(API_KEY, API_SECRET, REDIRECT_URI,
                   username=WEIBO_USERNAME, password=WEIBO_PASSWORD)
        show = c.get('users/show', uid=1282440983)
        print(show)
        statuses = c.get('statuses/home_timeline')
        statuses = str(statuses).decode("unicode-escape")
        print statuses

    @property
    def statuses(self):
        c = Client(API_KEY, API_SECRET, REDIRECT_URI,
                   username=WEIBO_USERNAME, password=WEIBO_PASSWORD)
        statuses = c.get('statuses/home_timeline')
        statuses = str(statuses).decode("unicode-escape")
        return statuses

# if __name__=='__main__':
    # check()