# Magnifico Experiments

## Compiler and Migration Library used

The migration library used can be found [here](https://github.com/systems-nuts/popcorn-compiler/tree/magnifico).
This needs to be installed, for example in `usr/local/popcorn`, as per the popcorn-kernel [wiki](https://github.com/ssrg-vt/popcorn-kernel/wiki/Compiler-Setup).

The compiler is either the Popcorn compiler or the Unifico compiler, depending on the experiment (decided from inside the repos in the following instructions).

## Compile the benchmarks

### Popcorn

The popcorn benchmarks are hosted [here](https://github.com/systems-nuts/popcorn-benchmark/tree/nikos/taco-migration-experiment).
After cloning, see the `popcorn-benchmark/heterogeneous_test_suits/NPB3.3-SER-C-FLAT-popcorn-explicit/README.md` for instructions on how to compile the benchmarks.

### Unifico

The unifico benchmarks are hosted [here](https://github.com/systems-nuts/magnifico/tree/nikos/taco-migration-experiment).
After cloning, see `magnifico/benchmarks/npb-unifico/README.md` for build instructions.


## Steps

The `NOTRANSFORM` flag should be set for the Unifico version, otherwise unset.

```bash
# Go to the experiment directory
cd <npb>.{unifico,popcorn}.<flag>.<class>

# Depending on the machine you are on
make reduce-noise-{x86,arm}

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
