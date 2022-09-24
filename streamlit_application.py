import sys
import streamlit as st
from PIL import Image
from streamlit.web import cli as stcli
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-west-2',
)

news_data_table = dynamodb.Table('bbcnews')


def main():
    st.title("BBC News Scrapping Project")
    st.markdown(
        "The dashboard will show the scraped articles from BBC news website.")
    st.sidebar.title("Navigation")
    # st.sidebar.markdown("Go to:")

    cateory = st.sidebar.selectbox("Main Category:", ('', 'SPORTS', 'NEWS'))

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

    if cateory == "NEWS":
        sub_category = st.sidebar.radio("Sub Category :", ('WORLD', 'BUSINESS', 'UK', 'CORONA VIRUS'))

        if sub_category == "WORLD":
            for object in result:
                if 'news_world' in object['id']:
                    filter_result.append(object)

        if sub_category == "BUSINESS":
            for object in result:
                if 'news_business' in object['id']:
                    filter_result.append(object)

        if sub_category == "UK":
            for object in result:
                if 'news_uk' in object['id']:
                    filter_result.append(object)

        if sub_category == "CORONA VIRUS":
            for object in result:
                if 'news_coronavirus' in object['id']:
                    filter_result.append(object)

    # sort the articles before showing
    ordered_dict = dict()

    for object in filter_result:
        date_int = int("".join(object['date'].split("-")))

        if date_int not in ordered_dict.keys():
            ordered_dict[date_int] = list()

        ordered_dict[date_int].append(object)

    # sort the keys
    ordered_keys = sorted(ordered_dict.keys(), reverse=True)

    with st.container():
        for date_key in ordered_keys:
            filter_result = ordered_dict[date_key]

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
