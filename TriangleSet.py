class TriangleSet:
    def __init__(self):
        self.ts = {}

    def add_triangle(self, i0, i1, i2):
        t = (i0, i1, i2)
        for i in range(3):
            self.ts[(t[i], t[(i + 1) % 3])] = t[(i + 2) % 3]
        if len(self.ts) % 3 != 0:
            raise Exception("Hola, there should be 3k entries!")

    def remove_triangle(self, i0, i1, i2):
        t = (i0, i1, i2)
        for i in range(3):
            self.ts.pop((t[i], t[(i + 1) % 3]))

    def __contains__(self, item):
        return item in self.ts

    def get_first(self):
        i0, i1 = next(iter(self.ts))
        i2 = self.ts[(i0, i1)]
        return i0, i1, i2

    def __getitem__(self, item):
        return self.ts[item]

    def get_triangles(self):
        triangles = set()
        for (i0, i1), i2 in self.ts.items():
            tr = [i0, i1, i2]
            triangles.add(tuple(sorted(tr)))
        return list(triangles)


if __name__ == '__main__':
    kek = {(0, 0): 1, (1, 1): 1, (2, 1): 3}
    print(next(iter(kek)))
