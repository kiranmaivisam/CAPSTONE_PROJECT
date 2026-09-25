\# Module 1 — Data Pipeline



\## Overview



This module builds a complete data pipeline for book data from Books to Scrape.



The pipeline performs:



1\. Web scraping using Requests and BeautifulSoup

2\. Data cleaning and type conversion

3\. Price conversion from GBP to INR

4\. SQLite database creation

5\. Normalized database storage using two related tables

6\. SQL querying

7\. Reading SQL results using pandas

8\. Reproducing a SQL JOIN using pandas merge



\## Data Source



Website: Books to Scrape



URL: https://books.toscrape.com/



The first 3 paginated product pages were scraped, producing 60 books.



\## Data Cleaning



The following transformations were performed:



\- Price was converted from text to float and stored as `price\_gbp`.

\- Rating words such as `Three` were converted to integers such as `3`.

\- Availability was converted to a Boolean `in\_stock` field.

\- Book categories were extracted from individual book pages.

\- INR price was calculated using the fixed conversion rate:



&#x20; 1 GBP = 105.50 INR



No missing values were found in the scraped dataset, so no imputation or row deletion was required.



\## Database Schema



Two normalized SQLite tables were created:



\### categories



\- category\_id — Primary Key

\- category\_name — Unique category name



\### books



\- book\_id — Primary Key

\- title

\- price\_gbp

\- price\_inr

\- rating

\- in\_stock

\- category\_id — Foreign Key referencing categories



\## SQL Queries



The project includes SQL queries demonstrating:



\- SELECT and WHERE

\- ORDER BY and LIMIT

\- DISTINCT

\- BETWEEN

\- JOIN



The query strings are stored in `sql\_queries.py`.



The generated query outputs are stored in `sql\_outputs.txt`.



\## Pandas SQL Integration



At least two SQL query results are read using `pd.read\_sql()`.



The SQL JOIN between `books` and `categories` is also reproduced using `pd.merge()` on in-memory DataFrames.



\## Files



\- `scraper.py` — End-to-end scraping, cleaning, database creation, SQL execution and pandas analysis

\- `sql\_queries.py` — SQL query definitions

\- `sql\_outputs.txt` — Saved SQL query outputs

\- `zepto.db` — SQLite database

