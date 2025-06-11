# Magnifico Experiments

## Steps

The `NOTRANSFORM` flag should be set for the Unifico version, otherwise unset.

```bash
# Depending on the machine you are on
make reduce-noise-{x86,arm}

# Go to the experiment directory
cd <npb>.{unifico,popcorn}.<flag>.<class>

# Single migration and back
make trip-x86-init NOTRANSFORM=
make trip-arm NOTRANSFORM=
make trip-x86-finalize NOTRANSFORM=

# 10 migrations (5 round trips)
make trip-x86-init NOTRANSFORM=
for i in $(seq 5); do
echo $i
make trip-arm NOTRANSFORM=
make trip-x86-continue NOTRANSFORM=
done
# Depending on the number of migration points, a final run might be needed
# This is because the application can allow just enough migrations, so that the
# above loop migrations will be just enough to finish the benchmark.
make trip-x86-finalize NOTRANSFORM=

# Measure recode
make perf-recode-{x86,arm} WARMUP=3 RUNS=3 NOTRANSFORM=
```
