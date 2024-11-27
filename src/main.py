import os.path
import tkinter as tk

from tkinter import ttk
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import src.simulation as sim

prototypes = {
    "p2": "src.Prototypes.Prototype2",
    "p3": "src.Prototypes.Prototype3",
    "p4": "src.Prototypes.Prototype4",
    "p5": "src.Prototypes.Prototype5",
    "p6": "src.Prototypes.Prototype6",
    "p7": "src.Prototypes.Prototype7",
}

availableSimulations = ["c", "p4", "p5", "p6", "p7"]

for key, module in prototypes.items():
    globals()[key] = __import__(module, fromlist=["main"])


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1NapEbwM5uHI1JoR1sZo8Qzd5WGt84tHy3jl_P5IljRM"
GRID_RANGE = "Grid!A1:AN40"
print(f"Using range: {GRID_RANGE}")


def main():
    def show_settings_window():
        def submit_settings():
            nonlocal testGridID, dataDisplayType, colorInterpolation, verboseFlag, SIMULATION_CHOICE
            testGridID = int(testGridID_var.get())
            dataDisplayType = dataDisplayType_var.get()
            colorInterpolation = colorInterpolation_var.get()
            verboseFlag = verboseFlag_var.get() == "True"
            SIMULATION_CHOICE = simulationChoice_var.get()
            settings_window.destroy()

        settings_window = tk.Tk()
        settings_window.title("Simulation Settings")

        tk.Label(settings_window, text="Test Grid ID:").grid(
            row=0, column=0, padx=10, pady=5
        )
        testGridID_var = tk.StringVar(value="7")
        tk.Entry(settings_window, textvariable=testGridID_var).grid(
            row=0, column=1, padx=10, pady=5
        )

        tk.Label(settings_window, text="Data Display Type:").grid(
            row=1, column=0, padx=10, pady=5
        )
        dataDisplayType_var = tk.StringVar(value="v")
        ttk.Combobox(
            settings_window,
            textvariable=dataDisplayType_var,
            values=["d", "vx", "vy", "v"],
        ).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(settings_window, text="Color Interpolation:").grid(
            row=2, column=0, padx=10, pady=5
        )
        colorInterpolation_var = tk.StringVar(value="l")
        ttk.Combobox(
            settings_window, textvariable=colorInterpolation_var, values=["l", "q"]
        ).grid(row=2, column=1, padx=10, pady=5)

        tk.Label(settings_window, text="Verbose:").grid(
            row=3, column=0, padx=10, pady=5
        )
        verboseFlag_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            settings_window, text="Verbose", variable=verboseFlag_var
        ).grid(row=3, column=1, padx=10, pady=5)

        tk.Label(settings_window, text="Simulation Choice:").grid(
            row=4, column=0, padx=10, pady=5
        )
        simulationChoice_var = tk.StringVar(value="p6")
        ttk.Combobox(
            settings_window,
            textvariable=simulationChoice_var,
            values=availableSimulations,
        ).grid(row=4, column=1, padx=10, pady=5)

        tk.Button(settings_window, text="Submit", command=submit_settings).grid(
            row=5, columnspan=2, pady=10
        )

        settings_window.mainloop()


    # initialize settings variables
    testGridID = 7
    dataDisplayType = "v"
    colorInterpolation = "l"
    verboseFlag = True
    SIMULATION_CHOICE = "p6"

    # show settings window
    show_settings_window()

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # TEST_GRID_ID: int = 7,
    # DATA_DISPLAY_TYPE: str = "v",
    # COLOR_INTERPOLATION: str = "l",
    # VERBOSE_VAL: bool = True

    try:
        match SIMULATION_CHOICE:
            case "c":
                sim.main(
                    creds,
                    SPREADSHEET_ID,
                    GRID_RANGE,
                    TEST_GRID_ID=testGridID,
                    DATA_DISPLAY_TYPE=dataDisplayType,
                    COLOR_INTERPOLATION=colorInterpolation,
                    VERBOSE_VAL=verboseFlag,
                )
            case "p4":
                p4.main(
                    creds,
                    SPREADSHEET_ID,
                    GRID_RANGE,
                    TEST_GRID_ID=testGridID,
                    DATA_DISPLAY_TYPE=dataDisplayType,
                    COLOR_INTERPOLATION=colorInterpolation,
                    VERBOSE_VAL=verboseFlag,
                )
            case "p5":
                p5.main(
                    creds,
                    SPREADSHEET_ID,
                    GRID_RANGE,
                    TEST_GRID_ID=testGridID,
                    DATA_DISPLAY_TYPE=dataDisplayType,
                    COLOR_INTERPOLATION=colorInterpolation,
                    VERBOSE_VAL=verboseFlag,
                )
            case "p6":
                p6.main(
                    creds,
                    SPREADSHEET_ID,
                    GRID_RANGE,
                    TEST_GRID_ID=testGridID,
                    DATA_DISPLAY_TYPE=dataDisplayType,
                    COLOR_INTERPOLATION=colorInterpolation,
                    VERBOSE_VAL=verboseFlag,
                )
            case "p7":
                p7.main(
                    creds,
                    SPREADSHEET_ID,
                    GRID_RANGE,
                    TEST_GRID_ID=testGridID,
                    DATA_DISPLAY_TYPE=dataDisplayType,
                    COLOR_INTERPOLATION=colorInterpolation,
                    VERBOSE_VAL=verboseFlag,
                )
            case _:
                sim.main(
                    creds,
                    SPREADSHEET_ID,
                    GRID_RANGE,
                    TEST_GRID_ID=testGridID,
                    DATA_DISPLAY_TYPE=dataDisplayType,
                    COLOR_INTERPOLATION=colorInterpolation,
                    VERBOSE_VAL=verboseFlag,
                )
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
