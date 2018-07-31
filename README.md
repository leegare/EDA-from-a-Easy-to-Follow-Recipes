# Project-II

## What are the top ingredients to prepare a MAX of quick and easy meals?
#### Exploring the homechef.com dataset of recipes
Ricardo Aguilar, K2 Exploratory Data Analysis

#### Introduction

This repository contains the following folders and files:

- Datasets: where a sqlite file contains the database with 3 tables explained further
- Img: Graphs and charts used to illustrate the project.
- The Jupyter notebooks: described below:

1. P2 DB Creation and tables - This notebook creates 3 tables in the project's database:
meal_info table: it's the main table consisting of :
meal_id, meal_title, cook-time , expertise level, spicyness level, days til expiration, category and personal rating.
meal_ingredients: it links the meal_id to the list of ingredients.
meal_bow: It's a table containing the Bag of Words used to segment the ingredients list.

2. P2 Web Scraping - The scripts in this notebook will scrape the recipes out of the website's dataset and fill the meal_info and meal_ingredients table. There is also another script that inserts the same amount of information but instead of getting the url of homechef's recipe index, it receives the url of a single meal.

3. P2 CSV scraping - Reads the data located in the csv file I've created since I started cooking with Homechef and logging the meal's id, meal's title, category, rating. Then defines the url of the recipe and scrapes the ingredients out of the web page and saves it on the meal_ingredients table.

4. P2 Merge csv with web info - Script that just merges the meal_info tables and the meal_ingredients tables from both sources (web and csv)

5. P2 Preprocess Data - contains the scripts to polish the data prior to interpretation and saves it in a sqlite file.

6. P2 Visualization - Script that has the code to create all files in the img folder.

7. P2 Project2 - Markdown content summarizing the project.

8. MVP - Markdown content of the MVP.
