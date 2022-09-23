BBC News Scrapper

### Web Site - http://54.218.12.212:8501/

## Infrastructure

- Following AWS services are used for the implementation
  - EC2 - Hosting the scraping code and streamlit application
  - DynamoDB - For storing the NoSQL data of the articles

## Implementation

The Application works in 2 parts

1. hourly_scrap_news_by_categories.py - This program runs every hour and scraps the data from BBC website for the Sports and New section
- Each article is uniquely identified using category+sub_category+ID
- Program scraps all the available links and check if the data already availabe
  - If no - insert the data
  - If yes - skip the data insert

2. streamlit_application.py - This file hosts the application and fetches the data from DynamoDB which contains the scraped data from the above file

3. Crontab - an entry for the file is added which will invoce the execution at every hour and 0th Minute
Working

## Security

- AWS Role is assigned to the EC2 mahcine in order to interact with the System
- SSH into the EC2 machine is whitelisted only to Developers IP
- HTTP and HTTPs traffic is only allowed on the port 8501 

## Scope of Improvement

- Sort the Articles by date descending
- Add photos of the article


