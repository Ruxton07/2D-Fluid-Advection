class Field2D:
    def __init__(self, res: int):
        self.field = []
        for b in range(res):
            fm = []
            for a in range(res):
                fm.append([0, 0, 0, 0, 1, 0, 0, 0, 0])
            self.field.append(fm[:])
        self.res = res

    @staticmethod
    def VisualizeField(a, sc, res, velocityField):
        stringr = ""
        for u in range(res):
            row = ""
            for v in range(res):
                n = int(u * a.res / res)
                x = int(v * a.res / res)
                flowmomentem = a.Momentum(n, x, velocityField)
                col = "\033[38;2;{0};{1};{2}m██".format(
                    int(127 + sc * flowmomentem[0]), int(127 + sc * flowmomentem[1]), 0
                )
                row = row + col
            print(row)
            stringr = stringr + row + "\n"
        return stringr

    def Momentum(self, x, y, velocityField):
        return velocityField[y][x][0] * sum(self.field[y][x]), velocityField[y][x][1] * sum(self.field[y][x])