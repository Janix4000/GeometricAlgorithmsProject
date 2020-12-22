class TriangleSet:
    def __init__(self):
        self.ts = {}

    def add_triangle(self, i0, i1, i2):
        t = (i0, i1, i2)
        for i in range(3):
            self.ts[(t[i], t[(i + 1) % 3])] = t[(i + 2) % 3]

    def remove_triangle(self, i0, i1, i2):
        t = (i0, i1, i2)
        for i in range(3):
            self.ts.pop((t[i], t[(i + 1) % 3]))

    def __contains__(self, item):
        return item in self.ts
