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
import numpy as np
import time


CLIENT_SECRET_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# LBM parameters
tau = 0.6  # Relaxation time
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

def genTestGrid(testNum: int = 1):
    if testNum == 1:
        # Example grid where there is a wave shape (sinusoidal) within the top 10 rows of the grid, with densities ranging from 0 to 100.
        return SimArray.SimArray([[math.sin(y/10*math.pi)*50+50 if y < 10 else 0 for x in range(40)] for y in range(40)])
    elif testNum == 2:
        # Example grid where is an apple logo shape within the grid, with densities ranging from 0 to 100.
        apple_logo = [[0] * 40 for _ in range(40)]
        # Left part of the apple
        for i in range(5, 15):
            for j in range(10, 30):
                apple_logo[i][j] = 100

        # Right part of the apple
        for i in range(10, 25):
            for j in range(20, 30):
                apple_logo[i][j] = 100

        # Top part (stem and curve of the apple)
        for i in range(2, 10):
            for j in range(4, 10):
                apple_logo[i][j] = 100

        # Bottom of the apple (rounded shape)
        for i in range(18, 25):
            for j in range(15, 20):
                apple_logo[i][j] = 100
        return SimArray.SimArray(apple_logo)
    else:
        return SimArray.SimArray([[0 for x in range(40)] for y in range(40)])

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
    if verbose >= 1:
        print(f"Total density before: {total_density_before}")
    # Create a copy of the densities to update
    new_densities = np.array([[cell.Density for cell in row] for row in sim])

    # Distribute fluid
    for x in range(40):
        for y in range(40):
            cur_density = sim[x][y].Density
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
                        spill_amount = max_spill * (difference / total_difference) * 0.25
                        if verbose >= 2:
                            print(f"Spilling {spill_amount} from ({x}, {y}) to ({nx}, {ny})")
                        if verbose >= 3:
                            print(f"Before: {new_densities[x][y]}, {new_densities[nx][ny]}")
                        new_densities[nx][ny] += spill_amount
                        new_densities[x][y] -= spill_amount
                        if verbose >= 3:
                            print(f"After: {new_densities[x][y]}, {new_densities[nx][ny]}")

    # Update the densities in the simulation
    for x in range(40):
        for y in range(40):
            sim[x][y].Density = new_densities[x][y]

    total_density_after = np.sum([[cell.Density for cell in row] for row in sim])
    if verbose >= 1:
        print(f"Total density after: {total_density_after}")
    #assert np.isclose(total_density_before, total_density_after), "Density is not conserved!"

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
    
    test_grid = genTestGrid(2)
    
    while True:
        time.sleep(2)  # Small time step to observe patterns
        test_grid = runSim(test_grid, 0)
        body, test_grid = genBodyFromSim(test_grid)
        updateSheetFromBody(service, SPREADSHEET_ID, body)