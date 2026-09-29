def test(x, y):
    out = 2
    while x < y:
        out *= x
        x += 1

    return out


x = 0
z = 0
while x < 5:
    y = 0
    while y < 3:
        z += test(x, y)
        y += 1
    x += 1
