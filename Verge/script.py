from bs4 import BeautifulSoup
import requests,json,csv,sqlite3
from datetime import datetime
from os.path import exists
import urllib.request



def connect(host='https://www.theverge.com/'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

if not connect():
    print("No internet")
    exit()
now = datetime.now()
date = now.strftime("%d%m%Y")


page = requests.get("https://www.theverge.com/")
if(page.status_code==200):
    soup = BeautifulSoup(page.text, 'html.parser')
    data = soup.select_one("#__NEXT_DATA__").text
    data = json.loads(data)
    id=0
    all_articles=[]
    data=data['props']['pageProps']['hydration']['responses']
    conn = sqlite3.connect('articles.db')
    cur=conn.cursor()
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ARTICLES' ''')
    if cur.fetchone()[0]!=1 : {
	conn.execute('''CREATE TABLE ARTICLES
         (ID INTEGER PRIMARY KEY   AUTOINCREMENT,
         TITLE           VARCHAR(100)    NOT NULL,
         URL       VARCHAR(1000)     NOT NULL,
         AUTHOR        VARCHAR(100),
         PUBLISH_DATE    DATE);''')
    }

    
    file_exists = exists('./articles/'+date+'_verge.csv')
    if(file_exists==False):
        csv_file=open('./articles/'+date+'_verge.csv', 'x', newline='')
    for i in data:
        for j in i['data']['community']['frontPage']['placements']:
            title=j['placeable']['title'] if j['placeable'] is not None else ''
            url=j['placeable']['url'] if j['placeable'] is not None else ''
            author=j['placeable']['author']['fullName'] if j['placeable'] is not None else ''
            publishDate=j['placeable']['publishDate'] if j['placeable'] is not None else ''
            cur.execute("SELECT * FROM ARTICLES WHERE Title='"+title+"'")
            rows = cur.fetchall()
            publishDate=publishDate.split('T',1)[0]
            if url!='':
                id=id+1
                all_articles.append({
                 "ID": id if id is not None else '',
                 "Title": title if title is not None else '',
                 "URL": url if url is not None else '',
                 "Author": author if author is not None else '',
                 "Publish Date": publishDate if publishDate is not None else ''
              })
            keys = all_articles[0].keys()
            with open('./articles/'+date+'_verge.csv', 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(all_articles)
            if(len(rows)>0):
                continue
            if url!='':
                sql=("INSERT INTO ARTICLES (TITLE,URL,AUTHOR,PUBLISH_DATE) VALUES ('"+title+"','"+url+"','"+ author+"','"+publishDate+"' )")
                conn.execute(sql)
    conn.commit()
    conn.close()



        

else:
    print("Request not processed")
