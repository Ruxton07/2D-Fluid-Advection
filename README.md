# 2D Fluid Simulation
This project simulates fluid dynamics on a 2D grid using Python. The simulation is visualized using Google Sheets, where each cell represents a grid cell with a certain fluid density. The project includes various prototypes and utility classes to facilitate the simulation and visualization.

## Project Structure

```
.
├── .gitignore
├── README.md
├── src/
│   ├── main.py
│   ├── Prototypes/
│   │   ├── Prototype1.js
│   │   ├── Prototype2.py
│   │   ├── Prototype3.py
│   │   ├── Prototype4.py
│   ├── simulation.py
│   ├── utilityclasses/
│   │   ├── GridMakerSubprocess.py
│   │   ├── GridObject.py
│   │   ├── SimArray.py
```


## Installation

1. Clone the repository:
```sh
   git clone https://github.com/Ruxton07/2DFluidSimulation.git
   cd 2DFluidSimulation
```
2. Install the required dependencies:
```sh
    pip install -r requirements.txt
```

3. Set up Google API credentials:
- Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
- Enable the Google Sheets API and Google Drive API.
- Create OAuth 2.0 credentials and download the `credentials.json` file.
- Place the `credentials.json` file in the root directory of the project.

## Usage

1. Run the main simulation script:

```sh
    python src/main.py
```

2. The simulation will update the specified Google Sheets document with the fluid dynamics visualization.

Currently, you need to edit the `SPREADSHEET_ID` and `GRID_RANGE` in main.py to make this work, since you do not own the spreadsheet I used to develop this project.

## Grid Maker Subprocess

The `GridMakerSubprocess` class in `src/utilityclasses/GridMakerSubprocess.py` allows you to create a custom grid by toggling squares on and off. The generated grid can be used as an initial state for the simulation. Sorry Linux users, this one only works on Windows. :\(

### Example Usage

```py
    from src.utilityclasses.GridMakerSubprocess import GridMakerSubprocess

    # Create a 40x40 grid
    GridMakerSubprocess(40, 40)
```

## Prototypes

The `src/Prototypes` directory contains various prototypes of the simulation. These prototypes demonstrate different approaches and algorithms for simulating fluid dynamics.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub or [contact me](#contact) if you have something else.

## Contact

For any questions or inquiries, please contact me at [rt.kellar@gmail.com] or direct message me through my discord, ruxton07.