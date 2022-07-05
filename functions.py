import os

import psycopg2
import challonge
import consts


def getPlayers(): 
    # Retrieves all players from the database to be used by command logic, returns those as a list of tuples
    i=0
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    cursor = conn.cursor()
    cursor.execute("SELECT CHALLONGE, DISCORDID, EXCUSED, LEAGUE FROM PLAYERS")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if rows:
        return rows

def getDelayers(round, leagueid): 
    # Uses challonge API to check which players haven't reported their results, returns 2D list of players and their opponents
    lazies = []
    challRound = 0
    if round < 8:
        challRound = round
    elif round == 8:
        challRound = 1
    else:
        challRound = 2
    
    challonge.set_credentials("Heltrosh", os.getenv("CHALLONGE_KEY"))
    tournaments = [challonge.tournaments.show("3deg6sfm"), challonge.tournaments.show("6svp9be5"), 
                   challonge.tournaments.show("ldc7iv9i"), challonge.tournaments.show("wgmwco9o"), 
                   challonge.tournaments.show("szwgkw9x"), challonge.tournaments.show("9ha7dixz")]
    for match in challonge.matches.index(tournaments[leagueid]["id"]):
        if match["round"] == challRound and match["state"] == "open":
            if round < 8: #group stage
                for player in challonge.participants.index(tournaments[leagueid]["id"]):
                    if player["group_player_ids"][0] == match["player1_id"]:
                        lazies.append([])
                        lazies[-1].append(player["challonge_username"])
                        for opponent in challonge.participants.index(tournaments[leagueid]["id"]):
                            if opponent["group_player_ids"][0] == match["player2_id"]:
                                lazies[-1].append(opponent["challonge_username"])
                        lazies.append([])
                        lazies[-1].append(lazies[-2][1])
                        lazies[-1].append(lazies[-2][0])
            else: #playoffs
                lazies.append([])
                lazies[-1].append(challonge.participants.show(tournaments[leagueid]["id"], match["player1_id"])["challonge_username"])
                lazies[-1].append(challonge.participants.show(tournaments[leagueid]["id"], match["player2_id"])["challonge_username"])
                lazies.append([])
                lazies[-1].append(lazies[-2][1])
                lazies[-1].append(lazies[-2][0])
    return lazies

def getPingMessage(discordName, round, opponent, league, isOpponentExcused): 
    # Returns the message to be sent to players with unreported results
    conn = conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    cursor = conn.cursor()
    cursor.execute("SELECT DEADLINE FROM DEADLINES WHERE ROUND = %s", [round])
    player = cursor.fetchone()
    deadline = player[0]
    cursor.execute("SELECT DISCORDNAME FROM PLAYERS WHERE CHALLONGE = %s", [opponent])
    player = cursor.fetchone()
    opponentDiscord = "ERROR, CONTACT HELTROSH"
    if player:
        opponentDiscord = player[0] 
    cursor.execute("SELECT LINK, CHANNEL FROM BRACKETLINKS WHERE LEAGUE = %s", [league])
    player = cursor.fetchone()
    bracketURL = player[0]
    discordChannel = player[1]
    cursor.close()
    conn.close()
    if isOpponentExcused:
        messageStr = consts.EXCUSED_PING_DM.format(discordName = discordName, round = round, opponent = opponent, 
                                                  opponentDiscord = opponentDiscord)
    else:
        messageStr = consts.NORMAL_PING_DM.format(discordName = discordName, round = round, opponent = opponent, 
                                                  opponentDiscord = opponentDiscord, deadline = deadline,
                                                  discordChannel = discordChannel, bracketURL = bracketURL)
    return messageStr

def processExcuse(challonge, rounds): 
    # Logic for excusing players, returns list of excused rounds
    cmdRounds = [int(round) for round in rounds]
    newRounds = []
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    cursor = conn.cursor()
    cursor.execute("SELECT CHALLONGE, EXCUSED FROM PLAYERS WHERE CHALLONGE = %s", [challonge])
    player = cursor.fetchone()
    if not player:
        cursor.close()
        conn.close()
        return newRounds
    dbRounds = player[1] #for clarity
    if not dbRounds:
        newRounds = sorted(cmdRounds)
    else:
        newRounds = sorted((set(cmdRounds).symmetric_difference(set(dbRounds))))
    cursor.execute("UPDATE PLAYERS SET EXCUSED = %s WHERE CHALLONGE = %s", (newRounds, challonge))
    cursor.close()
    conn.commit()
    conn.close()
    if not newRounds:
        return -1
    return newRounds