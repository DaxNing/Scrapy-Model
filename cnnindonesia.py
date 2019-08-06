#user/bin/python
#_*_ coding:UTF-8 _*_

import scrapy
import io
import json
import time
import random

class Detick(scrapy.Spider):

    name = "cnnindonesia"

    allowed_domains = ["cnnindonesia.com"] #抓取限制范围
    start_urls=['https://www.cnnindonesia.com/gaya-hidup/20190726120843-255-415709/serba-serbi-air-mani-dan-aromanya'] 
    i=1  


    original_url = start_urls[0]
    def parse(self,response):
        dic = {}
        title_list = response.xpath("/html/body/section[@id='content']/div[@class='container']/div[@class='l_content']/div[@class='content_detail']/h1[@class='title']//text()").extract()
        if len(title_list)!= 0:
            title =title_list[0].strip().replace("\n","")
            print(title)

        else:
            title = "No Title!"
           
        content_list = response.xpath("/html/body/section[@id='content']/div[@class='container']/div[@class='l_content']/div[@class='content_detail']/div[@class='detail_wrap']/div[@id='detikdetailtext']//text()").extract()
        if len(content_list)!= 0:
            content_list = [item.strip() for item in content_list] 
            content_ =" ".join(content_list)        #对文章内容处理后合并
            content =content_.replace("\n","").encode("utf-8")
            
        else:
            content = "No Content!"
            
        print(self.i)
        dic["item_id"]=self.i
        dic["title"]=title
        dic["content"]=content
        dic["original_url"]=self.original_url
        self.i+=1
        with io.open("C:/Users/86135/Desktop/Spider_works/id_articles_from_cnnidonesia_4.txt","ab") as f:
            json.dump(dic,f)
            f.write("\n")
        j=random.randint(1,6)
        next_page = response.xpath("/html/body/section[@id='content']/div[@class='container']/div[@class='l_content']/div[@class='box mb20']/div[@class='grid_row inline gap list media_rows']/article[@class='col_6']["+str(j)+"]/a/@href").extract()[0]
        self.original_url=next_page
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)    #跳转，dont_filter参数置为True可以使爬虫爬取重复网页
