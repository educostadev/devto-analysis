import json
import requests
import re
import pymongo


class Scraper(object):
    def __init__(self):
        self.url = 'https://ye5y9r600c-dsn.algolia.net/1/indexes/ordered_articles_production/query?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.20.3&x-algolia-application-id=YE5Y9R600C&x-algolia-api-key=YWVlZGM3YWI4NDg3Mjk1MzJmMjcwNDVjMjIwN2ZmZTQ4YTkxOGE0YTkwMzhiZTQzNmM0ZGFmYTE3ZTI1ZDFhNXJlc3RyaWN0SW5kaWNlcz1zZWFyY2hhYmxlc19wcm9kdWN0aW9uJTJDVGFnX3Byb2R1Y3Rpb24lMkNvcmRlcmVkX2FydGljbGVzX3Byb2R1Y3Rpb24lMkNDbGFzc2lmaWVkTGlzdGluZ19wcm9kdWN0aW9uJTJDb3JkZXJlZF9hcnRpY2xlc19ieV9wdWJsaXNoZWRfYXRfcHJvZHVjdGlvbiUyQ29yZGVyZWRfYXJ0aWNsZXNfYnlfcG9zaXRpdmVfcmVhY3Rpb25zX2NvdW50X3Byb2R1Y3Rpb24lMkNvcmRlcmVkX2NvbW1lbnRzX3Byb2R1Y3Rpb24%3D'
        self.payload = {
            'params': ''
        }
        self.payloadTemplate = {
            'params': 'query=*&hitsPerPage={0}&page={1}&attributesToHighlight=%5B%5D&tagFilters=%5B%22{2}%22%5D'
        }
        self.header = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'Referer': 'https://dev.to/'
        }

    '''
    Due a limitation on the backend you can not request more que 1000 articles. 
    '''
    def scrape(self, tag):
        articles = self.scrape_articles(tag, maxArticlesPerRequest=1000)

        #self.record_data_on_mongoDB(articles)
        self.export_data_to_csv(articles)

        print("Finished!")


    def export_data_to_csv(self, articles):
        for article in articles:
            print(article)

    def record_data_on_mongoDB(self, articles):
        mycol = self.connect_to_mongoDB()
        print("Recording on database...")
        for article in articles:
            x = mycol.insert_one(article)
            print(x.insert_one)

    def connect_to_mongoDB(self):
        myclient = pymongo.MongoClient(
            "mongodb://mongoadmin:mongopwd@localhost:27017/admin")
        mydb = myclient["devto"]
        mycol = mydb["articles"]
        return mycol

    def scrape_articles(self, tag, maxArticlesPerRequest=1, page=0):
        articles = []
        main_request_json = self.do_request(maxArticlesPerRequest, page, tag)
        articles.extend(main_request_json['hits'])
        print("{0} articles read".format(len(articles)))
        return articles

    def do_request(self, maxArticlesPerRequest, page, tag):
        self.payload['params'] = self.payloadTemplate['params'].format(
            maxArticlesPerRequest, page, tag)
        request = requests.post(
            url=self.url,
            data=json.dumps(self.payload),
            headers=self.header
        )

        main_request_json = json.loads(request.content)
        return main_request_json


if __name__ == '__main__':
    scraper = Scraper()
    tag = 'java'
    print("Reading articler from tag "+tag)
    scraper.scrape(tag)
