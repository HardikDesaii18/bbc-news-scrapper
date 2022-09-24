import requests
from bs4 import BeautifulSoup as bs
import re
import datetime
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-west-2',
)

news_data_table = dynamodb.Table('bbcnews')

sport_news_by_category = [
    'https://www.bbc.com/sport/golf/',
    'https://www.bbc.com/sport/tennis/',
    'https://www.bbc.com/sport/cricket/',
    'https://www.bbc.com/sport/football/'
]

general_news_by_category = [
    'https://www.bbc.com/news/business/',
    'https://www.bbc.com/news/world/',
    'https://www.bbc.com/news/uk/',
    'https://www.bbc.com/news/coronavirus/'

]


def insert_data_into_table(value_dict):
    article_id = value_dict['id']

    # check if the article exists in the Table, if yes, there is no need to reInsert the data
    query_response = news_data_table.query(
        KeyConditionExpression=Key('id').eq(article_id)
    )

    if ('Items' not in query_response) or ('Items' in query_response and len(query_response['Items']) == 0):
        news_data_table.put_item(Item=value_dict)
        # print("Inserted the record - {}".format(article_id))


def read_article_by_id(article_dict, article_category="sport", article_sub_category="general",
                       sub_class_name="data-reactid"):
    for url in article_dict.keys():

        article_title = str("""{}""".format(article_dict[url])).replace('"', '').replace("'", "")
        url_details = url.split("/")
        article_id = None
        article_content = ""

        article = requests.get(url)
        soup = bs(article.content, 'html.parser')

        if article_category == "sport":
            article_id = url_details[-1]

            for i in soup.select('p', {"id": sub_class_name}):

                if ('paragraph' in str(i)):
                    # print(i.text)
                    article_content += i.text

        if article_category == "news":
            article_id = str(url_details[-1]).split('-')[-1]

            for i in soup.select('p', {"id": "class"}):
                # print(i.text)
                article_content += i.text

        article_key = "{}_{}_{}".format(article_category, article_sub_category, article_id)

        insert_data_into_table(
            dict(
                id=article_key,
                category=article_category,
                subcategory=article_sub_category,
                title=article_title,
                content=article_content,
                date=str(datetime.datetime.now())[:10]
            )
        )


def get_news_articles(category_link, article_cateogry="sport", article_sub_category="general", class_name="gs-c-promo"):
    article_dict = dict()

    try:
        article = requests.get(category_link)
        soup = bs(article.content, 'html.parser')

        if article_cateogry == "sport":

            for i in soup.findAll('div', {"class": class_name}):
                name_key = ''
                value_link = ''

                if (category_link in str(i)):
                    pattern = category_link + '(.+?)"'
                    m = re.findall(pattern, str(i))
                    name_key = ''.join(re.findall(r'data-bbc-title=(.+?)"', str(i)))
                    value_link = category_link + ''.join(m)
                    article_dict[value_link] = name_key

            read_article_by_id(article_dict, article_cateogry, article_sub_category, "data-reactid")

        if article_cateogry == "news":
            for i in soup.findAll('a'):
                if (class_name in str(i) and "href" in str(i)):
                    title = i.select("h3")[0].text
                    name_key = i['href']

                    if name_key[:4] != "http":
                        updated_name_key = 'https://www.bbc.com' + name_key
                        article_dict[updated_name_key] = title

            read_article_by_id(article_dict, article_cateogry, article_sub_category,  "class")

    except Exception as ex:
        print("Following error occurred while scraping the News Article - {}".format(category_link))
        print(str(ex))


if __name__ == "__main__":

    # Get the Sports article
    for article_link in sport_news_by_category:
        sub_category = article_link.split("/")[-2]
        get_news_articles(
            article_link,
            "sport",
            sub_category,
            "gs-c-promo"
        )

    # Get the news articles

    for article_link in general_news_by_category:
        sub_category = article_link.split("/")[-2]

        get_news_articles(
            article_link,
            "news",
            sub_category,
            "gs-c-promo"
        )
