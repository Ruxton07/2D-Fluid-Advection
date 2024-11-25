import os.path
import sys
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
TEST_GRID_ID = 4

# LBM parameters
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

def genTestGrid(testNum: int = 1):
    return SimArray.SimArray(tg.getTestGrid(testNum)) if tg.getTestGrid(testNum) else SimArray.SimArray([[0 for x in range(40)] for y in range(40)])
def equilibrium(density, ux, uy):
    feq = np.zeros(9)
    for i, (cx, cy) in enumerate(velocities):
        cu = cx * ux + cy * uy
        feq[i] = (
            weights[i] * density * (1 + 3 * cu + 4.5 * cu**2 - 1.5 * (ux**2 + uy**2))
        )
    return feq


def genBodyFromSim(sim: SimArray, interpolation: str = "l"):
    requests = []
    for i in range(sim.len()):
        for j in range(len(sim[0])):
            density = min(sim[i][j].Density, 100)
            color = {}
            if interpolation == "l":
                color = {
                    "red": density / 100,
                    "green": 0,
                    "blue": (100 - density) / 100,
                }
            elif interpolation == "q":
                normalized_density = density / 100
                quadratic_density = normalized_density ** 2  # Quadratic interpolation
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
                                            "numberValue": round(density)
                                        },
                                    }
                                ]
                            }
                        ],
                        "fields": "userEnteredFormat.backgroundColor,userEnteredValue.numberValue",
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


def runSim(init_sim: SimArray, verbose=0):
    sim = init_sim.copy()
    total_density_before = np.sum([[cell.Density for cell in row] for row in sim])

    # Create a copy of the densities and velocities to update
    new_densities = np.array([[cell.Density for cell in row] for row in sim], dtype=float)
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
                        direction_factor = max(direction_factor, 0)  # Ensure non-negative

                        spill_amount = max_spill * (difference / total_difference) * 0.25 * direction_factor
                        if verbose >= 2:
                            print(f"Spilling {spill_amount} from ({x}, {y}) to ({nx}, {ny})")
                        if verbose >= 3:
                            print(f"Before: {new_densities[x][y]}, {new_densities[nx][ny]}")
                        new_densities[nx][ny] += spill_amount
                        new_densities[x][y] -= spill_amount
                        if verbose >= 3:
                            print(f"After: {new_densities[x][y]}, {new_densities[nx][ny]}")

                        # Update velocities based on pressure differences
                        pressure_difference = spill_amount
                        new_ux[x][y] -= pressure_difference * (nx - x)
                        new_uy[x][y] -= pressure_difference * (ny - y)
                        new_ux[nx][ny] += pressure_difference * (nx - x)
                        new_uy[nx][ny] += pressure_difference * (ny - y)

    # Update the densities and velocities in the simulation
    for x in range(40):
        for y in range(40):
            sim[x][y].Density = new_densities[x][y]
            sim[x][y].ux = new_ux[x][y]
            sim[x][y].uy = new_uy[x][y]

    total_density_after = np.sum([[cell.Density for cell in row] for row in sim])
    assert np.isclose(total_density_before, total_density_after), "Density is not conserved!"

    return sim


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
    
    test_grid = genTestGrid(TEST_GRID_ID)
    
    while True:
        time.sleep(1)  # Small time step to observe patterns
        test_grid = runSim(test_grid, 0)
        body, test_grid = genBodyFromSim(test_grid)
        updateSheetFromBody(service, SPREADSHEET_ID, body)