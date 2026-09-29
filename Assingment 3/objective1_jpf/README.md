# Objective 1: Java Pathfinder

This folder contains the two Java programs referenced in the assignment:

- `MyDeadlock.java` with `MyDeadlock.jpf`
- `MyRacer.java` with `MyRacer.jpf`

## Expected outcomes

- `MyDeadlock.jpf` should report a deadlock because the two threads lock `x` and `y` in opposite order.
- `MyRacer.jpf` should report a race condition because two threads update shared state without synchronization.

## Run commands

From Anaconda Prompt:

```bat
cd /d "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\Assingment 3\objective1_jpf"
jpf-core\bin\jpf.bat MyDeadlock.jpf
jpf-core\bin\jpf.bat MyRacer.jpf
```
