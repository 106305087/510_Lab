# 510_Lab5
### Overview
This is an interactive data visualization app for events in Seattle, which presents an overview of Seattle's events in these two months.
### Project Asset
- `app.py`: streamlit application for WebApp, which presents the data visualization
- `scraper.py`: Script to scrape website information
- `db.py`: Contains utility functions for database connection
- `data/`: JSONS files to store event data
- [Azure Link](https://techin510-peisyc-lab5.azurewebsites.net/)
### How to run
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Learning Points
1. How to connect with postgres on the Azure
2. How to implement SQL to create database and manipulate data
3. How to visualize the data in a proper format and make the chart interactive
