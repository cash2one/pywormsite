# coding:utf-8
import re
import logging

import tornado
import tornado.web
import tornado.gen
import tornado.escape
import tornado.websocket
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPClient

from pywormsite import config

request_log = logging.getLogger('request')
error_log = logging.getLogger('error')


# 搜索博客
class SearchHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        url_list = []
        title_list = []
        content = None
        try:
            content = self.get_argument('content')
        except Exception as e:
            pass
        if content:
            data = yield self.get_search(content)
            url_list = data["url_list"]
            title_list = data["title_list"]

        # self.render('search.html', url_list=url_list, title_list=title_list)
        self.render('youziku.html', url_list=url_list, title_list=title_list)

    @tornado.gen.coroutine
    def post(self):
        url_list = []
        title_list = []
        content = None
        try:
            content = self.get_argument('content')
        except Exception as e:
            error_log.error(e)
        if content:
            data = yield self.get_search(content)
            url_list = data["url_list"]
            title_list = data["title_list"]

        self.render('search.html', url_list=url_list, title_list=title_list)

    @tornado.gen.coroutine
    def get_search(self, content):
        url_list = []
        title_list = []
        html = None

        rd = '<h2><a href=".+?" target="_blank">(.*' + str(content) + ".*?)</a></h2>"
        rc = '<h2><a href="(.+?)" target="_blank">.*' + str(content) + ".*?</a></h2>"
        rb = re.compile(rd, re.IGNORECASE)
        ra = re.compile(rc, re.IGNORECASE)
        url = "http://{0}/catalog".format(self.application.url)
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(url, request_timeout=120)
        if response and response.code == 200:
            html = response.body.decode('utf-8')
        try:
            title_list = re.findall(rb, html)
            url_list = re.findall(ra, html)
            if not url_list:
                url_list = ['#']
                title_list = ['没有此类博文']
        except Exception as e:
            error_log.error(e)

        return {"url_list": url_list, "title_list": title_list}


@tornado.gen.coroutine
def get_search(content):
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()
    blog_id = []
    try:
        html = None

        rc = '<h2><a href="/blog/(.+?)/" target="_blank">.*' + str(content) + ".*?</a></h2>"
        ra = re.compile(rc, re.IGNORECASE)
        # url = "http://{0}/catalog".format(config()["pyworm_blog"]["url"])
        url = "http://www.pyworm.com/catalog/"
        http_client = HTTPClient()
        response = None
        try:
            response = http_client.fetch(url, request_timeout=5)
        except Exception as e:
            error_log.error(e)
        if response and response.code == 200:
            html = response.body.decode('utf-8')
        try:
            blog_id = re.findall(ra, html)
        except Exception as e:
            error_log.error(e)
    except Exception as e:
        error_log.error(e)
    finally:
        io_loop.stop()
    return {"blog_id": blog_id}
