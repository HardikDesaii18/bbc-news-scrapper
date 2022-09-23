import sys
import streamlit as st
from PIL import Image
from streamlit.web import cli as stcli
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-west-2',
    aws_access_key_id='AKIAX22ZAZD6KRJGIVVW',
    aws_secret_access_key='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'
)

news_data_table = dynamodb.Table('bbcnews')


def main():
    st.title("BBC News Scrapping Project")
    st.markdown(
        "The dashboard will show the scraped articles from BBC news website.")
    st.sidebar.title("Navigation")
    # st.sidebar.markdown("Go to:")

    cateory = st.sidebar.selectbox("Main Category:", ('', 'SPORTS', 'FINANCE'))

    response = news_data_table.scan()
    result = response['Items']

    while 'LastEvaluatedKey' in response:
        print('in lasteva')
        response = news_data_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        result.extend(response['Items'])

    filter_result = []

    if cateory == "SPORTS":
        sub_category = st.sidebar.radio("Sub Category :", ('ALL', 'CRICKET', 'FOOTBALL', 'TENNIS', 'GOLF'))

        if sub_category == "ALL":
            for object in result:
                if 'sport_' in object['id']:
                    filter_result.append(object)

        if sub_category == "CRICKET":
            for object in result:
                if 'sport_cricket' in object['id']:
                    filter_result.append(object)

        if sub_category == "FOOTBALL":
            for object in result:
                if 'sport_football' in object['id']:
                    filter_result.append(object)

        if sub_category == "TENNIS":
            for object in result:
                if 'sport_tennis' in object['id']:
                    filter_result.append(object)

        if sub_category == "GOLF":
            for object in result:
                if 'sport_golf' in object['id']:
                    filter_result.append(object)

    if cateory == "FINANCE":
        sub_category = st.sidebar.radio("Sub Category :", ('MARKET', 'POLITICS',))

        if sub_category == "MARKET":
            print("MARKET")

        if sub_category == "POLITICS":
            print("POLITICS")

    with st.container():
        for object in filter_result:
            with st.expander(object['title']):
                st.write("Date - {}".format(object['date']))
                st.write("Category - {}".format(str(object['category'])).upper())
                st.write("Sub Category - {}".format(str(object['subcategory'])).upper())
                st.write(object['content'])


st.set_page_config(
    layout="wide",
    page_title='BBC News Scrapper',
)

if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:

        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
