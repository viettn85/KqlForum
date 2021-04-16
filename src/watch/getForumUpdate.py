import smtplib, ssl, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time

from dotenv import load_dotenv
load_dotenv(dotenv_path='stock.env')
import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def sendMail(content):
    try:
        port = 587
        smtp_server = "smtp.gmail.com"
        message = MIMEMultipart()
        # message["From"] = os.getenv('sender')
        # message["To"] = os.getenv('receiver')
        message["Subject"] = "Update F319 " + datetime.now().strftime("%Y-%m-%d %H-%M")
        logger.info(message["Subject"])
        # message["Bcc"] = os.getenv('bcc') 
        message.attach(MIMEText("\n".join(content), "plain"))

        context = ssl.create_default_context()
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(os.getenv('sender'), os.getenv('password'))
        print(os.getenv('receiver'))
        server.sendmail(os.getenv('sender'), os.getenv('receiver').split(','), message.as_string())
    except Exception as e:
        logger.error("Error when sending email")
        logger.error(e)


def addEmailContent(content, username, newPosts):
    if len(newPosts) > 0:
        content.append('\n')
        content.append("New posts of {}:".format(username))
        content.extend(newPosts)    

def getNewPostById(content, userId, username, lastPost):
    vgm_url = 'http://f319.com/search/member?user_id=' + userId
    html_text = requests.get(vgm_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    rs = soup.find_all("div", {"class": "listBlock main"})
    if len(rs) > 0:
        newLastPost = rs[0].find_all("abbr", {"class": "DateTime"})[0]['data-time']
        newPosts = []
        for i in range(len(rs)):
            abbr = rs[i].find_all("abbr", {"class": "DateTime"})[0]
            lastDataTime = abbr['data-time']
            if lastDataTime <= lastPost:
                break
            link = "http://f319.com/{}".format(rs[i].find_all("h3", {"class": "title"})[0].find_all("a")[0]["href"])
            datetime = "{} {}".format(abbr['data-datestring'], abbr['data-timestring'])
            newPosts.append("{}: {}".format(datetime, link))
        addEmailContent(content, username, newPosts)
        return newLastPost

def getUpdate():
    df = pd.read_csv("data/user_post.csv")
    content = []
    for i in range(len(df)):
        logger.info("Updating for {}".format(df.iloc[i].Username))
        newLastPost = getNewPostById(content, str(df.iloc[i].UserId), df.iloc[i].Username, str(df.iloc[i].LastTimePost))
        df.iloc[i, 2] = newLastPost
    if len(content) > 0:
        sendMail(content)
    df.to_csv("data/user_post.csv", index=False)

def job():
    getUpdate()

if __name__ == '__main__':
    schedule.every(5).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # getUpdate()

# Username,UserId,LastTimePost
# QuocKhang,526931,1617592591
# T.11.11.11,491608,1617535394
# kuTom,498518,1617592591