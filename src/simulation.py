import math
import utilityclasses.GridObject as GridObject
import utilityclasses.SimArray as SimArray
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


def genTestGrid(testNum: int = 1):
    return (
        SimArray.SimArray(tg.getTestGrid(testNum))
        if tg.getTestGrid(testNum)
        else SimArray.SimArray([[0 for x in range(40)] for y in range(40)])
    )


# v is for velocity numbers displayed and d is for density numbers displayed
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
                quadratic_density = normalized_density**2  # quadratic interpolation
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
                                            (
                                                "stringValue"
                                                if data == "v"
                                                else "numberValue"
                                            ): data_val
                                        },
                                    }
                                ]
                            }
                        ],
                        "fields": (
                            "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.fontSize,userEnteredValue.stringValue"
                            if data == "v"
                            else "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.fontSize,userEnteredValue.numberValue"
                        ),
                    }
                }
            )

    body = {"requests": requests}
    return body, sim


def updateSheetFromBody(
    service, SPREADSHEET_ID, body
):  # this sends the data to the spreadsheets
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body
    )
    response = request.execute()
    return response


def runSim(init_sim: SimArray, verbose=False):
    sim = init_sim.copy()
    total_density_before = np.sum([[cell.Density for cell in row] for row in sim])

    # Create a copy of the densities and velocities to update
    new_densities = np.array(
        [[cell.Density for cell in row] for row in sim], dtype=float
    )
    new_ux = np.array([[cell.ux for cell in row] for row in sim], dtype=float)
    new_uy = np.array([[cell.uy for cell in row] for row in sim], dtype=float)

    # Distribute fluid
    for x in range(40):
        for y in range(40):
            cur_density = sim[x][y].Density
            cur_ux = sim[x][y].ux
            cur_uy = sim[x][y].uy
            max_spill = cur_density * 0.75
            if max_spill > 0:
                # Calculate the amount to distribute to each neighbor
                neighbors = []
                if x > 0:
                    neighbors.append((x - 1, y))
                if x < 39:
                    neighbors.append((x + 1, y))
                if y > 0:
                    neighbors.append((x, y - 1))
                if y < 39:
                    neighbors.append((x, y + 1))

                total_difference = sum(
                    max(cur_density - sim[nx][ny].Density, 0) for nx, ny in neighbors
                )
                if total_difference > 0:
                    for nx, ny in neighbors:
                        difference = max(cur_density - sim[nx][ny].Density, 0)
                        direction_factor = 1.0
                        if nx == x + 1:
                            direction_factor += cur_ux
                        elif nx == x - 1:
                            direction_factor -= cur_ux
                        if ny == y + 1:
                            direction_factor += cur_uy
                        elif ny == y - 1:
                            direction_factor -= cur_uy
                        direction_factor = max(
                            direction_factor, 0
                        )  # Ensure non-negative

                        spill_amount = (
                            max_spill
                            * (difference / total_difference)
                            * 0.25
                            * direction_factor
                        )
                        if verbose:
                            print(
                                f"Spilling {spill_amount} from ({x}, {y}) to ({nx}, {ny})"
                            )
                        if verbose:
                            print(
                                f"Before: {new_densities[x][y]}, {new_densities[nx][ny]}"
                            )
                        new_densities[nx][ny] += spill_amount
                        new_densities[x][y] -= spill_amount
                        if verbose:
                            print(
                                f"After: {new_densities[x][y]}, {new_densities[nx][ny]}"
                            )

                        # Transfer velocities along with the fluid
                        new_ux[nx][ny] = (
                            new_ux[nx][ny] * sim[nx][ny].Density + cur_ux * spill_amount
                        ) / new_densities[nx][ny]
                        new_uy[nx][ny] = (
                            new_uy[nx][ny] * sim[nx][ny].Density + cur_uy * spill_amount
                        ) / new_densities[nx][ny]

                        # Introduce velocity based on density difference (potential energy to kinetic energy conversion)
                        velocity_introduction = math.sqrt(
                            difference
                        )  # Simplified conversion
                        if nx == x + 1:
                            new_ux[nx][ny] += velocity_introduction
                        elif nx == x - 1:
                            new_ux[nx][ny] -= velocity_introduction
                        if ny == y + 1:
                            new_uy[nx][ny] += velocity_introduction
                        elif ny == y - 1:
                            new_uy[nx][ny] -= velocity_introduction

                        # Handle cells next to walls by redirecting velocity
                        if nx == 0 and new_ux[nx][ny] < 0:
                            new_ux[nx][ny] = -new_ux[nx][ny]
                        elif nx == 39 and new_ux[nx][ny] > 0:
                            new_ux[nx][ny] = -new_ux[nx][ny]
                        if ny == 0 and new_uy[nx][ny] < 0:
                            new_uy[nx][ny] = -new_uy[nx][ny]
                        elif ny == 39 and new_uy[nx][ny] > 0:
                            new_uy[nx][ny] = -new_uy[nx][ny]

    # Update the densities and velocities in the simulation
    for x in range(40):
        for y in range(40):
            sim[x][y].Density = new_densities[x][y]
            sim[x][y].ux = new_ux[x][y]
            sim[x][y].uy = new_uy[x][y]

    total_density_after = np.sum([[cell.Density for cell in row] for row in sim])
    assert np.isclose(
        total_density_before, total_density_after
    ), "Density is not conserved!"

    return sim


# TEST_GRID_ID = 7
# DATA_DISPLAY_TYPE = "v"
# COLOR_INTERPOLATION = "l"
# VERBOSE = True


def main(
    creds,
    SPREADSHEET_ID,
    GRID_RANGE: str = "Grid!A1:AN40",
    TEST_GRID_ID: int = 7,
    DATA_DISPLAY_TYPE: str = "v",
    COLOR_INTERPOLATION: str = "l",
    VERBOSE_VAL: bool = True,
):
    print(f"Using range: {GRID_RANGE} on spreadsheet {SPREADSHEET_ID}")
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=GRID_RANGE).execute()
    )
    values = result.get("values", [])
    if not values:
        print("No data found.")
        return

    test_grid = genTestGrid(TEST_GRID_ID)

    while True:
        time.sleep(1)
        test_grid = runSim(test_grid, VERBOSE_VAL)
        body, test_grid = genBodyFromSim(
            test_grid, COLOR_INTERPOLATION, DATA_DISPLAY_TYPE
        )
        updateSheetFromBody(service, SPREADSHEET_ID, body)
