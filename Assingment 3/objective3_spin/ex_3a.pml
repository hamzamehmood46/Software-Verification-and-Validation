bool b[2]
byte k = 0
byte cnt = 0

active [2] proctype user() {
    byte i = _pid;
    byte j = 1 - i;

C0:
    b[i] = false;

C1:
    if
    :: k != i ->
C2:
        if
        :: !b[j] -> goto C2
        :: else ->
            k = i;
            goto C1
        fi
    :: else ->
        cnt++;
crit:
        assert(cnt == 1);
        cnt--;
        b[i] = true;
        goto C0
    fi
}
