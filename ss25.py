from website import base_page

# 首页
class home_page(base_page):
    def __init__(self):
        self.set_url("http://www.2s5s.com/")

    def get_all_links(self):
        soup = self.pp136_html(self.get_html())
        tags = soup.select('div.nav_btn > a[href*="pai"]')
        if tags:
            links = []
            for tag in tags:
                links.append({"link": self.adjust_url(tag["href"]), "text": tag.text})
            return links
        return None

    def adjust_url(self, url):
        return self.get_url() + url

    def path(self):
        return "s2s5网站"



# 数据页面
class page(base_page):
    #  页面的标题
    __title = ""

    def __init__(self, url):
        self.set_url_deep(url, deep=2)

    # 路径
    def path(self):
        if "" == self.__title:
            soup = self.pp136_html(self.get_html())
            self.__title = soup.title.text
        return self.__title

    # 所有资源项
    def get_all_links(self):
        soup = self.pp136_html(self.get_html())
        imageList = soup.select('.img_list li[class="box_shadow"]')

        if imageList:
            items = []
            for image in imageList:
                img = None
                imgLink = image.find("a", class_="imgC")
                if imgLink:
                    img = imgLink.find("img")

                link = image.find("a")
                items.append({"link": self.adjust_url(link["href"]), "title": link.text, "img": self.adjust_url(img["src"])})
            return items
        return None

    # 下一页
    def next_page(self):
        soup = self.pp136_html(self.get_html())

        np = soup.find('div', class_="page")\
            .find("a", text="下一页")
        if np:
            link = {"link": self.adjust_url2(np["href"])}
            return link
        return None


    def adjust_url(self, url):
        return self.get_parent() + url

    def adjust_url2(self, url):
        return self.get_url()[0: self.get_url().rfind("/")]+ "/" + url


class page_detail(base_page):

    # 标题
    __title = ""

    def __init__(self, url):
        self.set_url_deep(url, deep=4)


    # 获取资源
    def get_all_res(self):
        soup = self.pp136_html(self.get_html())
        contentPic = soup.select("div.content_pic img[src]")
        if contentPic:
            pics = []
            for pic in contentPic:
                pics.append({"img":self.adjust_url(pic["src"])})
            return pics
        return None

    # 下一页
    def next_page(self):
        soup = self.pp136_html(self.get_html())

        np = soup.find('div', class_="page")
        if np:
            np = np.find("a", text="下一页")
            if np:
                link = {"link": self.adjust_url2(np["href"])}
                return link
        return None


    def adjust_url(self, url):
        return self.get_parent() + url

    def adjust_url2(self, url):
        return self.get_url()[0:self.get_url().rfind("/")] + "/" + url

    # 路径
    def path(self):
        if "" == self.__title:
            soup = self.pp136_html(self.get_html())
            self.__title = soup.title.text
        return self.__title
