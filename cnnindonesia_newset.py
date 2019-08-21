#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import datetime
import time
import random

class mySpider(scrapy.Spider):

    name = "cnnindonesia_url"

    start_date = '2018/11/01'
    # allowed_domains = ["cnnindonesia.com"]
    start_urls=['https://www.cnnindonesia.com/indeks?date='+start_date+'&p=1&date='+start_date+'&kanal=2']



    def get_before(self,date):
        date_list = date.split("/")
        now = date_list[0]+'-'+date_list[1]+'-'+date_list[2]
        print(now)
        d = datetime.datetime.strptime(now, '%Y-%m-%d')
        before = d + datetime.timedelta(days=-1)
        before = before.strftime('%Y/%m/%d')
        print(before)
        return before


    i=1
    k=2

    now = start_date
    def parse(self,response):

        s=1
        while True:

            url_xpath='//*[@id="content"]/div/div[4]/div/div[1]/article['+ str(s) +']/a/@href'
            url_list=response.xpath(url_xpath).extract()
            print(url_list)
            if len(url_list)!=0:
                yield scrapy.Request(response.urljoin(url_list[0].encode("utf-8")),callback=self.choose_content)
                s+=1
            else:
                break

        if s == 1:  # 说明这页完全没有内容 or 不存在，跳转日
            self.now = self.get_before(self.now)
            print("skipping date:%s" % (self.now))
            with open("C:/Users/86135/Desktop/Spider_works/id_articles_from_lsscnnindonesia_day.txt", "a") as o:
                o.write("skipping date: " + self.now + "\n")
            self.k = 1

        if self.now != "2017/01/01": #设置终止时间
            next_page="https://www.cnnindonesia.com/indeks?date="+self.now+"&p="+str(self.k)+"&date="+self.now+"&kanal=2"
            self.k+=1
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def choose_content(self,response):
        dic = {}
        title_list = response.xpath(
            "/html/body/section[@id='content']/div[@class='container']/div[@class='l_content']/div[@class='content_detail']/h1[@class='title']//text()").extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")
            print(title)

        else:
            title = "No Title!"
        content_list = response.xpath(
            "/html/body/section[@id='content']/div[@class='container']/div[@class='l_content']/div[@class='content_detail']/div[@class='detail_wrap']/div[@id='detikdetailtext']//text()").extract()
        if len(content_list) != 0:
            content_list = [item.strip() for item in content_list]
            content_ = " ".join(content_list)
            content = content_.replace("\n", "").encode("utf-8")
        else:
            content = "No Content!"
        print(self.i)
        dic["item_id"] = self.i
        dic["title"] = title
        dic["content"] = content
        dic["original_url"] = response.url
        self.i += 1
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_newest_3.txt", "ab") as f:
            json.dump(dic, f)
            f.write("\n")

