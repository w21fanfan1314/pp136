import os
import requests
import hashlib
import jieba

from website import page_inteface

# 配置信息
class config:
    # 当前的操作目录， 默认当前目录
    path = ""

    # 文件名称
    __config_name = "pp136"

    # 所有的路劲
    urls = []

    def __init__(self, config_name):
        self.path = os.path.abspath("config")
        self.__config_name = config_name
        self.__init_config()

    # 加入一个URL
    def add_url(self, url):
        file = self.__get_config_path("a")

        if not self.urls.__contains__(url):
            file.write(url + "\n")
            self.urls.append(url)

        file.close()

    # 读取配置信息
    def read_config(self):
        file = self.__get_config_path("r")
        self.urls = []
        for line in file:
            self.urls.append(line.replace("\n", ""))
        file.close()
        return self.urls

    # 删除一个URL
    def remove_url(self, url):
        file = self.__get_config_path("r")

        text = ""
        for line in file:
            if line.__ne__(url +'\n'):
                text += line
        file.close()

        file = self.__get_config_path("w")
        file.write(text)
        file.close()

    # 初始化配置信息
    def __init_config(self):
        file = self.__get_config_path("a")
        file.close()

        self.read_config()

    # 获取当前的配置目录
    def __get_config_path(self, mode):
        exists = os.path.exists(self.path)
        if not exists:
            os.makedirs(self.path)
        return open(self.path +"/" + self.__config_name +'.txt', mode)



# 在文件到本地
class download:
    # 保存的目录
    save_path = ""

    def __init__(self):
        self.save_path = os.path.abspath("")
        self.__m = hashlib.md5()

    # 保存文件信息
    def download_file(self, file, link):
        r = requests.get(link, stream=True, timeout=60)
        if r.status_code == 200:
            dir = self.save_path +"/" + file
            if not os.path.exists(dir):
                os.makedirs(dir)

            with open(dir + self.__get_file_name(link), "wb") as f:
                for chunk in r:
                    f.write(chunk)
                f.close()

    # 根据文件的路径检测文件是否已经下载
    def check(self, path):
        return os.path.isfile(path) and os.path.exists(path)

    # 获取文件的名称
    def __get_file_name(self, link = ""):
        (filepath, temp_file_name) = os.path.split(link)
        (sort_name, extension) = os.path.splitext(temp_file_name)
        self.__m.update(link.encode("utf8"))
        return self.__m.hexdigest() + extension



class run:

    __home_link = None
    __page_link = None

    # 首页
    home = page_inteface
    # 子页面
    page = page_inteface
    # 详情
    detail = page_inteface

    def __init__(self, home, page, detail):
        self.home = home()
        self.page = page
        self.detail = detail

        self.word = cloud_word()
        self.conf = config(self.home.path())
        self.down = download()


    # 检测网站是否已经开始爬取
    def __is_get(self):
        paths = self.conf.read_config()
        return paths.__len__() > 0

    # 爬去网站的所有数据
    def get_all_res(self):
        self.get_website_by_config(self.conf.read_config())

    def get_website_by_config(self, urls = []):
        if urls and urls.__len__() == 2:
            self.__home_link = urls[0]
            self.__page_link = urls[1]
        else:
            self.word.clear_words()

        home_links = self.home.get_all_links()
        if home_links:
            for home_link in home_links:
                h_title = home_link["text"]
                h_link = home_link["link"]
                if not self.__home_link:
                    self.__home_link = h_link
                else:
                    if self.__home_link == h_link:
                        self.__home_link = h_link
                    else:
                        continue

                self.conf.add_url(self.__home_link)
                p = self.page(self.__home_link)
                while True:
                    # 某一个菜单下，页面中的所有的链接
                    page_links = p.get_all_links()
                    for page_link in page_links:
                        title = page_link["title"]
                        link = page_link["link"]
                        if not self.__page_link:
                            self.__page_link = link
                        else:
                            if self.__page_link == link:
                                self.__page_link = link
                            else:
                                continue

                        print("页面地址:" + self.__page_link)
                        self.conf.add_url(self.__page_link)
                        # 加入词云的统计
                        self.word.add_word(p.path())

                        # 获取资源
                        d = self.detail(self.__page_link)
                        while True:
                            save_path = self.home.path() + "/" + p.path() + "/" + d.path() + "/"
                            detail_res = d.get_all_res()
                            if detail_res:
                                for res in detail_res:
                                    img_src = res["img"]
                                    print("下载内容:" + img_src)
                                    self.down.download_file(save_path, img_src)
                                    print("[下载成功]")

                            # 下一页的数据
                            nl = d.next_page()
                            if nl:
                                d.set_url(nl["link"])
                            else:
                                break
                        self.conf.remove_url(self.__page_link)
                        self.__page_link = None

                    # 获取下一页的地址，如果由继续的向下爬取
                    next_link = p.next_page()
                    if next_link:
                        print("下一页:" + next_link["link"])
                        p.set_url(next_link["link"])
                    else:
                        break

                self.conf.remove_url(self.__home_link)
                self.__home_link = None
            print(self.word.statistics_words())

        else:
            print("[Error] 无法获取起始页的地址")



# 提取词汇的功能
class cloud_word:
    # 进行标题分词
    words = []

    def __init__(self):
        self.__save_path = os.path.abspath("word.txt")


    # 加入词云
    def add_word(self, text):
        file = open(self.__save_path, "a")
        file.write(text)
        file.close()

    # 清空词云
    def clear_words(self):
        os.remove(self.__save_path)

    # 统计词云
    def statistics_words(self):
        file = open(self.__save_path, "r")
        __words = ""
        for line in file:
            __words += line
        file.close()

        self.words = jieba.cut(__words, cut_all=False)
        mapping = {}
        for word in set(self.words):
            mapping[word] = self.words.count(word)
        return mapping
