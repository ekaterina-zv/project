import scrapy
import time
import re
import json

class QuoteSpider(scrapy.Spider):
    name = 'quote'
    allowed_domains = ['sitilink.ru']
    start_urls = ["http://www.citilink.ru/catalog/feny/"]
    
    def parse(self, response):
        urls_pages = response.css('div.PaginationWidget__wrapper-pagination > a::attr(href)').extract()
        urls_pages.insert(0,response.url)
        urls_pages_new =[]
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url_page in urls_pages:
            if url_page not in urls_pages_new:
                urls_pages_new.append(url_page)
                url_page = response.urljoin(url_page)
                print(url_page)
                yield scrapy.Request(url = url_page,callback=self.parse_page, dont_filter=True, headers=headers)
        
        #follow pagination link
        #next_page_url = response.css('div.PaginationWidget__wrapper-pagination > a::attr(href)').extract_first()
        #if next_page_url:
            #next_page_url=response.urljoin(next_page_url)
            #print(next_page_url)
            #yield scrapy.Request(url = next_page_url,callback=self.parse, dont_filter=True)
    def parse_page(self, response):
        urls_links_new =[]
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        urls_links = response.css('div.product_data__gtm-js.product_data__pageevents-js.ProductCardHorizontal.js--ProductCardInListing.js--ProductCardInWishlist > div > a::attr(href)').extract()
        for url_link in urls_links:
            if url_link not in urls_links_new:
                urls_links_new.append(url_link)
                url_link = response.urljoin(url_link)
                yield scrapy.Request(url = url_link,callback=self.parse_details, dont_filter=True, headers=headers)
                time.sleep(1)
    def parse_details(self, response):
        Item = {}
        sect = []
        stock = True
        price_data={}
        str_ = response.css('div.ProductHeader__product-id::text').extract_first()
        rpc = re.findall(r'\d+',str_)
        Item['RPC'] = rpc
        Item['URL'] = response.url
        Item['title'] = response.css('h1.Heading.Heading_level_1.ProductHeader__title::text').extract_first()
        #Item['brend'] = response.css('span.name::text').extract_first()
        for quote in response.css('div.Breadcrumbs'):
            sect.append(quote.css('span::text').get())
        Item['section'] = sect
        
        orig = response.css('span.ProductHeader__price-old_current-price::text').extract_first()
        if orig:
            o = re.findall(r'\d+',orig)
            original = o[0]
            curr = response.css('span.ProductHeader__price-default_current-price::text').extract_first()
            c = re.findall(r'\d+',curr)
            current = c[0]
            price_data['current'] = float(current)
            sale = int((float(original)-float(current))/float(original)* 100)
            price_data['sale'] = "Скидка: " + str(sale) +"%"
            price_data['original'] = float(original)
        elif orig == []:
            curr = response.css('span.ProductHeader__price-default_current-price::text').extract_first()
            c = re.findall(r'\d+',curr)
            current = c[0]
            price_data['current'] = float(current)
            price_data['sale'] = 0.0
            price_data['original'] = price_data['current']
        
        st = response.css('ProductHeader__not-available-header').extract_first()
        if st:
            stock = False
        Item['stock'] = stock
        #print(Item)
        """
        with open("data_file.json", "w") as write_file:
            json.dump(Item, write_file)
        """