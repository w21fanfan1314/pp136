from website import base_page



# 代表一个网页的内容
class page(base_page):
    # 标题
    __title = ""

    # 通过一个地址创建一个页面对象
    def __init__(self, url = ""):
        self.set_url(url)

    # 获取当前页面的所有连接
    def get_all_links(self):
        soup = self.pp136_html(self.get_html())
        items = soup.find_all("table", class_="y")
        if items:
            els = []
            for item in items:
                # 图像
                img = item.find("img")
                # 标题和连接
                link = item.find("a", class_="mayi")
                els.append({"title": link.text, "img": img["src"], "link": self.adjust_url(link["href"])})
            return els
        return None

    # 获取当前页面的下一页内容
    def next_page(self):
        soup = self.pp136_html(self.get_html())

        nextLink = soup.find("a", title="下一页")
        if nextLink:
            return {"link": self.adjust_url(nextLink["href"])}
        return None

    # 路径
    def path(self):
        if "" == self.__title:
            soup = self.pp136_html(self.get_html())
            self.__title = soup.title.text
        return self.__title

    def adjust_url(self, url):
        return self.get_parent() +'/' + url



# 首页
class home_page(base_page):

    def __init__(self):
        self.set_url("http://www.pp136.com/")

    # 获取首页的菜单
    def get_menus(self):
        soup = self.pp136_html(self.get_html())
        menu = soup.find("table", attrs={"height": "34"})
        if menu:
            links = menu.find_all("a")
            if 0 < len(links):
                menus = []
                for link in links:
                    if link.text:
                        menus.append({"link": link["href"], "text": link.text})
                return menus
        return None

    # 获取更新链接
    def get_upate_links(self):
        soup = self.pp136_html(self.get_html())
        update_text = soup.find("b", text="街拍图片更新")

        if update_text:
            update_link = update_text.find_parent("table")
            if update_link:
                update_links = update_link.find_all("a", target="_blank")
                if update_links:
                    links = []
                    for link in update_links:
                        links.append({"link": link["href"], "title": link.text})
                    return links
        return None


    # 可以免费的下载的链接
    def get_all_links(self):
        links = self.get_menus()
        if links:
            urls = []
            for link in links:
                text = link['text']
                if text.find("首页") < 0 and text.upper().find("VIP") < 0:
                    urls.append(link)
            return urls
        return None

    # 路径，网页的名字
    def path(self):
        return "PP136网站"




# 详情页面
class page_detail(base_page):
    __title = ""

    def __init__(self, url):
        self.set_url(url)

    # 获取页面的所有可以下载的链接
    def get_all_res(self):
        soup = self.pp136_html(self.get_html())

        res = soup.find_all("img")
        if res:
            images = []
            for image in res:
                images.append({"img": self.adjust_url(image["src"])})
            return images
        return None

    # 下一页的链接
    def next_page(self):
        soup = self.pp136_html(self.get_html())

        next_page = soup.find("a", text="下一页")
        if next_page:
            return {"link": self.adjust_url(next_page["href"]), "title": next_page.text}


    def adjust_url(self, url = ""):
        if url.find("http") < 0:
            return self.get_parent() +'/'+ url
        return url


    # 路径
    def path(self):
        if "" == self.__title:
            soup = self.pp136_html(self.get_html())
            self.__title = soup.title.text
        return self.__title