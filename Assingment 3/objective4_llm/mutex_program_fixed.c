#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX 10
#define MAX_COUNT 15

int count = 0;
pthread_mutex_t count_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t count_max = PTHREAD_COND_INITIALIZER;

void *increment(void *arg) {
    int id = *(int *)arg;
    int i;

    for (i = 0; i < MAX; i++) {
        pthread_mutex_lock(&count_mutex);
        count++;
        printf("thread %d incremented count to %d\n", id, count);
        if (count >= MAX_COUNT) {
            pthread_cond_signal(&count_max);
        }
        pthread_mutex_unlock(&count_mutex);
    }

    return NULL;
}

void *watch(void *arg) {
    int id = *(int *)arg;

    pthread_mutex_lock(&count_mutex);
    while (count < MAX_COUNT) {
        pthread_cond_wait(&count_max, &count_mutex);
    }
    printf("watch thread %d saw count = %d\n", id, count);
    pthread_mutex_unlock(&count_mutex);

    return NULL;
}

int main() {
    pthread_t threads[3];
    int thread_id[3] = {0, 1, 2};

    pthread_create(&threads[0], NULL, increment, &thread_id[0]);
    pthread_create(&threads[1], NULL, increment, &thread_id[1]);
    pthread_create(&threads[2], NULL, watch, &thread_id[2]);

    pthread_join(threads[0], NULL);
    pthread_join(threads[1], NULL);
    pthread_join(threads[2], NULL);

    return 0;
}
