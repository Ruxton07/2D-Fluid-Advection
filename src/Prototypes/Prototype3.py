import os.path
import sys
import math
import utilityclasses.GridObject as GridObject
import utilityclasses.SimArray as SimArray
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from time import sleep
import numpy as np

CLIENT_SECRET_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]
EPOCH_STEPS = 20

# LBM parameters
tau = 0.9  # Relaxation time
c_sqr = 1 / 3  # Speed of sound squared
weights = [4 / 9] + [1 / 9] * 4 + [1 / 36] * 4  # Weights for the D2Q9 model
velocities = [
    (0, 0),
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
    (1, 1),
    (-1, 1),
    (-1, -1),
    (1, -1),
]  # Lattice velocities


def equilibrium(density, ux, uy):
    feq = []
    for i, (cx, cy) in enumerate(velocities):
        cu = cx * ux + cy * uy
        feq.append(
            weights[i] * density * (1 + 3 * cu + 4.5 * cu**2 - 1.5 * (ux**2 + uy**2))
        )
    return feq


def runSim(sim_archive: SimArray, verbose=0):
    sim = sim_archive.copy()
    f = [
        [[0 for _ in range(9)] for _ in range(40)] for _ in range(40)
    ]  # Distribution functions
    feq = [
        [[0 for _ in range(9)] for _ in range(40)] for _ in range(40)
    ]  # Equilibrium distribution functions

    # Initialize distribution functions
    for x in range(40):
        for y in range(40):
            density = sim[x][y].Density
            feq[x][y] = equilibrium(density, 0, 0)
            f[x][y] = feq[x][y][:]

    for step in range(EPOCH_STEPS):
        # Collision step
        for x in range(40):
            for y in range(40):
                density = sum(f[x][y])
                if density > 0:
                    ux = sum(f[x][y][i] * velocities[i][0] for i in range(9)) / density
                    uy = sum(f[x][y][i] * velocities[i][1] for i in range(9)) / density
                else:
                    ux, uy = 0, 0
                feq[x][y] = equilibrium(density, ux, uy)
                for i in range(9):
                    f[x][y][i] += -(f[x][y][i] - feq[x][y][i]) / tau

        # Streaming step
        f_new = [[[0 for _ in range(9)] for _ in range(40)] for _ in range(40)]
        for x in range(40):
            for y in range(40):
                for i, (cx, cy) in enumerate(velocities):
                    nx, ny = (x + cx) % 40, (y + cy) % 40
                    f_new[nx][ny][i] = f[x][y][i]
        f = f_new

        # Update macroscopic variables
        for x in range(40):
            for y in range(40):
                sim[x][y].Density = min(
                    max(round(sum(f[x][y])), 0), 100
                )  # Ensure density is within 0 to 100

    return sim


def genBodyFromSim(sim: SimArray, interpolation: str = "l", data: str = "d"):
    requests = []
    for i in range(sim.len()):
        for j in range(len(sim[0])):
            density = min(sim[i][j].Density, 100)
            data_val = 0
            font_size = 7 if data == "d" else 10
            match data:
                case "d":
                    data_val = round(density)
                case "vx":
                    data_val = sim[i][j].ux
                case "vy":
                    data_val = sim[i][j].uy
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
                                        "userEnteredFormat": {
                                            "backgroundColor": color,
                                            "textFormat": {"fontSize": font_size},
                                        },
                                        "userEnteredValue": {
                                            "stringValue" if data == "v" else "numberValue": data_val
                                        },
                                    }
                                ]
                            }
                        ],
                        "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.fontSize,userEnteredValue.stringValue" if data == "v" else "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.fontSize,userEnteredValue.numberValue",
                    }
                }
            )

    body = {"requests": requests}
    return body, sim

def updateSheetFromBody(service, SPREADSHEET_ID, body):
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body
    )
    response = request.execute()
    return response


def main(creds, SPREADSHEET_ID, GRID_RANGE):
    print(f"Using range: {GRID_RANGE} on spreadsheet {SPREADSHEET_ID}")
    service = build("sheets", "v4", credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=GRID_RANGE).execute()
    )
    values = result.get("values", [])
    if not values:
        print("No data found.")
        return

    # Example grid where the entire top row is density = 100 and the rest is 0
    test_grid_1 = SimArray.SimArray(
        [[100 if y == 0 else 0 for x in range(40)] for y in range(40)]
    )
    # Example grid where the middle column (19) is 100, as well as the entire middle row (19) is 100. This should look like a plus sign.
    test_grid_2 = SimArray.SimArray(
        [[100 if x == 19 or y == 19 else 0 for x in range(40)] for y in range(40)]
    )
    # Example grid where the there is a wave shape (sinusoidal) within the top 10 rows of the grid, with densities ranging from 0 to 100.
    test_grid_3 = SimArray.SimArray(
        [
            [math.sin(x / 10 * math.pi) * 50 + 50 if y < 10 else 0 for x in range(40)]
            for y in range(40)
        ]
    )
    genBodyFromSim(test_grid_3)
    for i in range(EPOCH_STEPS):
        sleep(3)
        print(f"===================={i+1}====================")
        body, test_grid_3 = genBodyFromSim(runSim(test_grid_3, 2))
        updateSheetFromBody(service, SPREADSHEET_ID, body)
    return values
