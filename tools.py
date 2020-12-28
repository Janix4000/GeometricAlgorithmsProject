def own_det_3(a, b, c):
    return (a[0] * b[1]) + (a[1] * c[0]) + (b[0] * c[1]) - (c[0] * b[1]) - (b[0] * a[1]) - (a[0] * c[1])


def det(a, b, c):
    a, b, c = a.as_tuple(), b.as_tuple(), c.as_tuple()
    return own_det_3(a, b, c)


def dist_sq(a, b):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2


def less_angle(p1, p2, a, det=det, delta=1e-13):
    if p1 is a:
        return True
    if p2 is a:
        return False
    det = det(a, p1, p2)
    if abs(det) < delta:
        return dist_sq(a, p1) >= dist_sq(a, p2)
    return det >= delta
