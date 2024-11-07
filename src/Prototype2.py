import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from time import sleep

import sys
import math
import GridObject
import SimArray


CLIENT_SECRET_FILE = "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]
EPOCH_STEPS = 10


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
    test_grid_1 = SimArray.SimArray([[100 if y == 0 else 0 for x in range(40)] for y in range(40)])
    # Example grid where the middle column (19) is 100, as well as the entire middle row (19) is 100. This should look like a plus sign.
    test_grid_2 = SimArray.SimArray([[100 if x == 19 or y == 19 else 0 for x in range(40)] for y in range(40)])
    # Example grid where the there is a wave shape (sinusoidal) within the top 10 rows of the grid, with densities ranging from 0 to 100.
    test_grid_3 = SimArray.SimArray([[math.sin(x/10*math.pi)*50+50 if y < 10 else 0 for x in range(40)] for y in range(40)])
    genBodyFromSim(test_grid_3)
    for i in range(EPOCH_STEPS):
        sleep(3)
        print(f"===================={i+1}====================")
        body, test_grid_3 = genBodyFromSim(runSim(test_grid_3, 2))
        updateSheetFromBody(service, SPREADSHEET_ID, body)
    return values

def runSim(sim_archive: SimArray, verbose=0):
    sim = sim_archive.copy()
    #print(f"sim: {sim}")
    #print(f"sim_archive: {sim_archive}")
    #print(sim_archive.printIndices())
    #print(f"-----{sim_archive[0][0].Density}---{sim_archive[0][1].Density}-----")
    # Assuming Density, IsLand, Current, x, y, grid, and land_grid are defined elsewhere
    for x in range(sim_archive.len()):
        for y in range(len(sim_archive[0])):
            cur_density = sim_archive[x][y].Density
            max_spill = cur_density * 0.75 if cur_density else 0
            if x==0 and verbose > 1:
                print(f"X: {x} and y: {y} and sim_archive[x][y]: {sim_archive[x][y]} and Cur density: {cur_density} and max spill: {max_spill}")

            if max_spill > 0:
                #print(f"Spilling {max_spill} from {x}, {y}")
                if verbose > 2:
                    print(f"Adjacent nodes: {sim_archive[x - 1][y] if x > 0 else None}, {sim_archive[x + 1][y] if x < sim_archive.len() - 1 else None}, {sim_archive[x][y - 1] if y > 0 else None}, {sim_archive[x][y + 1] if y < len(sim_archive[0]) - 1 else None}")
                grid_left = sim_archive[x - 1][y] if x > 0 else None
                grid_right = sim_archive[x + 1][y] if x < sim_archive.len() - 1 else None
                grid_down = sim_archive[x][y - 1] if y > 0 else None
                grid_up = sim_archive[x][y + 1] if y < len(sim_archive[0]) - 1 else None
                adjacent_nodes = [grid_left, grid_right, grid_down, grid_up]

                for node in adjacent_nodes:
                    #print("\n")
                    #print(node, node.index if node else None)
                    #print(node.Density+max_spill/4 if node else None)
                    if verbose > 3:
                        print(f"Node density: {node.Density if node else None}")
                        print(f"Cur density: {cur_density}")
                        print(type(node))
                        print(type(node.Density) if node else None)
                    if type(node) is GridObject.GridObject and (node.Density < cur_density): # and (node.Density + max_spill / 4) <= cur_density
                        if node.index[0] == 0 or node.index[0] == 1:
                            #print(node.Density)
                            #print(max_spill)
                            print(f"Spilling {max_spill / 4} to {node.index}")

                        sim[node.index[0]][node.index[1]].Density += max_spill / 4
                        if verbose > 2:
                            print(f"node index: {node.index} is now {sim[node.index[0]][node.index[1]].Density}")
                        #print(sim[x][y].index)
                        #if x == 0 and y <=3:
                            #print(sim_archive)
                        sim[x][y].Density -= max_spill / 4
                        #print(sim_archive[0][1].Density)
                        #if x == 0 and y <=3:
                            #print(sim_archive)
    if verbose > 0:
        print(sim)
    return sim

# The sim dict passed to genBodyFromSim is the output of runSim, which means it's a 2D array of GridObjects where
# .Density can be used to access the density of the grid at that point. The color of each grid cell is determined
# by a linear gradient (interpolation) from blue to red, where blue is low density (0) and red is the high density (100).
# Remember, cell values will always be from 0 to 100.
def genBodyFromSim(sim: SimArray):
    requests = []
    for i in range(sim.len()):
        for j in range(len(sim[0])):
            density = sim[i][j].Density
            color = {
                "red": density/100,
                "green": 0,
                "blue": (100 - density)/100,
            }
            requests.append({
                "updateCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": i,
                        "endRowIndex": i + 1,
                        "startColumnIndex": j,
                        "endColumnIndex": j + 1,
                    },
                    "rows": [{
                        "values": [{
                            "userEnteredFormat": {
                                "backgroundColor": color
                            },
                            "userEnteredValue": {
                                "numberValue": round(density)
                            }
                        }]
                    }],
                    "fields": "userEnteredFormat.backgroundColor,userEnteredValue.numberValue"
                }
            })
    
    body = {
        "requests": requests
    }
    return body, sim

def updateSheetFromBody(service, SPREADSHEET_ID, body):
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body
    )
    response = request.execute()
    return response