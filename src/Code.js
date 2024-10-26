//This is a deprecated file. When I first implemented this project (and made this extremely low quality code),
//I was using JavaScript integrated with Google Apps Script. I have since used python for my algorithm this code is
//no longer used, deprecated, and very bad at simulating anyways. I am keeping it here for reference.

/*const X_GRID_SIZE = 40;
const Y_GRID_SIZE = 40;

function main() {
    Logger.log("Program begin.");
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
    initializeGrid(sheet);
    for (var step = 0; step < 10; step++) {
        //Utilities.sleep();
        Logger.log("Step " + step);
        updateGrid(sheet);
    }
}

function initializeGrid(sheet) {
    for (var i = 0; i < X_GRID_SIZE; i++) {
        for (var j = 0; j < Y_GRID_SIZE; j++) {
            var height = Math.random();
            sheet.getRange(i + 1, j + 1).setValue(Math.round(height*100)/100);
            sheet.getRange(i + 1, j + 1).setBackground(getColorFromHeight(height));
            sheet.getRange(i + 1, j + 1).setFontSize(7);
        }
    }
}

function updateGrid(sheet) {
    var heights = [];
    for (var i = 0; i < 40; i++) {
        heights[i] = [];
        for (var j = 0; j < 40; j++) {
            heights[i][j] = sheet.getRange(i + 1, j + 1).getValue();
        }
    }

    var newHeights = [];
    for (var i = 0; i < 40; i++) {
        newHeights[i] = [];
        for (var j = 0; j < 40; j++) {
            var sum = 0;
            var count = 0;
            for (var di = -1; di <= 1; di++) {
                for (var dj = -1; dj <= 1; dj++) {
                    if (di === 0 && dj === 0) continue;
                    var ni = i + di;
                    var nj = j + dj;
                    if (ni >= 0 && ni < 40 && nj >= 0 && nj < 40) {
                        sum += heights[ni][nj];
                        count++;
                    }
                }
            }
            newHeights[i][j] = sum / count;
        }
    }
    Logger.log(newHeights[15][15]);
    for (var i = 0; i < 40; i++) {
        for (var j = 0; j < 40; j++) { 
            sheet.getRange(i + 1, j + 1).setValue(newHeights[i][j]);
            sheet.getRange(i + 1, j + 1).setBackground(getColorFromHeight(newHeights[i][j]));
        }
    }
}

function getColorFromHeight(height) {
    var red = Math.floor(255 * height);
    var blue = 255-red;
    return rgbToHex(red, 0, blue);
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length === 1 ? "0" + hex : hex;
}

function getRandomColorString() {
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += Math.floor(Math.random() * 16).toString(16);
    }
    return color;
}

function addToSideBar() {
    const htmlServ = HtmlService.createHtmlOutputFromFile('sidebar')
        .setTitle('Fluid Info')
        .setWidth(300);
    const html = htmlServ.evaluate();
    const ui = SpreadsheetApp.getUi();
    ui.showSidebar(html);
}*/

/*Similar Luau Implementation
local HadDensity = math.max(0, Density - 2) * 0.75
                
                if HadDensity > 0 then
                    local Total = 0
                    
                    local GridLeft = Grid[x - 1]
                    local GridRight = Grid[x + 1]
                    local GridDown = Grid[x][y - 1]
                    local GridUp = Grid[x][y + 1]
                    
                    if GridLeft and GridLeft[y] and (Density + HadDensity / 4) > GridLeft[y][1] then
                        local Land = LandGrid[x - 1] and LandGrid[x - 1][y]
                        
                        if (not Land) or IsLand or (Density + HadDensity / 4) > ((LandGrid[x - 1][y] + 1) * 2) then
                            Grid[x - 1][y][1] = GridLeft[y][1] + HadDensity / 4
                            Grid[x - 1][y][3] = true
                            
                            Total = Total + 0.25
                        end
                    end
                    
                    if GridRight and GridRight[y] and (Density + HadDensity / 4) > GridRight[y][1] then
                        local Land = LandGrid[x + 1] and LandGrid[x + 1][y]
                        
                        if (not Land) or IsLand or (Density + HadDensity / 4) > ((LandGrid[x + 1][y] + 1) * 2) then
                            Grid[x + 1][y][1] = GridRight[y][1] + HadDensity / 4
                            Grid[x + 1][y][3] = true
                            
                            Total = Total + 0.25
                        end
                    end
                    
                    if GridDown and (Density + HadDensity / 4) > GridDown[1] then
                        local Land = LandGrid[x] and LandGrid[x][y - 1]
                        
                        if (not Land) or IsLand or (Density + HadDensity / 4) > ((LandGrid[x][y - 1] + 1) * 2) then
                            Grid[x][y - 1][1] = GridDown[1] + HadDensity / 4
                            Grid[x][y - 1][3] = true
                            
                            Total = Total + 0.25
                        end
                    end
                    
                    if GridUp and (Density + HadDensity / 4) > GridUp[1] then
                        local Land = LandGrid[x] and LandGrid[x][y + 1]
                        
                        if (not Land) or IsLand or (Density + HadDensity / 4) > ((LandGrid[x][y + 1] + 1) * 2) then
                            Grid[x][y + 1][1] = GridUp[1] + HadDensity / 4
                            Grid[x][y + 1][3] = true
                            
                            Total = Total + 0.25
                        end
                    end
                    
                    Density = Density - HadDensity * Total
                    
                    if Density <= 0 then
                        Grid[x][y] = { 0, Current[2], HadDensity > 0 or Current[3] }
                    else
                        Grid[x][y] = { Density, Current[2], Current[3] }
                    end
                end
*/