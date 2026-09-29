# Objective 2: PySym

This folder reproduces the sample program from the PySym README and a small driver that symbolically executes it.

## Files

- `test.py` - the sample program from the PySym repository README
- `run_pysym_example.py` - creates a PySym project, explores all paths, and prints the final value of `z`

## Expected outcome

The PySym README shows:

- 45 deadended paths
- 1 completed path
- final `z = 26`

## Run commands

```bat
conda create -n svv-a3 python=3.8 -y
conda activate svv-a3
pip install git+https://github.com/bannsec/pySym.git
cd /d "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\Assingment 3\objective2_pysym"
python run_pysym_example.py
```
