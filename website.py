import requests
from bs4 import BeautifulSoup


class pp:
    # 网站源码解析方式
    parser = "html5lib"

    # 请求 PP136 网站
    def pp136_request(self, url):
        r = requests.get(url)
        r.encoding = "GBK"
        return r

    # 请求 pp136 并且返回解析后的对象
    def pp136_html(self, html):
        soup = BeautifulSoup(html, self.parser)
        return soup

    # 通过一个地址请求 获取网页的源代码，进行解析后返回对象
    def pp136_url(self, url):
        soup = BeautifulSoup(self.pp136_request(url), self.parser)
        return soup

# 网站接口
class page_inteface:
    # 获取页面的所有可以爬去的连接
    def get_all_links(self):
        return None

    # 获取当前的页面的路径
    def path(self):
        return None

    # 获取下一个页面的连接
    def next_page(self):
        return None

    # 获取页面的可以保存的资源连接
    def get_all_res(self):
        return None

    # 获取网页源码
    def get_html(self):
        return None

    # 页面地址
    def get_url(self):
        return None

    # 调整URL， 返回已经调整好的的URL
    def adjust_url(self, url):
        return url

# 基础网站实现
class base_page(page_inteface, pp):
    __url = ""
    # 已经加载的内容
    __html = ""
    # 上一级目录
    __parent = ""
    # 父类级别
    __deep = 1

    # 获取页面的html内容，只获取一次
    def get_html(self):
        if self.__url and "" == self.__html:
            r = self.pp136_request(self.__url)
            self.__html = r.text
        return self.__html

    # 获取当前页面地址
    def get_url(self):
        return self.__url

    # 设置当前页面的链接
    def set_url(self, url):
        self.set_url_deep(url, self.__deep)

    def set_url_deep(self, url, deep = 1):
        self.__deep = deep
        self.__url = url
        self.__parent = url
        for i in range(0, deep):
            self.__parent = self.__parent[0:self.__parent.rfind("/")]
        # 清空缓存的网页内容
        self.__html = ""

    def get_parent(self):
        return self.__parent