Optimizations
=============

This is a record of the optimizations applied:

- removed string operations by guarding the debug print statements behind an `if self.debug: ...`; I attempted to wrap this logic inside a `self.log(format, *args)` but RPython expects format operations with `%` to have a constant string on the left side.
- attempted to use `@unroll_safe` and found that with `@unroll_safe` on `transform_rule`, `transform_native`:

  ```
  PYPYLOG=jit:e2.log time bin/e2 src/main/sumprimes.e2
  76127
  1.64user 0.02system 0:01.84elapsed 90%CPU (0avgtext+0avgdata 44240maxresident)k
  0inputs+1448outputs (0major+17708minor)pagefaults 0swaps
  without unroll_safe
  ```
  
  and without:
  
  ```
  PYPYLOG=jit:e2.log time bin/e2 src/main/sumprimes.e2
  76127
  1.88user 0.01system 0:02.07elapsed 91%CPU (0avgtext+0avgdata 43332maxresident)k
  0inputs+360outputs (0major+17536minor)pagefaults 0swaps
  ``` 
