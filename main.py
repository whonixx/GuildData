import requests
import json
import pandas as pd
import numpy as np
import glob
import csv
import os

from colorama import Fore
from datetime import date


RED = Fore.RED
GREEN = Fore.GREEN
RESET = Fore.RESET
spacer = "_" * 50
space6 = "_" * 60
dashes = "#" * 90


# checks to see if "stats" directory exist. If it does, it moves on. Otherwise, it creates a new directory called "stats" and created a new file called "strikeTracker.csv" and writes the first line as a header with 4 prenamed columns.
try:
    listOfFiles = glob.glob('stats/*')
    CSV_FILE = max(listOfFiles, key=os.path.getctime)
    players = pd.read_csv(f'{CSV_FILE}', usecols=['Player'])
except ValueError:
    os.mkdir("stats")
    header = ["Player", "Strike 1", "Strike 2", "Strike 3"]
    data = []
    with open("stats/strikeTracker.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(data)


# loads the config file and applies the Guild ID to the splinterlands API to pull stats for the desired guild. It then prints out a dataframe to show stats and provides an option to save the stats into the "stats" folder.
def getCurrentStats():
    f = open("config.json")
    data = json.load(f)
    guildID = data['Guild_ID']
    today = date.today()
    API = f"https://api.splinterlands.io/guilds/members?guild_id={guildID}"

    response = requests.get(API).json()
    encodedJson = json.dumps(response, indent=4)
    data = json.loads(encodedJson)

    storage = {}
    for k, v in [(key, d[key]) for d in data for key in d]:
        if k not in storage:
            storage[k] = [v]
        else:
            storage[k].append(v)
            

    playerList = []
    guildHall = []
    guildShop = []
    barracks = []
    arena = []
    totalcontributions = []

    for i in range(len(storage['player'])):
        if storage['status'][i] == 'active':
            player = storage['player'][i]
            playerList.append(player)
            contributions = json.loads(storage['data'][i])['contributions']
            guildHallData = contributions.get('guild_hall') or int()
            guildHall.append(guildHallData)
            guildShopData = contributions.get('guild_shop') or {}
            guildShopDEC = guildShopData.get('DEC') or int()
            guildShop.append(guildShopDEC)
            barracksData = contributions.get('barracks') or {}
            barracksDEC = barracksData.get('DEC') or int()
            barracks.append(barracksDEC)
            arenaData = contributions.get('arena') or {}
            arenaDEC = arenaData.get('DEC') or int()
            arena.append(arenaDEC)
            total = guildHallData + guildShopDEC + barracksDEC + arenaDEC
            totalcontributions.append(total)
            
    df = pd.DataFrame(np.array([playerList, guildHall, guildShop, barracks, arena, totalcontributions]).T)
    df.columns = ['Player', 'Guild Hall', 'Guild Shop', 'Barracks', 'Arena', 'Total']
    df.index += 1
    os.system('cls')
    print(df, "\n")
    question = input("Save to stats folder? [Y/N]: ")
    if question.lower() == "y":
        df.to_csv(f'stats/{today}_stats.csv', index=False)
        print("Saved to stats folder")
        retToMainMenu()
    elif question.lower() == "n":
        retToMainMenu()
    else:
        print("Invalid entry.. Returning to Main Menu")
        mainMenu()


# reads the "strikeTracker" file and gives the option to add a strike to a member of the guild.
def addStrike():
    today = date.today()
    df = pd.read_csv('stats/strikeTracker.csv')
    print(df)
    print(spacer, '\n')
    try:
        playerIndex = int(input('Index of player to receive strike: '))
        if df.at[int(f'{playerIndex}'), 'Strike 1'] == 'x':
            df.at[int(f'{playerIndex}'), 'Strike 1'] = today
        elif df.at[int(f'{playerIndex}'), 'Strike 1'] != 'x' and df.at[int(f'{playerIndex}'), 'Strike 2'] == 'x':
            df.at[int(f'{playerIndex}'), 'Strike 2'] = today
        elif df.at[int(f'{playerIndex}'), 'Strike 1'] != 'x' and df.at[int(f'{playerIndex}'), 'Strike 2'] != 'x':
            df.at[int(f'{playerIndex}'), 'Strike 3'] = today
        df.to_csv('stats/strikeTracker.csv', index=False)
        print(df)
        retToMainMenu()
    except ValueError:
            print(f'{RED}Invalid Data. Returning to Main Menu{RESET}')
            mainMenu()
    except KeyError:
        os.system('cls')
        print("Invalid player index. Returning to Main Menu")
        mainMenu()


# reads the "strikeTracker" file and prints out a current dataframe.
def viewStrikes():
    df = pd.read_csv('stats/strikeTracker.csv')
    print(space6)
    print(df)
    print(space6)
    print()
    retToMainMenu()


# provides a menu to give options in relation to guild member strikes.
def strikeTrackerMenu():
    os.system('cls')
    options = input(f'''
    A: Give Player Strike
    B: View Strike DataFrame
    M: Main Menu
    X: Exit
    {spacer}\n
    Selection: ''')
    print(options)
    if options.lower() == "a":
        addStrike()
    elif options.lower() == "b":
        viewStrikes()
    elif options.lower() == "m":
        mainMenu()
    elif options.lower() == "x":
        exit()
    else:
        os.system('cls')
        print(f'{GREEN}{spacer}{RESET}\n')
        print(f'''{RED}ERROR: You picked an invalid option\nReturning to Main Menu.{RESET}''')
        print(f'{GREEN}{spacer}{RESET}')
        mainMenu()


# allows you to add a player to the guild member list
def addPlayer():
    newPlayer = input('New players name: ').lower()
    df = pd.DataFrame({
    'Player': [f'{newPlayer}'],
    'Strike 1': ['x'],
    'Strike 2': ['x'],
    'Strike 3': ['x'],
    })
    df.to_csv('stats/strikeTracker.csv', mode='a', header=False, index=False)
    print()
    print(f'ATTENTION!! : {newPlayer} has been successfully added to players list')
    option = input("""
    A: View Player List
    M: Main Menu
    X: Exit

    Selection: """)
    if option.lower() == "a":
        df = pd.read_csv('stats/strikeTracker.csv')
        os.system('cls')
        print(df)
        print()
        retToMainMenu()
    elif option.lower() == "m":
        os.system('cls')
        mainMenu()
    elif option.lower() == "x":
        exit()
    else:
        retToMainMenu()


# allows you to remove a player from the guild member list
def removePlayer():
    df = pd.read_csv('stats/strikeTracker.csv')
    print(players)
    playerToRemove = input('Name of player: ').lower()
    df2 = df[~df['Player'].str.contains(f'{playerToRemove}', na=False)]
    df2.to_csv('stats/strikeTracker.csv', mode='w', index=False)
    print(spacer)
    print(f'{playerToRemove} has been successfully removed from players list')
    print(spacer)
    retToMainMenu()


# allows you to import an entire team by providing a Guild ID
def importTeam():
    guildID = input("Guild ID: ")
    API = f"https://api.splinterlands.io/guilds/members?guild_id={guildID}"

    response = requests.get(API).json()
    encodedJson = json.dumps(response, indent=4)
    data = json.loads(encodedJson)

    storage = {}
    for k, v in [(key, d[key]) for d in data for key in d]:
        if k not in storage:
            storage[k] = [v]
        else:
            storage[k].append(v)

    playerList = []

    for i in range(len(storage['player'])):
        if storage['status'][i] == "active":
            player = storage['player'][i]
            playerList.append(player)


    for i in playerList:
        df = pd.DataFrame({
        'Player': [f'{i}'],
        'Strike 1': ['x'],
        'Strike 2': ['x'],
        'Strike 3': ['x'],
        })
        df.to_csv('stats/strikeTracker.csv', mode='a', header=False, index=False)
        print(f'{i} has been successfully added to players list')

    print
    print()
    retToMainMenu()


# will ask you to input two different files from the "stats" folder and compares the two different weeks and provides a dataframe to show you the comparison.
def compareTwoWeeks():
    try:
        df1 = input('Previous Week CSV: ' )
        if df1 == "m":
            os.system('cls')
            mainMenu()
        else:
            df2 = input('Current Week CSV: ')
            previousWeek = pd.read_csv(f'{df1}', usecols=['Player', 'Total'])
            previousWeek.rename(columns={'Player': 'Player', 'Total': 'Last Week'}, inplace=True)
            newWeek = pd.read_csv(f'{df2}', usecols=['Total'])
            newWeek.rename(columns={'Player': 'Player', 'Total': 'Current Week'}, inplace=True)

            df = pd.concat([previousWeek, newWeek], axis=1, join="inner")
            df['Weekly Total'] = df['Current Week'] - df['Last Week']
            print(df.to_string(index=False))
            print()
            retToMainMenu()
    except FileNotFoundError:
        print("""An error occurred! Please try again!
        Example Format:
            Previous Week CSV: stats/2021-12-18_stats.csv
            Current Week CSV: stats/2021-12-25_stats.csv

            Type "m" to return to Main Menu.
        """)
        compareTwoWeeks()


# prints out a detailed help menu that explains what utility each function provides.
def helpMe():
    os.system('cls')
    print(f"""
    h
    Note: First time here? Edit your config file!

        Example:
                "Guild_ID": "c43af991dc15970e2047548f5b7bfc30a9943543"

        Change the Guild Id to the Guild ID of your choice.

        From the Main Menu, select "D: Team Roster Adjustments" and you can 
        either import an entire team using a Guild ID or you can import specific
        players using the "add player" feature.

    {dashes}

    A: Build Contribution Report

        - This is useful once you have a team saved and want to view how much each
        player has contributed to each building. It will also provide the total 
        contributions of each player.

    Example: 
                    
                  Player Guild Hall Guild Shop Barracks Arena  Total
    1        superflykai       1000          0        0   100   1100
    2       jimmyballsac        250          0        0     0    250
    3             saryx9        250          0        0     0    250
    4   legolasgreenleaf        550          0      450     0   1000
    5         mrxquizite        500          0     1000     0   1500
    6       supersloth11        750          0     1435    70   2255
    7         thebusycat        750          0     1750     0   2500
    8           vodolaza        909          0     2005     0   2914
    9               wobs        650       2307     2208   821   5986
    10           plebdev       6000      16500     5800  3500  31800
    11            sexeed       3253        986      608  1004   5851
    12          sdrea787       6274       4450     3314  2899  16937
    13    goldenbrownpdx       4412       2989     3507   692  11600
    14          mikofs31       3592        770     1100   450   5912
    15            idkpdx      12247       1000     5588     0  18835

    {dashes}

    B: Strike Tracker

    - This feature is useful if you have a "3 strikes and you're out" rule as it allows
    you to keep track of the players and their strikes. You may also choose to view the 
    Strike Tracker dataframe which will show you how many strikes each player has and when
    they occurred. At this time, there is no automatic removal of strikes so you will have
    to manually remove them. 

    Example:
                  Player    Strike 1    Strike 2 Strike 3
    0       supersloth11           x           x        x
    1         thebusycat           x           x        x
    2           vodolaza  2021-11-27  2021-12-04        x
    3               wobs           x           x        x
    4            plebdev           x           x        x
    5             sexeed  2021-11-27  2021-12-11        x
    6           sdrea787           x           x        x
    7     goldenbrownpdx           x           x        x
    8           mikofs31           x           x        x
    9             idkpdx           x           x        x
    10        mrxquizite           x           x        x
    11  legolasgreenleaf  2021-12-27           x        x
    12            saryx9  2021-12-27           x        x
    13      jimmyballsac  2021-12-27           x        x
    14       superflykai  2021-12-27           x        x

    {dashes}

    C: Weekly Numbers

    {RED}-WARNING!{RESET} Before using this feature, you will need to have at least 2 stat reports
    from different dates saved in your stats folder. {RED}!WARNING{RESET}
    
    I run this tool weekly to allow me to share with my guild what the team does on a weekly basis
    and to keep track of who isn't doing their weekly contributions. You will be required to enter 
    the file path for each .csv report.

    Example:
            Previous Week CSV: stats/2021-12-18_stats.csv
            Current Week CSV: stats/2021-12-25_stats.csv

    Example Output:
              Player  Last Week  Current Week  Weekly Total
         superflykai          0          1100          1100
        jimmyballsac        250           250             0
              saryx9        250           250             0
    legolasgreenleaf       1000          1000             0
          mrxquizite       1500          1500             0
        supersloth11       1905          2205           300
          thebusycat       2250          2500           250
            vodolaza       2667          2767           100
                wobs       5736          5986           250
             plebdev      30400         31400          1000
              sexeed       5601          5601             0
            sdrea787      16615         16825           210
      goldenbrownpdx      11000         11400           400
            mikofs31       5522          5812           290
              idkpdx      18169         18835           666

    {dashes}

    D: Team Roster Adjustment
    - This feature allows you to add and remove players from your team.
    Adding a new player will add them to the strike board with 3 empty strikes. 

    - Removing a player will also remove their name/contributions from any previous stat reports.
    """)
    retToMainMenu()


# main menu to show what options the app has to offer.
def mainMenu():
    options = input(f"""
    A: Build Contribution Report
    B: Strike Tracker
    C: Weekly Numbers
    D: Team Roster Adjustments
    H: Help!
    X: Exit
    {spacer}\n
    Selection: """)
    print(options)
    if options.lower() == "a":
        getCurrentStats()
    elif options.lower() == "b":
        strikeTrackerMenu()
    elif options.lower() == "c":
        compareTwoWeeks()
    elif options.lower() == "d":
        os.system('cls')
        choice = input("What would you like to do?\n1: Add Player\n2: Remove Player\n3. Import Team\n\nSelection: ")
        if choice == "1":
            addPlayer()
        elif choice == "2":
            removePlayer()
        elif choice == "3":
            importTeam()
        else:
            os.system('cls')
            print("Invalid Option. Returning to Main Menu!")
            mainMenu()
    elif options.lower() == "h":
        helpMe()
    elif options.lower() == "x":
        exit()
    else:
        os.system('cls')
        print(f'{RED}INVALID OPTION\nRETURNING TO MAIN MENU{RESET}')
        mainMenu()


# prints out a banner/title for the app when intially opened.
def banner():
    print("""
    #################################################
    #                                               #
    # -  Splinterlands Guild Data Control Center  - #
    #                                               #
    #################################################
    """)


# gives easy access of returning to the main menu
def retToMainMenu():
    option = input("Return to Main Menu: [Y/N]? ")
    if option.lower() == "y":
        os.system('cls')
        mainMenu()
    elif option.lower() == "n":
        print("Goodbye!")
        exit()
    else:
        os.system('cls')
        print("Invalid Option. Returning to Main Menu.")
        mainMenu()


banner()
mainMenu()
