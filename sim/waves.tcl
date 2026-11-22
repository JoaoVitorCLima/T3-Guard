database -open waves -shm -into $::env(T3_GUARD_SHM) -default
probe -create -database waves tb -all -depth 1
run
exit
