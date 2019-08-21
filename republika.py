#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import datetime
import re
import time
import random

class mySpider(scrapy.Spider):

    name = "republika"

    start_date = '2019/08/20'
    # allowed_domains = ["republika.co.id.com"]
    start_urls = ['https://www.republika.co.id/index/'+start_date]



    def get_before(self,date):
        date_list = date.split("/")
        now = date_list[0]+'-'+date_list[1]+'-'+date_list[2]
        print(now)
        d = datetime.datetime.strptime(now, '%Y-%m-%d')
        before = d + datetime.timedelta(days=-1)
        before = before.strftime('%Y/%m/%d')
        print(before)
        return before


    id = 1
    page = 40

    now = start_date
    def parse(self, response):

        par = 3
        while True:

            url_xpath = '//*[@id="wrapper"]/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[2]//div['+str(par)+']//a/@href'
            url_list = response.xpath(url_xpath).extract()
            if par == 3 and len(url_list) == 2:
                break

            if len(url_list) != 0:
                yield scrapy.Request(response.urljoin(url_list[0].encode("utf-8")), callback=self.choose_content)
                par += 1
            else:
                break

        if par == 3:  # 说明这页完全没有内容 or 不存在，跳转日
            self.now = self.get_before(self.now)
            print("skipping date:%s" % self.now)
            with open("C:/Users/86135/Desktop/Spider_works/id_articles_from_republika_day.txt", "a") as o:
                o.write("skipping date: " + self.now + "\n")
            self.page = 0

        if self.now != "2017/01/01": #设置终止时间
            next_page = "https://republika.co.id/index/" + self.now + '/' + str(self.page)
            self.page += 40
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def choose_content(self,response):
        dic = {}
        title_list = response.xpath(
            '//*[@id="wrapper"]/div[2]/div[1]/div[2]/div[1]/div/div[1]/h1//text()').extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")
        else:
            title = "No Title!"


        content_list = []
        n = 1
        flag = 0
        while True :
            content_xpath = '//*[@id="wrapper"]/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div[3]/div/p['+str(n)+']//text()'
            con = response.xpath(content_xpath).extract()
            if len(con) != 0:
                if re.match("BACA JUGA", con[0]) == None and re.match("Baca Juga",con[0]) == None and re.match("Baca juga",con[0]) == None:
                    content_list.append(con[0])
                flag = 0
                n += 1
            else:   # 连续两段没有内容退出，排除某一段是图片的情况和两段是空白的情况
                if flag == 2:
                    break
                else:
                    flag += 1
                    n += 1
                    continue

        if len(content_list) != 0:
            content_list = [item.strip() for item in content_list]
            content_ = " ".join(content_list)
            content = content_.replace("\n", "").replace("\t", "")
            content = content.encode(encoding="utf-8")
        else:
            content = "No Content!"

        print(self.id)
        dic["item_id"] = self.id
        dic["title"] = title
        dic["content"] = content
        dic["original_url"] = response.url
        self.id += 1
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_republika.txt", "ab") as f:
            json.dump(dic, f)
            f.write("\n")

