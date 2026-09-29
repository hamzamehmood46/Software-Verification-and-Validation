from z3 import *

def solve(label, constraint):
    s = Solver()
    s.add(constraint)
    print(f"\n=== {label} ===")
    if s.check() == sat:
        m = s.model()
        print("x =", m[x])
        print("y =", m[y])
    else:
        print("UNSAT")

x = Int('x')
y = Int('y')

z = x + y

pathA = And(z > 10, x > y)
pathB = And(z > 10, x <= y)
pathC = (z <= 10)

solve("Path A (return 1)", pathA)
solve("Path B (return 2)", pathB)
solve("Path C (return 3)", pathC)