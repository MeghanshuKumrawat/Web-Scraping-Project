from ast import keyword
import requests
from bs4 import BeautifulSoup
import csv
import datetime
from pprint import pprint
import sqlite3
from colorama import Fore, Style, init

init(convert=True)


class Verge_scraper:
    def __init__(self, url, keyword=""):
        """
        colours code :
            RED : Error
            CYAN : create_object
            YELLOW : data_extractor
            WHITE : print_table
            GREEN : write_to_csv
            BLUE : write_to_database
        """
        self.url = url
        self.keyword = keyword
        self.articles = []
        self.soup = None

    def create_object(self):
        r = requests.get(self.parse_url())
        if r.status_code == 200:
            self.soup = BeautifulSoup(r.content, 'html5lib')
            print(Fore.CYAN + "VERGE_scraper : Object created!\n","Status Code : ", r.status_code)
        else:
            print(Fore.RED + "VERGE_scraper : Object not created!\n","Status Code : ", r.status_code)

    def parse_url(self):
        parsed_url = "https://" + self.url + "/" + self.keyword
        return parsed_url  

    def keyword_extractor(self):
        pass
    def data_extractor(self):
        try:
            for i, row in enumerate(self.soup.find_all("div", attrs={"class":"c-entry-box--compact__body"})):
                if str(row.h2.a["href"]).split('/')[2] == "www.theverge.com":
                    article = {}
                    article["id"] = i
                    try:
                        article["url"] = row.h2.a["href"]
                    except:
                        article["url"] = None
                    try:
                        article["headline"] = row.h2.text
                    except:
                        article["headline"] = None
                    try:
                        article["author"] = row.span.a.text
                    except:
                        article["author"] = None
                    try:
                        article["date"] = str(row.span.time['datetime']).split('T')[0]
                    except:
                        article["date"] = None
                    self.articles.append(article)
            print(Fore.YELLOW + "VERGE_scraper : Data extracted successfully!")
        except Exception as e:
            print(e)

    def write_to_csv(self):
        curr_date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        filename = curr_date +'_verge.csv'
        with open(filename, 'w', newline='') as f:
            w = csv.DictWriter(f,['id','url','headline','author','date'])
            w.writeheader()
            for article in self.articles:
                w.writerow(article)
        print(Fore.GREEN + "VERGE_scraper : CSV file created successfully!")
                
    def write_to_database(self):
        try:
            sqliteConnection = sqlite3.connect('Verge_scraper.db')
            sqlite_create_table_query = '''CREATE TABLE if not exists Verge_Articles(id INT PRIMARY KEY, url VARCHAR(255),
                                    headline VARCHAR(255), author VARCHAR(255), date VARCHAR(100));'''

            cursor = sqliteConnection.cursor()
            print(Fore.BLUE + "VERGE_scraper : Successfully Connected to SQLite!")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            sqlite_insert_data_query = 'INSERT INTO Verge_Articles (id, url, headline, author, date) VALUES(:id, :url, :headline, :author, :date);'
            print(Fore.BLUE + "VERGE_scraper : SQLite table created!")
            cursor.executemany(sqlite_insert_data_query, self.articles)
            sqliteConnection.commit()
        
            print(Fore.BLUE + 'VERGE_scraper : We have inserted', cursor.rowcount, 'records to the table!')
            cursor.close()

        except sqlite3.Error as error:
            print(Fore.RED + "VERGE_scraper : Error while creating a sqlite table! ", error)
        finally:
            if sqliteConnection:
                sqliteConnection.close()
        print(Fore.BLUE + "VERGE_scraper : sqlite connection is closed!")


    def print_table(self):
        if len(self.articles) != 0:
            print(Fore.WHITE)
            pprint(self.articles)
        else:
            print(Fore.GREEN + "VERGE_scraper : No Data Available!")


if __name__=="__main__":
    obj = Verge_scraper(url="www.theverge.com")
    obj.create_object()
    obj.data_extractor()
    obj.print_table()
    obj.write_to_csv()
    obj.write_to_database()