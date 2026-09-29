# CS5374 Assignment 3

This folder contains source files and notes for all four objectives in `Assignment3-CS5374-Spring2026.pdf`.

## Folder layout

- `objective1_jpf/` - Java Pathfinder examples for deadlock and race detection
- `objective2_pysym/` - PySym sample program and driver
- `objective3_spin/` - SPIN models for exercise 3 (mutual exclusion)
- `objective4_llm/` - LLM-based model checking analysis with CTL formulas

## Running from Anaconda Prompt

Open Anaconda Prompt and change into this folder:

```bat
cd /d "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\Assingment 3"
```

Then load the prepared toolchain:

```bat
call assignment_env.bat
```

### Objective 1: JPF

JPF has already been cloned and built locally in `objective1_jpf\jpf-core` using Java 11.

Compile the sample Java files and run JPF:

```bat
cd objective1_jpf
javac MyDeadlock.java MyRacer.java
jpf-core\bin\jpf.bat +classpath=. MyDeadlock.jpf
jpf-core\bin\jpf.bat +classpath=. MyRacer.jpf
```

Tested result:

- `MyDeadlock.jpf` reports a deadlock
- `MyRacer.jpf` reports a race for field `MyRacer$Pair.x`

### Objective 2: PySym

The working conda environment is already created as `svv-a3-py36`. This uses Python 3.6 because the upstream PySym package is not compatible with newer Python versions on Windows without patching.

Run:

```bat
cd objective2_pysym
conda activate svv-a3-py36
python run_pysym_example.py
```

Tested result:

- `<PathGroup with 45 deadended, 1 completed>`
- `Computed z = 26`

### Objective 3: SPIN

SPIN and GCC are already installed and configured by `assignment_env.bat`.

Run:

```bat
cd objective3_spin
spin -run ex_3a.pml
spin -p -replay ex_3a.pml

spin -run ex_3b.pml
spin -p -replay ex_3b.pml

spin -run ex_3c.pml
spin -p -replay ex_3c.pml
```

Tested result:

- `ex_3b.pml` completes with `errors: 0`
- `ex_3c.pml` reports `assertion violated (cnt==1)`

### Objective 4: LLM analysis

Read:

```bat
notepad objective4_llm\analysis.md
```

Files:

- `objective4_llm\analysis.md`
- `objective4_llm\mutex_program_fixed.c`

## Notes

- Installed and verified locally:
  - Miniconda at `C:\Users\hamza\miniconda3`
  - Java 11 and Java 17
  - SPIN 6.5.1
  - MSYS2 GCC
  - Git
- For the assignment submission, you should still capture your own screenshots after running each objective in your own Anaconda Prompt session.
