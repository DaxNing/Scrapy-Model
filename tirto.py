#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import time
import random

class mySpider(scrapy.Spider):

    name = "tirto"
    start_urls = ['https://tirto.id/mildreport']

    i = 1
    k = 2


    def parse(self, response):

        s = 1
        while True:

            url_xpath = '//*[@id="__layout"]/div/div[4]/div/div[2]/div[3]/div['+str(s)+']/div/a/@href'
            url_list = response.xpath(url_xpath).extract()
            print(url_list)
            if len(url_list) != 0:
                yield scrapy.Request(response.urljoin("https://tirto.id"+url_list[0].encode("utf-8")), callback=self.choose_content)
                s += 1
            else:
                break


        next_page = "https://tirto.id/mildreport/"+str(self.k)
        self.k += 1
        if self.k <= 396:
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def choose_content(self, response):
        dic = {}
        title_list = response.xpath('//*[@id="__layout"]/div/div[3]/div[3]/div/div[2]/div/div[2]/div[1]/h1//text()').extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")
            print(title)

        else:
            title = "No Title!"

        content_list = response.xpath('//*[@id="__layout"]/div/div[3]/div[3]/div/div[2]/div/div[2]/div[3]/div[5]//text()').extract()
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
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_tirto.txt", "ab") as f:
            json.dump(dic, f)
            f.write("\n")