#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import re

class mySpider(scrapy.Spider):

    name = "suara"

    # allowed_domains = ["suara.com"]
    start_urls=['https://www.suara.com/indeks/terkini/all/2019?']


    item_id = 1
    page = 2

    def parse(self,response):

        piece = 1
        while True:
            url_xpath ='//*[@id="main-content"]/div[2]/div/ul/li['+str(piece)+']/div/div/div[2]/h4/a/@href'
            url_list = response.xpath(url_xpath).extract()
            print(url_list)
            if len(url_list) != 0:
                yield scrapy.Request(response.urljoin(url_list[0].encode("utf-8")), callback=self.choose_content)
                piece += 1
            else:
                break


        next_page = "https://www.suara.com/indeks/terkini/all/2019?page="+str(self.page)
        self.page += 1
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def choose_content(self, response):
        dic = {}
        title_list = response.xpath(
            '//*[@id="contentsWrapper"]/div[1]/header/div/div[1]/h1//text()').extract()
        if len(title_list) != 0:
            title = title_list[0].strip().replace("\n", "")
        else:
            title = "No Title!"


        if re.match(r"Berita Terpopuler Tekno",title) == None:  #排除多篇新闻整合的文章
            content_list = []
            para = 1
            flag = 0
            while True:
                content_xpath = '//*[@id="contentsWrapper"]/div[1]/article/p['+str(para)+']//text()'
                con = response.xpath(content_xpath).extract()
                if len(con) != 0:
                    if re.match("BACA JUGA", con[0]) == None and re.match("Baca Juga",con[0]) == None and re.match("Baca juga",con[0]) == None:
                        content_list.append(con[0])
                    para += 1
                    flag = 0
                else:
                    if flag != 2:   #排除图片或空白段嵌入的情况
                        para += 1
                        flag += 1
                        continue
                    else:
                        break

            if len(content_list) != 0:
                content_list = [item.strip() for item in content_list]
                content_ = " ".join(content_list)
                content = content_.replace("\n", "")
                content = content.encode(encoding="utf-8")
            else:
                content = "No Content!"


            print(self.item_id)
            dic["item_id"] = self.item_id
            dic["title"] = title
            dic["content"] = content
            dic["original_url"] = response.url
            self.item_id += 1
            with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_suara.txt", "ab") as f:
                json.dump(dic, f)
                f.write("\n")

