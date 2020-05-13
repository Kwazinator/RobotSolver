import requests
import json
import datetime
import time
import ricochet
import model
import http.client
#/home/kwazinator/PycharmProjects/robits/venv/lib/python3.5/site-packages/selenium
from selenium import webdriver #http://stanford.edu/~mgorkove/cgi-bin/rpython_tutorials/Scraping_a_Webpage_Rendered_by_Javascript_Using_Python.php

SHAPES = ['H', 'C', 'T', 'S']

def getSolution(thesolutions):
    result = ""
    for solution in thesolutions:
        for move in solution:
            if (move[0] == 'G'):
                result += "blue "
            elif (move[0] == 'Y'):
                result += "yellow "
            elif (move[0] == 'B'):
                result += "red "
            elif (move[0] == 'R'):
                result += "green "
            if (move[1] == 'N'):
                result += "up "
            elif (move[1] == 'S'):
                result += "down "
            elif (move[1] == 'E'):
                result += "right "
            elif (move[1] == 'W'):
                result += "left "
        result = result[:-1]
        result += '\n'
    linedata = result.splitlines() #split lines by \n
    z, v = 30, 5
    solutions = [["" for x in range(z)] for y in range(v)]
    for x, line in enumerate(linedata):
        liner = line.split(" ") #split lines by whitespace
        for y, line2 in enumerate(liner):
            solutions[x][y] = line2
    return solutions

def createStorePost(solutions, goals):
    arraysolutions = [{} for n in range(5)]
    for x, solutionNum in enumerate(solutions):
        arraysolutions[x] = {"solution": [], "goal": goals[x], "goalColor": goals[x][2]}
        for lineNum in solutionNum:
            if '' != lineNum:
                arraysolutions[x]['solution'] += [lineNum]
    return arraysolutions


def getHighscore(high):
    scoretocheck = "<td>" + str(high) + "</td>"
    browser = webdriver.Chrome()
    getURL = "http://www.robotreboot.com/highscore"
    browser.get(getURL)
    html = browser.page_source
    browser.close()
    if scoretocheck in html:
        return 1
    else:
        return 0


def getHeaders():
    headers = {
        "Connection": "keep-alive",
        "Content-length": 16,
        "Content-type": "application/json; charset=utf-8",
        "Date": datetime.datetime.now(),
        "Etag": "W/\"10-oV4hJxRVSENxc/wX8+mA4/Pe4tA\"",
        "Server": "Cowboy",
        "Via": "1.1 vegur",
        "X-Powered-By": "Express"
    }
    return headers


def findLeftWalls(boardData, width, height):
    walls = [["" for n in range(16)] for x in range(16)]
    xNumPixelsPerSquare = int(height / 16)
    yNumPixelsPerSquare = int(width / 16)
    Horoffset = 3 * width * 4  # offset to put "line to check" in middle of squares
    Veroffset = 0  # 3*4
    for row in range(16):
        for column in range(16):
            if boardData[
               (row * width * 4 * yNumPixelsPerSquare + column * xNumPixelsPerSquare * 4 + Horoffset + Veroffset):(
                       row * width * 4 * yNumPixelsPerSquare + column * 4 * xNumPixelsPerSquare + 4 + Veroffset + Horoffset)] == [
                0, 0, 0, 255]:
                walls[row][column] += 'W'
                if column > 0:
                    walls[row][column-1] += 'E'
    return walls


def postDiscord(moves):
    # system library for getting the command line argument
    # your webhook URL
    webhookurl = "https://discordapp.com/api/webhooks/534861126723174400/AVmFD9SmF3_xoqXTCLbX08Bhp3MHKDjQ690DKvBY0_oUQZxIy_lHGjT9Tmz4XLOzXxD6"

    # compile the form data (BOUNDARY can be anything)
    formdata = "------:::BOUNDARY:::\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + moves + "\r\n------:::BOUNDARY:::--"

    # get the connection and make the request
    connection = http.client.HTTPSConnection("discordapp.com")
    connection.request("POST", webhookurl, formdata, {
        'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
        'cache-control': "no-cache",
    })
    # get the response
    response = connection.getresponse()
    result = response.read()
    # return back to the calling function with the result
    return result.decode("utf-8")


def findUpWalls(leftwalls, boardData, width, height):
    xNumPixelsPerSquare = int(height / 16)
    yNumPixelsPerSquare = int(width / 16)
    Horoffset = 0  # offset to put "line to check" in middle of squares
    Veroffset = int(xNumPixelsPerSquare / 2) * 4  # 20*4
    for row in range(16):
        for column in range(16):
            if boardData[
               (row * width * 4 * yNumPixelsPerSquare + column * xNumPixelsPerSquare * 4 + Horoffset + Veroffset):(
                       row * width * 4 * yNumPixelsPerSquare + column * 4 * xNumPixelsPerSquare + 4 + Veroffset + Horoffset)] == [
                0, 0, 0, 255]:
                leftwalls[row][column] += 'N'
                if row > 0:
                    leftwalls[row-1][column] += 'S'
    return leftwalls


def convertstringcolor(string):
    val = ""
    if "green" in string:
       val = 'H'
    elif "yellow" in string:
        val = 'C'
    elif "red" in string:
        val = 'S'
    else:
        val = 'T'
    return val


#0 = upper left  1 = upper right 2 = lower left 3 = lower right
def getQuads(wallarray, goals):
    quads = [["" for n in range(4)] for x in range(5)]
    for z, board in enumerate(wallarray):
        for y, row in enumerate(board):
            for x, column in enumerate(row):
                if y < 8 and x < 8:
                    quads[z][0] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][0] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][0] += ','
                elif y < 8 and x >= 8:
                    quads[z][1] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][1] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][1] += ','
                elif y >= 8 and x < 8:
                    quads[z][2] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][2] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][2] += ','
                else:
                    quads[z][3] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][3] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][3] += ','


    for x, quad in enumerate(quads):
        for y, lists in enumerate(quad):
            quads[x][y] = lists[:-1]
    print(quads)
    return quads

def getBoards(walls,robits,goals):
    for robot in robits:
        posx = robot[0]
        posy = robot[1]
        if "green" in robot[2]:
            col = 'G'
        elif "red" in robot[2]:
            col = 'R'
        elif "yellow" in robot[2]:
            col = 'Y'
        elif "blue" in robot[2]:
            col = 'B'
        else:
            col = 'X'
        if walls[posx][posy] == 'X':
            walls[posx][posy] = col
        else:
            walls[posx][posy] += col
    wallarray = [walls for n in range(5)]
    boardQuads = getQuads(wallarray, goals)
    return boardQuads


def sendData(postresponse):
    jsondump = json.dumps(postresponse)
    jsondata = json.loads(jsondump)
    reqpost = requests.post(url=urlpost, json=jsondata)
    print(reqpost)


def getCanvasData():
    browser = webdriver.Chrome()
    getURL = "http://www.robotreboot.com/challenge"
    browser.get(getURL)
    javascript = "canv = document.querySelector(\"canvas\"); canv2D = canv.getContext(\"2d\"); return canv2D.getImageData(0,0,canv.width,canv.height);"
    newdata = browser.execute_script(javascript)
    browser.close()
    return newdata


def getConfig():
    URL = "http://www.robotreboot.com/challenge/config"
    rget = requests.get(url=URL, params="")
    return rget.json()


def getWalls(boardData):
    leftwalls = findLeftWalls(boardData['data'], boardData['width'], boardData['height'])
    upwalls = findUpWalls(leftwalls, boardData['data'], boardData['width'], boardData['height'])
    for x, array in enumerate(upwalls):
        for y, attribute in enumerate(array):
            if y == 15:
                leftwalls[x][y] += 'E'
            if x == 15:
                leftwalls[x][y] += 'S'
            if attribute == '' and x != 15 and y != 15:
                leftwalls[x][y] = 'X'
    return leftwalls


def getRobots(robits):
    result = [int for n in range(4)]
    for x, robot in enumerate(robits):
        result[x] = robot[1] + robot[0] * 16
    return result

def placeGoals(grid,goals):
    green,yellow,red,blue = 0,0,0,0
    result = ["" for n in range(5)]
    for x, goal in enumerate(goals):
        if "green" in goal[2]:
            colshape = 'G'
            colshape += SHAPES[green]
            green += 1
        elif "red" in goal[2]:
            colshape = 'R'
            colshape += SHAPES[red]
            red += 1
        elif "yellow" in goal[2]:
            colshape = 'Y'
            colshape += SHAPES[yellow]
            yellow += 1
        elif "blue" in goal[2]:
            colshape = 'B'
            colshape += SHAPES[blue]
            blue += 1
        result[x] = colshape
        grid[goal[1] + goal[0]*16] += colshape
    return result


def callback():
    return


oldconfig = getConfig()['config']
humans = 4
robotscores = 0

while 1:
    try:
        counter = 0
        time.sleep(15)
        while (datetime.datetime.now().hour != 15 or datetime.datetime.now().minute != 59 or datetime.datetime.now().second < 55):
            time.sleep(3)
        while (getConfig()['config'] == oldconfig):
            time.sleep(.5)
            counter += 1
            if (counter > 200):
                time.sleep(600)
        boardData = getCanvasData()
        walls = getWalls(boardData)
        data = getConfig()
        urlpost = "http://www.robotreboot.com/challenge/submission"
        config = data['config']
        oldconfig = config
        challengeID = data['challengeId']
        goals = data['goals']
        robots = data['robots']
        # sort
        for x in range(4):
            if "green" in robots[x][2]:
                green = robots[x]
            elif "yellow" in robots[x][2]:
                yellow = robots[x]
            elif "blue" in robots[x][2]:
                blue = robots[x]
            elif "red" in robots[x][2]:
                red = robots[x]
        robots[0] = green
        robots[1] = blue
        robots[2] = red
        robots[3] = yellow

        print(walls)
        print(robots)
        print(goals)

        grid = []
        for wall in walls:
            grid += wall
        robits = getRobots(robots)
        listTokens = placeGoals(grid, goals)
        colorz = ['' for n in range(4)]
        for x, robot in enumerate(robots):
            if "green" in robot[2]:
                colorz[x] = 'G'
            elif "red" in robot[2]:
                colorz[x] = 'R'
            elif "yellow" in robot[2]:
                colorz[x] = 'Y'
            elif "blue" in robot[2]:
                colorz[x] = 'B'
        # model.Game(grid=grid, robots=robits, token=listTokens[0])
        paths = [[] for n in range(5)]
        for x, tokenz in enumerate(listTokens):
            print('answers')
            print(grid)
            print(robits)
            print(colorz)
            print(tokenz)
            print('**************************************')
            paths[x] = ricochet.search(model.Game(grid=grid, robots=robits, col=colorz, token=tokenz))
        print(paths)

        totalMoves = 0
        for path in paths:
            totalMoves += len(path)

        print(totalMoves)
        winner = getHighscore(totalMoves)
        if winner==1:
            humans+=1
        else:
            robotscores+=1
        print(humans)
        print(robotscores)
        solutions = getSolution(paths)
        arraysolutions = createStorePost(solutions, goals)
        name = "[🤖] humans: " + str(humans) + " robots: " + str(robotscores)
        postresponse = {
            "remainingPuzzle": 0,
            "totalMoves": totalMoves,
            "store": arraysolutions,
            "config": config,
            "challengeId": challengeID,
            "name": name
        }
        print(postresponse)
        postDiscord(solutions)
        #sendData(postresponse)
    finally:
        pass








