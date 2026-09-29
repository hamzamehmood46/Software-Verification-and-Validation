from z3 import *

def solve(label, constraint):
    s = Solver()
    s.add(constraint)
    print(f"\n=== {label} ===")
    if s.check() == sat:
        m = s.model()
        print("a =", m[a])
        print("b =", m[b])
    else:
        print("UNSAT")

a = Int('a')
b = Int('b')

c = a * b

pathP1 = And(c == 20, a > 0)
pathP2 = And(c == 20, a <= 0)
pathP3 = (c != 20)

solve("Path P1 (return 'P1')", pathP1)
solve("Path P2 (return 'P2')", pathP2)
solve("Path P3 (return 'P3')", pathP3)