# Objective 3: SPIN

This folder includes Promela models for Exercise 3, "Verifying a Mutual Exclusion Algorithm."

## Files

- `ex_3a.pml` - 1966 algorithm modeled from the pseudo-code in the exercise
- `ex_3b.pml` - Peterson's algorithm
- `ex_3c.pml` - faulty mutual exclusion algorithm from the exercise

## Expected outcomes

- `ex_3a.pml` should be disproved by SPIN because the algorithm is flawed.
- `ex_3b.pml` should satisfy `assert(cnt == 1)` and preserve mutual exclusion.
- `ex_3c.pml` should fail the assertion and SPIN should produce a counterexample.

## Run commands

```bat
cd /d "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\Assingment 3\objective3_spin"
spin -run ex_3a.pml
spin -p -replay ex_3a.pml

spin -run ex_3b.pml
spin -p -replay ex_3b.pml

spin -run ex_3c.pml
spin -p -replay ex_3c.pml
```

To try a shorter counterexample for `ex_3c.pml`, you can also use:

```bat
spin -run -i ex_3c.pml
spin -p -replay ex_3c.pml
```
