import math
import utilityclasses.GridObject as GridObject
import utilityclasses.SimArray as SimArray
import utilityclasses.Field2D as f2d
import testgrids as tg
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import numpy as np
import time


CLIENT_SECRET_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

TEST_GRID_ID = 7
DATA_DISPLAY_TYPE = "v"
COLOR_INTERPOLATION = "l"
VERBOSE_VAL = 3

def genTestGrid(testNum: int = 1):
    return SimArray.SimArray(tg.getTestGrid(testNum)) if tg.getTestGrid(testNum) else SimArray.SimArray([[0 for x in range(40)] for y in range(40)])

def sum(a):
    s = 0
    for e in a:
        s = s + e
    return s

def genBodyFromSim(sim: SimArray, interpolation: str = "l", data: str = "d"):
    requests = []
    for i in range(sim.len()):
        for j in range(len(sim[0])):
            density = min(sim[i][j].Density, 100)
            data_val = 0
            match data:
                case "d":
                    data_val = density
                case "vx":
                    data_val = sim[i][j].ux, 100
                case "vy":
                    data_val = sim[i][j].uy, 100
                case "v":
                    ux = sim[i][j].ux
                    uy = sim[i][j].uy
                    if ux > 0 and uy > 0:
                        data_val = "↗"  # Up and to the right
                    elif ux < 0 and uy > 0:
                        data_val = "↖"  # Up and to the left
                    elif ux > 0 and uy < 0:
                        data_val = "↘"  # Down and to the right
                    elif ux < 0 and uy < 0:
                        data_val = "↙"  # Down and to the left
                    elif ux > 0 and uy == 0:
                        data_val = "→"  # Right
                    elif ux < 0 and uy == 0:
                        data_val = "←"  # Left
                    elif ux == 0 and uy > 0:
                        data_val = "↑"  # Up
                    elif ux == 0 and uy < 0:
                        data_val = "↓"  # Down
                    else:
                        data_val = "•"  # No movement
                case "_":
                    data_val = ""
            color = {}
            if interpolation == "l":
                color = {
                    "red": density / 100,
                    "green": 0,
                    "blue": (100 - density) / 100,
                }
            elif interpolation == "q":
                normalized_density = density / 100
                quadratic_density = normalized_density ** 2  # quadratic interpolation
                color = {
                    "red": quadratic_density,
                    "green": 0,
                    "blue": 1 - quadratic_density,
                }
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": i,
                            "endRowIndex": i + 1,
                            "startColumnIndex": j,
                            "endColumnIndex": j + 1,
                        },
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredFormat": {"backgroundColor": color},
                                        "userEnteredValue": {
                                            "stringValue" if data == "v" else "numberValue": data_val
                                        },
                                    }
                                ]
                            }
                        ],
                        "fields": "userEnteredFormat.backgroundColor,userEnteredValue.stringValue" if data == "v" else "userEnteredFormat.backgroundColor,userEnteredValue.numberValue",
                    }
                }
            )

    body = {"requests": requests}
    return body, sim

def updateSheetFromBody(service, SPREADSHEET_ID, body): #this sends the data to the spreadsheets
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body
    )
    response = request.execute()
    return response

Weights = [1 / 36, 1 / 9, 1 / 36, 1 / 9, 4 / 9, 1 / 9, 1 / 36, 1 / 9, 1 / 36]
DiscreteVelocityVectors = [
    [-1, 1],
    [0, 1],
    [1, 1],
    [-1, 0],
    [0, 0],
    [1, 0],
    [-1, -1],
    [0, -1],
    [1, -1],
]

res = 100
a = f2d.Field2D(res)
velocityField = []
for DummyVariable in range(res):
    DummyList = []
    for DummyVariable2 in range(res):
        DummyList.append([0, 0])
    velocityField.append(DummyList[:])
DensityField = []
for DummyVariable in range(res):
    DummyList = []
    for DummyVariable2 in range(res):
        DummyList.append(1)
    DensityField.append(DummyList[:])
DensityField[50][50] = 2
DensityField[40][50] = 2
MaxSteps = 120
SpeedOfSound = 1 / math.sqrt(3)
TimeRelaxationConstant = 0.5
for s in range(MaxSteps):
    df = f2d.Field2D(res)
    for y in range(res):
        for x in range(res):
            for v in range(9):
                Velocity = a.field[y][x][v]
                FirstTerm = Velocity
                FlowVelocity = velocityField[y][x]
                Dotted = (
                    FlowVelocity[0] * DiscreteVelocityVectors[v][0]
                    + FlowVelocity[1] * DiscreteVelocityVectors[v][1]
                )
                taylor = (
                    1
                    + ((Dotted) / (SpeedOfSound**2))
                    + ((Dotted**2) / (2 * SpeedOfSound**4))
                    - (
                        (FlowVelocity[0] ** 2 + FlowVelocity[1] ** 2)
                        / (2 * SpeedOfSound**2)
                    )
                )
                density = DensityField[y][x]
                equilibrium = density * taylor * Weights[v]
                SecondTerm = (equilibrium - Velocity) / TimeRelaxationConstant
                df.field[y][x][v] = FirstTerm + SecondTerm
    for y in range(0, res):
        for x in range(0, res):
            for v in range(9):
                TargetY = y + DiscreteVelocityVectors[v][1]
                TargetX = x + DiscreteVelocityVectors[v][0]
                if TargetY == res and TargetX == res:
                    a.field[TargetY - res][TargetX - res][v] = df.field[y][x][v]
                elif TargetX == res:
                    a.field[TargetY][TargetX - res][v] = df.field[y][x][v]
                elif TargetY == res:
                    a.field[TargetY - res][TargetX][v] = df.field[y][x][v]
                elif TargetY == -1 and TargetX == -1:
                    a.field[TargetY + res][TargetX + res][v] = df.field[y][x][v]
                elif TargetX == -1:
                    a.field[TargetY][TargetX + res][v] = df.field[y][x][v]
                elif TargetY == -1:
                    a.field[TargetY + res][TargetX][v] = df.field[y][x][v]
                else:
                    a.field[TargetY][TargetX][v] = df.field[y][x][v]
    for y in range(res):
        for x in range(res):
            DensityField[y][x] = sum(a.field[y][x])
            FlowVelocity = [0, 0]
            for DummyVariable in range(9):
                FlowVelocity[0] = (
                    FlowVelocity[0]
                    + DiscreteVelocityVectors[DummyVariable][0]
                    * a.field[y][x][DummyVariable]
                )
            for DummyVariable in range(9):
                FlowVelocity[1] = (
                    FlowVelocity[1]
                    + DiscreteVelocityVectors[DummyVariable][1]
                    * a.field[y][x][DummyVariable]
                )
            FlowVelocity[0] = FlowVelocity[0] / DensityField[y][x]
            FlowVelocity[1] = FlowVelocity[1] / DensityField[y][x]
            velocityField[y][x] = FlowVelocity
    f2d.VisualizeField(a, 128, 100, velocityField)



