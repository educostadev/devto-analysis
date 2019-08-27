import json
import requests
import re
import pymongo
import datetime
import pandas as pd
import sys
from openpyxl.workbook import Workbook


class MondoDB(object):
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

    # Due a limitation on the backend you can not request more que 1000 articles.
    def scrape(self, tag, articlesVisited={}, tagsVisited=[]):
        if (tag not in tagsVisited):
            articles = self.get_articles(tag, maxArticlesPerRequest=1000)
            tagsVisited.append(tag)
            for article in articles:
                if article['id'] not in articlesVisited:
                    articlesVisited[article['id']] = article
                    for tag in article['tag_list']:
                        self.scrape(tag, articlesVisited, tagsVisited)

    def export_to_csv(self, articles, prefix):
        df = pd.DataFrame(articles)
        filename = "{0}_{1}.xlsx".format(
            datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
            prefix
        )
        print("Writting "+filename)
        df.to_excel(filename, sheet_name=prefix)

    def get_articles(self, tag, maxArticlesPerRequest=1, page=0):
        articles = []
        try:
            main_request_json = self.do_request(
                maxArticlesPerRequest, page, tag)
            articles.extend(main_request_json['hits'])
            # Remove articles with not enough data
            for article in list(articles):
                if self.isInValid(article):
                    articles.remove(article)
            print("{0};{1}".format(len(articles), tag))
            return self.enrich_data(articles)
        except:
            print("Error")
        return articles

    def isInValid(self, article):
        return 'published_at_int' not in article or 'id' not in article

    def enrich_data(self, articles):
        for i in range(0, len(articles)):
            article = articles[i]
            newfields_dict = {}
            published_at_int = article['published_at_int']
            readable_published_at = datetime.datetime.fromtimestamp(
                published_at_int).strftime("%Y/%m/%d %H:%M:%S")
            newfields_dict['readable_published_at'] = readable_published_at
            dicts_merged = {**newfields_dict, **article}
            articles[i] = dicts_merged
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
    sys.setrecursionlimit(50000)  # increase recursion depth
    scraper = Scraper()
    tag = 'Java'
    articlesVisited = {}
    tagsVisited = []
    scraper.scrape(tag, articlesVisited, tagsVisited)
    scraper.export_to_csv(list(articlesVisited.values()), "dataset")
    print("{0} articles read for tags {1}".format(
        len(articlesVisited), tagsVisited))
    print("Finished!")
