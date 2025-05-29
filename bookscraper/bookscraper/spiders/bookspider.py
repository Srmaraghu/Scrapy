import scrapy
from bookscraper.items import BookItem 
import random

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        'FEEDS': #overrides FEEDS in settings.py
        {
            'books2data.json':{'format':'json','overwrite':True}   ,
        }
    }

    def parse(self, response):
        #get all books  
        books = response.css('article.product_pod')

        for book in books:
            new_book_url = response.css('h3 a::attr(href)').get()
            if 'catalogue/' in new_book_url:
                book_url = 'https://books.toscrape.com/'+ new_book_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/'+ new_book_url


            yield response.follow(book_url,callback= self.parse_book_page)
            
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/'+ next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/'+ next_page
            
            yield response.follow(next_page_url, callback=self.parse)



    def parse_book_page(self,response):
        item = BookItem()


        item['url'] = response.url
        item['title'] = response.css('.product_main h1::text').get()
        item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        item['stars'] = response.css('p.star-rating').attrib['class']


         # Extract values from table
        table_data = {
            row.css('th::text').get(): row.css('td::text').get()
            for row in response.css('table tr')
        }

        item['product_type'] = table_data.get('Product Type')
        item['price_excl_tax'] = table_data.get('Price (excl. tax)')
        item['price_incl_tax'] = table_data.get('Price (incl. tax)')
        item['tax'] = table_data.get('Tax')
        item['availability'] = table_data.get('Availability')
        item['number_of_reviews'] = table_data.get('Number of reviews')


        yield item





# //ul[@class='breadcrumb']
#  here // means: search anywhere in the document.
# ul[@class='breadcrumb'] means: find a <ul> tag with the class "breadcrumb".

# /li[@class='active']
# Inside that <ul>, find an <li> that has the class active.

# /preceding-sibling::li[1]
#This moves backward to the previous <li> element that is a sibling of the current one.

# preceding-sibling:: is an axis in XPath. It finds earlier siblings (i.e. elements that share the same parent).

# li[1] means: select the closest (immediately preceding) <li>.


# xpath_expr = "//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()"
# response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()


#scrapy shell









# scrapy genspider bookspider books.to.scrape