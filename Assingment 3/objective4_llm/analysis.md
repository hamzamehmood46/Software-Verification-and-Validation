# Objective 4

## Program

The given mutex program has:

- two increment threads
- one watch thread
- shared variable `count`
- mutex `count_mutex`
- condition variable `count_max`

I corrected the syntax problems in the original gist and saved the clean version in `mutex_program_fixed.c`.

## CTL expression

Let `Race` mean that two threads access `count` at the same time and at least one access is a write.

The race-condition query is:

`EF(Race)`

The race-free safety property is:

`AG(!Race)`

One expanded form is:

`AG(!((Inc0Write && Inc1Write) || (Inc0Write && WatchRead) || (Inc1Write && WatchRead)))`

## LLM-style analysis

The corrected program does not have a race on `count`.

Reason:

1. Both increment threads update `count` only after `pthread_mutex_lock(&count_mutex)`.
2. The watch thread reads `count` only while holding the same mutex.
3. `pthread_cond_wait(&count_max, &count_mutex)` releases the mutex while waiting and locks it again before continuing.
4. Because all accesses to `count` use the same mutex, conflicting accesses cannot happen at the same time.

## Result

`EF(Race)` is false.

`AG(!Race)` is true.

So the intended mutex program is race-free for shared variable `count`.
