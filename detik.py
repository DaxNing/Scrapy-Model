#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import datetime
import re
import logging
import time
import random

class mySpider(scrapy.Spider):

    name = "detik"

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'CONCURRENT_REQUESTS_PER_IP': 0
    }

    start_date ='04/22/2017'

    # allowed_domains = ["detik.com"]
    start_urls=['https://news.detik.com/indeks/berita/1?date='+start_date]

    def get_before(self,date):
        date_list = date.split("/")
        now = date_list[2]+'-'+date_list[0]+'-'+date_list[1]
        print(now)
        d = datetime.datetime.strptime(now, '%Y-%m-%d')
        before = d + datetime.timedelta(days=-1)
        before = before.strftime('%m/%d/%Y')
        print(before)
        return before

    now = start_date
    i = 22978
    k = 2

    def parse(self,response):
        s=1
        while s<=20:

            url_xpath='//*[@id="indeks-container"]/li['+str(s)+']/article/div/a/@href'
            url_list=response.xpath(url_xpath).extract()
            if len(url_list)!=0:
                yield scrapy.Request(response.urljoin(url_list[0].encode("utf-8")),callback=self.choose_content)
                s += 1
            else:
                break
        logging.info("There are %d news in page %d" % ( s-1,self.k))

        if s == 1:  # 说明这页完全没有内容 or 不存在，跳转日期 #设置终止时间
            self.now = self.get_before(self.now)
            print("skipping date:%s" % (self.now))
            with open("C:/Users/86135/Desktop/Spider_works/id_articles_from_detik_day.txt", "a") as o:
                o.write("skipping date: "+self.now+"\n")
            self.k = 1

        if self.now != "01/01/2017":
            next_page = "https://news.detik.com/indeks/berita/"+str(self.k)+"?date="+self.now
            self.k += 1
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def choose_content(self,response):
        dic = {}
        title_list = response.xpath( "/html/body/div[@class='container']/div[@class='content']/div[@class='detail_content']/article/div[@class='jdl']/h1//text()").extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")

        else:
            title = "No Title!"
            logging.warning("No title,it's url :%s" % response.url)

        content_list = response.xpath(
            "/html/body/div[@class='container']/div[@class='content']/div[@class='detail_content']/article/div[@class='detail_wrap']/div[@id='detikdetailtext']//text()").extract()
        if len(content_list) != 0:
            content_list = [item.strip() for item in content_list]
            content_ = " ".join(content_list)

            content = content_.replace("\n", "").replace("\t", "").encode("utf-8")
            content = re.sub(r"googletag\.cmd\.push\(function\(\) { googletag\.display\('div-gpt-ad-1565706950874-0'\)" , "", content )
        else:
            content = "No Content!"
            logging.warning("No content,it's url :%s" % response.url)

        print(self.i)
        dic["item_id"] = self.i
        dic["title"] = title
        dic["content"] = content
        dic["original_url"] = response.url
        self.i += 1
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_detik_4.txt", "ab") as f:
            json.dump(dic, f)
            f.write("\n")




