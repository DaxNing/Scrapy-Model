#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import datetime
import re


class mySpider(scrapy.Spider):

    name = "jpnn"

    start_date = '2019/08/19'
    # allowed_domains = ["jpnn.com"]
    start_urls = ['https://www.jpnn.com/indeks?id=&d=19&m=08&y=2019&tab=all']

    i = 1  # item-id
    page = 0  # 页数
    now = start_date


    def get_before(self,date):
        date_list = date.split("/")
        now = date_list[0]+'-'+date_list[1]+'-'+date_list[2]
        print(now)
        d = datetime.datetime.strptime(now, '%Y-%m-%d')
        before = d + datetime.timedelta(days=-1)
        before = before.strftime('%Y/%m/%d')
        print(before)
        return before


    def choose_content(self,response):
        dic = {}
        title_list = response.xpath('//*[@id="content-utama"]/div[1]/div/h1//text()').extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")

        else:
            title = "No Title!"

        print(title)
        content_list = []
        n = 1
        flag = 0
        while n <= 10:
            content_xpath = '//*[@id="konten-artikel"]/div[2]/p[' + str(n) + ']//text()'
            con = response.xpath(content_xpath).extract()
            if len(con) != 0:
                if re.match("BACA JUGA", con[0]) == None:
                    content_list.append(con[0])
                n += 1
            elif n == 1:  # 由于有的文章第一段没内容
                n += 1
                continue
            else:   # 连续两段没有内容退出，排除某一段是图片的情况
                if flag == 1:
                    break
                else:
                    flag = 1
                    n += 1
                    continue

        if len(content_list) != 0:
            content_list = [item.strip() for item in content_list]
            content_ = " ".join(content_list)
            content = content_.replace("\n", "").replace("\t", "")
            content = content.encode(encoding="utf-8")
        else:
            content = "No Content!"

        print(self.i)
        dic["item_id"] = self.i
        dic["title"] = title
        dic["content"] = content
        dic["original_url"] = response.url
        self.i += 1
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_jpnn.txt", "ab") as f:
            json.dump(dic, f)
            f.write('\n')

    def choose_date(self):
        self.now = self.get_before(self.now)
        print("skipping date:%s" % (self.now))
        with open("C:/Users/86135/Desktop/Spider_works/id_articles_from_jpnn_day.txt", "a") as o:
            o.write("skipping date: " + self.now + "\n")
        self.page = 0

    def parse(self, response):

        par = 1
        if self.page == 0:
            while True:
                url_xpath ='//*[@id="content-utama"]/div[1]/div[3]/div[2]/div[3]/ul/li[' + str(par) + ']/a/@href'
                url_list = response.xpath(url_xpath).extract()
                print(url_list)
                if len(url_list) != 0:
                    yield scrapy.Request(response.urljoin(url_list[0]),
                                         callback=self.choose_content)
                    par += 1
                else:
                    break
        else:
            url_xpath = '//a/@href'
            url_list = response.xpath(url_xpath).extract()
            while par < len(url_list):
                yield scrapy.Request(response.urljoin(url_list[par]),
                                     callback=self.choose_content)
                par += 1

        if par != 1:   # 判断页面有没有内容
            date_list = self.now.split("/")
            print(date_list[0], date_list[1], date_list[2])
            self.page += 10
            print(self.page)
            yield scrapy.FormRequest(
                url='https://www.jpnn.com/ajax/loadmore_indeks',
                formdata={"offset": str(self.page),
                          "id": "",
                          "tab": "all",
                          "d": date_list[2],
                          "m": date_list[1],
                          "y": date_list[0]},
                callback=self.parse
            )

        else:
            if self.now != '2019/08/01':
                self.choose_date()
                date_list = self.now.split("/")
                changed_url = "https://www.jpnn.com/indeks?id=&d="+date_list[2]+"&m="+date_list[1]+"&y="+date_list[0]+"&tab=all"
                next_page = response.urljoin(changed_url)
                yield scrapy.Request(url=next_page, callback=self.parse)