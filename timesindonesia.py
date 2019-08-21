#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import datetime
import time
import random

class mySpider(scrapy.Spider):

    name = "timesindonesia"

    start_date = '2019/08/12'
    # allowed_domains = ["timesindonesia.com"]
    start_urls = ['https://www.timesindonesia.co.id/indeks/'+start_date]

    i = 1  # item-id
    page = 2  # 页数
    par = 1  # 段落
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


    def choose_url(self,response):
        print(response.status)
        if response.status != 500:
            while True:
                url_xpath = '//*[@id="results"]/article['+str(self.par)+']'
                url_list = response.xpath(url_xpath).extract()
                print(url_list)
                if len(url_list) != 0:
                    yield scrapy.Request(response.urljoin('https://www.timesindonesia.co.id' + url_list[0].encode("utf-8")),
                                         callback=self.choose_content)
                    self.par += 1
                else:
                    date_list = self.now.split("/")
                    print(date_list[0],date_list[1],date_list[2])
                    self.page += 1
                    yield scrapy.FormRequest(
                        url='https://www.timesindonesia.co.id/data/indeks.list.php',
                        formdata={"page": str(self.page), "in_years": date_list[0], "in_month": date_list[1],
                                  "in_date": date_list[2]},
                        callback=self.choose_url
                    )
                    break


    def choose_content(self,response):
        dic = {}
        title_list = response.xpath(
            "/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/div/div/article/h1//text()").extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")
            print(title)

        else:
            title = "No Title!"

        print(title)
        content_list = []
        n = 1
        flag = 0
        while n <= 10:
            content_xpath = '//*[@id="other_news"]/p[' + str(n) + ']//text()'
            con = response.xpath(content_xpath).extract()
            if len(con) != 0:
                content_list.append(con[0])
                n += 1
            elif n == 1:  # 由于有的文章第一段没内容
                n += 1
                continue
            else:   # 连续两段没有内容退出，排除某一段是图片的情况
                if flag == 1:
                    break
                else :
                    flag =1
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
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_timesindonesia.txt", "ab") as f:
            json.dump(dic, f)
            f.write('\n')

    def choose_date(self):
        self.now = self.get_before(self.now)
        print("skipping date:%s" % (self.now))
        with open("C:/Users/86135/Desktop/Spider_works/id_articles_from_timesindonesia_day.txt", "a") as o:
            o.write("skipping date: " + self.now + "\n")
        self.page = 2

    def parse(self, response):
        print(response.url)
        yield scrapy.Request(url=response.url, callback=self.choose_url)
        self.par = 1
        if self.now != '2019/08/01':
            self.choose_date()
            changed_url = 'https://www.timesindonesia.co.id/indeks/'+self.now
            next_page = response.urljoin(changed_url)
            yield scrapy.Request(url=next_page, callback=self.parse)