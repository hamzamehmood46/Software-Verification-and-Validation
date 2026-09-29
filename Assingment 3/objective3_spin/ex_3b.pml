bool flag[2]
bool turn
byte cnt = 0

active [2] proctype user() {
    flag[_pid] = true;
    turn = _pid;
    (flag[1 - _pid] == false || turn == 1 - _pid);

    cnt++;
crit:
    assert(cnt == 1);
    cnt--;

    flag[_pid] = false
}
