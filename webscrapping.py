from selenium.webdriver import Chrome
from time import sleep
import json
import pandas as pd
from selenium.webdriver.common.by import By  # Import By class
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def connection():

    '''
    This function creates the connection to the browser. 
    '''
    # Set up Chrome options to run in headless mode
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    #driver.get('https://www.google.com/')
  
     #Create browser connection
    #browser = Chrome(service=Service("path/to/chromedriver"), options=chrome_options)
    #first_page = 'https://www.hltv.org/results'
    return driver

def getMatches(url):

    '''
    This function gets the data of each match
    Note: Still need to add the stats of each players to the dataframe
    '''
    #Initial dataframe for all matches of that day
    browser = connection()
    df = pd.DataFrame(columns=['game', 'link'])

    browser.get(url)
    sleep(2)


    # Find elements by class name 'a-reset'
    games = browser.find_elements(By.CLASS_NAME, 'a-reset')
    
    #Get the link and the matche name 
    for i in range(len(games)):
        df.loc[i, 'game'] = games[i].text
        df.loc[i, 'link'] = games[i].get_attribute('href')
    
    #Drop duplicates
    df.drop_duplicates(inplace=True)

    #Only get the matches 
    df2 = df[(df['game'] != 'BENCH') & (df['game'] != '') ]
    df2 = df2[df2['link'].str.contains('/matches/') & df2['link'].notna()]

    #Split the query to get the game, teams, score, event and type of match
    df2['split_game'] = df2['game'].str.split('\n')

    #Check if they are really matches (needs teams, score and type of match making 5 columns)
    df3 =  df2[df2['split_game'].apply(lambda x: len(x) > 2)]

    #Extract the matchid 
    df3['match_id'] = df3['link'].str.extract(r'/matches/(\d+)/')

    #Get the match details
    df3['team_1']= df3['split_game'].str[0]
    df3['team_2']=df3['split_game'].str[2]
    df3['result']=df3['split_game'].str[1]
    df3['event']=df3['split_game'].str[3]
    df3['match_type']=df3['split_game'].str[4]

    #get the result of each team
    df3['result']=df3['result'].str.split('-')
    df3['score_t1'] =df3['result'].str[0]
    df3['score_t2'] =df3['result'].str[1]

    # Change the datatype of score_1 and score_2 to int
    df3['score_t1'] = df3['score_t1'].astype(int)
    df3['score_t2'] = df3['score_t2'].astype(int)

    #Get the match winner
    df3['Winner'] = df3.apply(lambda row: row['team_1'] if row['score_t1'] > row['score_t2'] else row['team_2'], axis=1)

    df3.drop(columns=['game','split_game','result'],inplace=True)
    browser.quit()
    return df3


def getplayers(url):

    '''This function fetches all the players in a specific match'''
    sleep(3)
    browser = connection()
    browser.get(url)
    
    lineups = browser.find_element(By.CLASS_NAME, 'lineups').find_elements(By.CLASS_NAME, 'players')
    p = []
    for lineup in lineups:
        players=lineup.find_elements(By.CLASS_NAME, 'player')
        for player in players:
            href = player.find_element(By.TAG_NAME, 'a').get_attribute('href')
            p.append(href)
             
    df1 = pd.DataFrame(p, columns=['player']).drop_duplicates()

    browser.quit()

    return df1


def playerdetails(url,df):
    
    '''
    This function gets all the details about a player
    '''
    browser=connection()

    browser.get(url)       
    sleep(2)

    playerInfoWrapper = browser.find_element(By.CLASS_NAME, 'playerInfoWrapper')

    playerNameWrapper = playerInfoWrapper.find_element(By.CLASS_NAME, 'playerNameWrapper')
    playername = playerNameWrapper.find_element(By.CLASS_NAME, 'playerRealname') #name
    playerInfo = playerInfoWrapper.find_element(By.CLASS_NAME, 'playerInfo')
        
    df.loc[df['player'] == url, 'Name'] = playername.text
    df.loc[df['player'] == url,'nationality'] = playername.find_element(By.TAG_NAME, 'img').get_attribute('alt')
    info = playerInfo.text.split('\n')
    df.loc[df['player'] == url,'age'] = info[1]
    df.loc[df['player'] == url,'team'] = info[3]

    browser.quit()

    return df
    
def getevents(url):

    '''
    Gets the event that each match was played 
    '''
    browser=connection()

    browser.get('url')
        
    events = browser.find_element(By.CLASS_NAME, 'timeAndEvent').find_element(By.CLASS_NAME, 'text-ellipsis')

    id = events.find_element(By.TAG_NAME, 'a').get_attribute('href')
    name = events.text
             
    df1 = pd.DataFrame(pcolumns=['id','event'])
    df1['id'] = id
    df1['event']=name

    browser.quit()
    return df1
