import requests
from bs4 import BeautifulSoup as bs
import re
import datetime
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-west-2',
    aws_access_key_id='AKIAX22ZAZD6KRJGIVVW',
    aws_secret_access_key='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'

)

news_data_table = dynamodb.Table('bbcnews')

sport_news_by_category = [
    'https://www.bbc.com/sport/golf/',
    'https://www.bbc.com/sport/tennis/',
    'https://www.bbc.com/sport/cricket/',
    'https://www.bbc.com/sport/football/'
]


def insert_data_into_table(value_dict):

    article_id = value_dict['id']

    # check if the article exists in the Table, if yes, there is no need to reInsert the data
    query_response = news_data_table.query(
        KeyConditionExpression=Key('id').eq(article_id)
    )

    if ('Items' not in query_response) or ('Items' in query_response and len(query_response['Items']) == 0):
        news_data_table.put_item(Item=value_dict)
        print("Inserted the record - {}".format(article_id))

    elif 'Items' in query_response and len(query_response['Items']) >= 1:
        print("Article {} already available in the table, skipping the data insertion".format(article_id))


def read_article_by_id(article_dict, sub_class_name="data-reactid"):

    for url in article_dict.keys():

        article_title = str("""{}""".format(article_dict[url])).replace('"', '').replace("'", "")

        url_details = url.split("/")

        article_id = url_details[-1]
        article_sub_category = url_details[-2]
        article_category = url_details[-3]

        article_content = ""
        article = requests.get(url)
        soup = bs(article.content, 'html.parser')
        for i in soup.select('p', {"id": sub_class_name}):

            if ('paragraph' in str(i)):
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


def get_news_articles(category_link, news_cateogry="sports", class_name="gs-c-promo"):
    article_dict = dict()

    try:
        article = requests.get(category_link)
        soup = bs(article.content, 'html.parser')

        for i in soup.findAll('div', {"class": class_name}):
            name_key = ''
            value_link = ''

            if (category_link in str(i)):
                pattern = category_link + '(.+?)"'
                m = re.findall(pattern, str(i))
                name_key = ''.join(re.findall(r'data-bbc-title=(.+?)"', str(i)))
                value_link = category_link + ''.join(m)
                article_dict[value_link] = name_key

        sub_class_name = "data-reactid"

        if category == "news":
            sub_class_name = "data-reactid"

        read_article_by_id(article_dict)

    except Exception as ex:
        print("Following error occurred while scraping the News Article - {}".format(category_link))
        print(str(ex))


if __name__ == "__main__":

    for article_link in sport_news_by_category:

        category = str(article_link).split("/")[-3]

        class_name = "gs-c-promo"

        if category == "news":
            class_name = "gs-c-promo"

        get_news_articles(
            article_link,
            category,
            class_name
        )
