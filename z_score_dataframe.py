# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 15:14:52 2021

@author: cflensbatina
"""

"""
This script scrapes cefconnect.com to get Z Score and Discount data on specified Closed End Funds.
It relies on two other scripts, one that I created (z_scores.py) and one borrowed from Charles Severance at the University of Michigan (hidden.py).
This script returns a series of dataframes recommending which funds to buy and sell based on the parameters used.
It emails the three dataframes to an email list saved in hidden.py.
It also saves the unsorted main dataframe as CEFS.csv on your computer.

Change the default emails in hidden.py and add your email password so the script will run correctly.
Don't change z_scores.py.

The default filters in this tool represent my opinions and are not recommendations or advice.
They are meant to be informative, but you must do your own research before investing.
Consult a financial advisor before making any investments, to best fit your situation and risk profile.

The score listed on the "buy" dataframe is a composite of several factors.
Lower scores are better, in general, but each fund is different.
Again, do your own research before investing in any funds.
"""

# Import specific packages
import z_scores
import hidden

# Import general packages
from time import localtime
from os.path import getmtime
import pandas as pd
import ssl, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define functions
def save_cefs(tickers) :
    cefs = z_scores.z_scores_discounts(tickers)
    cefs.to_csv(path_or_buf='CEFs.csv', index=False, mode='w')
    return cefs

def check_file_date(file) :
    file_time = getmtime(file)
    local_file_time = localtime(file_time)
    return local_file_time

# Choose CEFs to analyze
tickers = ['TYG','DSL','KMF','HPI','RMT','ARDC','HYI','HPF',
           'TEAF','MXF','BMEZ','PGZ','ETG','THQ','HIE','RQI',
           'RNP','EHT','EMF','PDT','GCV','NCV','BFY','BNY',
           'JDD','FGB','SZC','JCE']

# Check modification date on 'CEFs.csv'
try : local_file_time = check_file_date('CEFs.csv')

except :
    print ('\nNo file found')
    save_cefs(tickers)
    print ('\nFile saved')
    local_file_time = check_file_date('CEFs.csv')

# Scrape CEF data and save current CEFs to file
if local_file_time[0:3] != localtime()[0:3] : cefs = save_cefs(tickers)

# Or open 'CEFs.csv' and assign to cefs as a dataframe
else : cefs = pd.read_csv('CEFs.csv')

# Create Sell DF
sell = cefs.loc[(cefs['1 Yr Z']>=0.5) & (cefs['Current D']>=-3)].copy()

# Create Buy DF and add "Score" column
buy = cefs.loc[(cefs['1 Yr Z']<=0.5) & (cefs['Current D']<=-3)].copy()
buy['Score'] = (buy['1 Yr Z'] - 0.5) * buy['Current D'] * (buy['Current D']-buy['3 Yr D'])
buy = buy.sort_values(by=['Score'])

"""
sell1 = cefs.loc[(cefs['1 Yr Z']>=0) & (cefs['Current D']>=1)]
sell2 = cefs.loc[(cefs['1 Yr Z']>=0.5) & (cefs['Current D']>=-3)]
sell3 = cefs.loc[(cefs['1 Yr Z']>=1) & (cefs['Current D']>=-5)]
sell4 = cefs.loc[(cefs['1 Yr Z']>=1.5) & (cefs['Current D']>=-7)]

sell = pd.concat([sell1,sell2,sell3,sell4], axis=0, ignore_index = True, verify_integrity=False)

buy1 = cefs.loc[(cefs['1 Yr Z']<=-1) & (cefs['Current D']<=-2)]
buy2 = cefs.loc[(cefs['1 Yr Z']<=-0.5) & (cefs['Current D']<=-4)]
buy3 = cefs.loc[(cefs['1 Yr Z']<=0) & (cefs['Current D']<=-8)]
buy4 = cefs.loc[(cefs['1 Yr Z']<=0.5) & (cefs['Current D']<=-12)]

buy = pd.concat([buy1,buy2,buy3,buy4], axis=0, ignore_index = True, verify_integrity=False)
"""

# Set up email
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = hidden.auto_email()["user_name"]
receiver_emails = hidden.email_list()
password = hidden.auto_email()["password"]

#recipients = ['ToEmail@domain.com'] 
#emaillist = [elem.strip().split(',') for elem in recipients]

# Create Message
message = MIMEMultipart()
message['Subject'] = "Portfolio"
message['From'] = hidden.auto_email()["user_name"]


html = """\
<html>
  <head></head>
  <body>
    {0}
  </body>
</html>
""".format(cefs.to_html())

part1 = MIMEText(html, 'html')
message.attach(part1)

html2 = """\
<html>
  <head><br>Sell</head>
  <body>
    {0}
  </body>
</html>
""".format(sell.to_html())

part2 = MIMEText(html2, 'html')
message.attach(part2)

html3 = """\
<html>
  <head><br>Buy</head>
  <body>
    {0}
  </body>
</html>
""".format(buy.to_html())

part3 = MIMEText(html3, 'html')
message.attach(part3)

# Create a secure SSL context and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server :
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_emails, message.as_string())
    print ('Message sent')
