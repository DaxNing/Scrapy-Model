#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import time
import random

class mySpider(scrapy.Spider):

    name = "tempo"

    # allowed_domains = ["tempo.com"]
    start_urls=['https://bisnis.tempo.co/read/1232248/mandiri-tebar-inspirasi-wirausaha-ke-generasi-muda']
    i=1


    original_url = start_urls[0]
    def parse(self,response):
        dic = {}
        title_list = response.xpath("/html[@id='tempoco-2017']/body/div[@class='container']/main[@id='detail']/div[@class='container-desktop']/section[@id='article']/div[@class='col w-70']/div[@class='wrapper']/article/h1//text()").extract()
        if len(title_list)!= 0:
            title =title_list[0].strip().replace("\n","")

        else:
            title = "No Title!"
        print(title)

        content_list = []
        k = 1
        while True:
            content_xpath = "/html[@id='tempoco-2017']/body/div[@class='container']/main[@id='detail']/div[@class='container-desktop']/section[@id='article']/div[@class='col w-70']/div[@class='wrapper']/article/div[@id='isi']/p[" + str(
                k) + "]//text()"
            con = response.xpath(content_xpath).extract()
            if len(con) != 0:
                content_list.append(con[0])
            else:
                break
            k += 1
        if len(content_list) != 0:
            content_list = [item.strip() for item in content_list]
            content_ = " ".join(content_list)
            content = content_.replace("\n", "")
            content = content.encode(encoding="utf-8")
        else:
            content = "No Content!"

        print(self.i)
        dic["item_id"]=self.i
        dic["title"]=title
        dic["content"]=content
        dic["original_url"]=self.original_url
        self.i+=1
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_tempo.txt","ab") as f:
            json.dump(dic,f)
            f.write("\n")

        j = random.randint(1, 4) #随机选取下一爬取文章链接
        next_page = response.xpath("/html[@id='tempoco-2017']/body/div[@class='container']/main[@id='detail']/div[@class='container-desktop']/section[@id='article']/div[@class='col w-70']/div[@class='wrapper']/section[@id='section-3']/div[@class='wrapper clearfix'][1]/div[@id='terkait']/div[@class='wrapper']/li["+str(j)+"]/div[@class='card card-type-1']/div[@class='wrapper clearfix']/a[@class='col'][2]/@href").extract()[0]
        self.original_url = next_page
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
