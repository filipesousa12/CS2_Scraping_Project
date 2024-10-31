from time import sleep
import pandas as pd
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
from datetime import datetime
import logging



def connection():

    '''
    This function creates the connection to the browser. 
    '''
    try:
        # Set up firefox options to run in headless mode
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")   
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        driver = webdriver.Firefox(options=options)

        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {str(e)}")
        raise


def log_error(message):
    
    '''
    Function to produce an errorfile for that specific day
    Parameter:
        message(string ?)-> The error message coming from the exception in each function used
    '''

    error_folder = "error_messages"
    os.makedirs(error_folder, exist_ok=True)  # Create folder if it doesn't exist

    # Get the current date and format it for the file name
    current_date = datetime.now().strftime("%Y-%m-%d")
    error_file_name = f"error_log_{current_date}.txt"
    
    # Full path to the error file
    error_file_path = os.path.join(error_folder, error_file_name)
    
    # Log the error message to the file
    with open(error_file_path, "a") as error_file:
        error_file.write(f"{message}\n")
    return 

def getMatches(url):

    '''
    This function gets the data of each match.
    Parameter:
        url(String) -> url of the page results from hltv 
    '''
   
    try:
        browser = connection()

        #Initial dataframe for all matches of that day
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
        df2 = df[(df['game'] != 'BENCH') & (df['game'] != '') ].copy()
        df2 = df2[df2['link'].str.contains('/matches/') & df2['link'].notna()]

        #Split the query to get the game, teams, score, event and type of match
        df2['split_game'] = df2['game'].str.split('\n')

        #Check if they are really matches (needs teams, score and type of match making 5 columns)
        df3 =  df2[df2['split_game'].apply(lambda x: len(x) > 2)].copy()

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
        df3.reset_index(drop=True, inplace=True)
        browser.quit()
        return df3

    except Exception as e:
        log_error(f"Error occurred: {str(e)}")
        if 'browser' in locals():
            browser.quit()  # Ensure browser quits in case of error


def getplayers(url):

    '''
    This function fetches all the players in a specific match
    Parameter:
        url(string) -> the url of a specific match 
    '''
 
    try:
        browser = connection()
        sleep(3)
        browser.get(url) 
        
        lineups = browser.find_element(By.CLASS_NAME, 'lineups').find_elements(By.CLASS_NAME, 'players') #gets the lineups from a specific match
        p = [] #empty list to fill with each player url
        for lineup in lineups: 
            players=lineup.find_elements(By.CLASS_NAME, 'player') #find all the elements with the class player
            for player in players:
                href = player.find_element(By.TAG_NAME, 'a').get_attribute('href') #gets the href with will have the url for the specific player
                p.append(href)
                
        df1 = pd.DataFrame(p, columns=['player']).drop_duplicates() #Creates a dataset with the unique player's url

        browser.quit()

        return df1
    
    except Exception as e:

        log_error(f"Error occurred: {str(e)}")
        if 'browser' in locals():
            browser.quit() 


def playerdetails(url,df):
    
    '''
    This function gets all the details about a player
    Parameters:
        url(string)-> url of the player
        df (pandas dataframe) -> the players dataset to enrich with the player's information
    '''

    try:
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
    
    except Exception as e:
        log_error(f"Error occurred: {str(e)}")
        if 'browser' in locals():
            browser.quit() 
        
def getevents(url):

    '''
    Gets the event that each match was played 
    Parameter:
        url(string) -> the url of a specific match 
    '''
    try:
        browser=connection()

        browser.get(url)
            
        events = browser.find_element(By.CLASS_NAME, 'timeAndEvent').find_element(By.CLASS_NAME, 'text-ellipsis')

        id = events.find_element(By.TAG_NAME, 'a').get_attribute('href')
        name = events.text
                
        df1 = pd.DataFrame(pcolumns=['id','event'])
        df1['id'] = id
        df1['event']=name

        browser.quit()
        return df1
    
    except Exception as e:
        log_error(f"Error occurred: {str(e)}")
        if 'browser' in locals():
            browser.quit() 


def extract():
    
    '''
    This function executes the extract of matches, players, players details and events

    '''
    results_page = 'https://www.hltv.org/results'
    matches = getMatches(results_page)
    if matches is None or matches.empty:
        print("deu merda")
        print(connection())
    else:
        players = pd.DataFrame(columns=['player'])
        events = pd.DataFrame(columns=['event'])
        
        for match in matches['link'][:2]:
            event = getevents(match)
            player = getplayers(match)
            players = pd.concat([players,player], ignore_index=True)
            events = pd.concat([events,event], ignore_index=True)
            
        players.drop_duplicates(inplace=True)
        #Extract the matchid 
        players['player_id'] = players['player'].str.extract(r'/player/(\d+)/')

        events.drop_duplicates(inplace=True)
        events['event_id'] = events['event'].str.extract(r'/events/(\d+)/')

    
        #Check if the folders exists if not it will create one (This functionality will go away once i move it to a cloud provider)
        os.makedirs('matches', exist_ok=True)
        os.makedirs('players', exist_ok=True)
        os.makedirs('events', exist_ok=True)

    
        current_date = datetime.now().strftime("%Y-%m-%d")
        matches.to_parquet(f'matches/matches_{current_date}.parquet')
        players.to_parquet(f'players/players_{current_date}.parquet')
        events.to_parquet(f'events/events_{current_date}.parquet')
    


