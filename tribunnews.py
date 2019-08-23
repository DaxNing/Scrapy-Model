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

    name = "tribunnews"

    start_date = '2019-08-12'
    # allowed_domains = ["tribunnews.com"]
    start_urls = ['https://www.tribunnews.com/index-news?date='+start_date]



    def get_before(self,date):
        d = datetime.datetime.strptime(date, '%Y-%m-%d')
        before = d + datetime.timedelta(days=-1)
        before = before.strftime('%Y-%m-%d')
        print(before)
        return before


    i = 1
    k = 2  #页数

    now = start_date
    def parse(self,response):

        s = 1
        while True:

            url_xpath = '/html/body/div[4]/div[4]/div[1]/div/div[2]/div[2]/ul/li['+str(s)+']/h3/a/@href'
            url_list = response.xpath(url_xpath).extract()
            print(url_list)
            if len(url_list) != 0:
                yield scrapy.Request(response.urljoin(url_list[0].encode("utf-8")),callback=self.choose_content)
                s += 1
            else:
                break

        if s == 1 :  # 说明这页完全没有内容 or 不存在，跳转日期
            self.now = self.get_before(self.now)
            print("skipping date:%s" % (self.now))
            with open("C:/Users/86135/Desktop/Spider_works/id_articles_from_tribunnews_day.txt", "a") as o:
                o.write("skipping date: " + self.now + "\n")
            self.k = 1

        if self.now != "2017-01-01":#设置终止时间
            next_page = "https://www.tribunnews.com/index-news?date="+self.now+"&page="+str(self.k)
            print(next_page)
            self.k += 1
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def choose_content(self,response):
        dic = {}
        title_list = response.xpath('//*[@id="arttitle"]//text()').extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")
        else:
            title = "No Title!"

        content_list = []
        n = 1
        while True:
            content_xpath = '//*[@id="article_con"]/div[3]/p['+str(n)+']//text()'
            con = response.xpath(content_xpath).extract()
            if len(con) != 0:
                if re.match('Baca juga:',con[0]) == None:
                    content_list.append(con[0])
                n += 1
            elif n == 1:#由于有的文章第一段没内容
                n += 1
                continue
            else :
                break

        if len(content_list) != 0:
            content_list = [item.strip() for item in content_list]
            content_ = " ".join(content_list)
            content = content_.replace("\n", "")
            content = content.encode(encoding="utf-8")
        else:
            content = "No Content!"


        print(self.i)
        dic["item_id"] = self.i
        dic["title"] = title
        dic["content"] = content
        dic["original_url"] = response.url
        self.i += 1
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_tribunnews.txt", "ab") as f:
            json.dump(dic, f)
            f.write("\n")

