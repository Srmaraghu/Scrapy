# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
from dotenv import load_dotenv
import os


load_dotenv()

class BookscraperPipeline:
    def process_item(self, item, spider):
        

        adapter = ItemAdapter(item)

        #strip all whitespaces from strings
        field_names= adapter.field_names()
        for field_name in field_names:
            if field_name !='description':
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        #category and product type convert to lowercase
        lowercase_keys = ['category','product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()


        # Convert price fields to float
        price_keys = ['price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            if value is not None:
                try:
                    clean_value = value.replace('£', '')
                    adapter[price_key] = float(clean_value)
                except ValueError:
                    spider.logger.warning(f"Failed to convert {price_key} with value: {value}")
                    adapter[price_key] = None
            else:
                adapter[price_key] = None
                


        
        ##reviews convert string to num
        reviews_string = adapter.get('number_of_reviews')
        adapter['number_of_reviews'] = int(reviews_string)

        ##Stars -> convert text tO number
        stars_string = adapter.get('stars') #star-rating Three
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1].lower

        if stars_text_value == "zero":
            adapter['stars'] = 0
        elif stars_text_value == "One":
            adapter['stars'] = 1
        elif stars_text_value == "Two":
            adapter['stars'] = 2
        elif stars_text_value == "Three":
            adapter['stars'] = 3
        elif stars_text_value == "Four":
            adapter['stars'] = 4
        elif stars_text_value == "Five":
            adapter['stars'] = 5


        return item


class SaveToMySql:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
            )

        self.cur = self.conn.cursor()

         # Create table if it doesn't exist
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url TEXT,
                title VARCHAR(255),
                description TEXT,
                category VARCHAR(100),
                stars VARCHAR(50),
                product_type VARCHAR(100),
                price_excl_tax VARCHAR(20),
                price_incl_tax VARCHAR(20),
                tax VARCHAR(20),
                availability VARCHAR(100),
                number_of_reviews INT
            )
        """)
        self.conn.commit()

    

    def process_item(self, item, spider):
        self.cur.execute("""
            INSERT INTO books (
                url, title, description, category, stars,
                product_type, price_excl_tax, price_incl_tax,
                tax, availability, number_of_reviews
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            item.get('url'),
            item.get('title'),
            item.get('description'),
            item.get('category'),
            item.get('stars'),
            item.get('product_type'),
            item.get('price_excl_tax'),
            item.get('price_incl_tax'),
            item.get('tax'),
            item.get('availability'),
            int(item.get('number_of_reviews') or 0)
        ))

        self.conn.commit()
        return item


    def close_spider(self,spider):
        self.cur.close()
        self.conn.close()