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

- add `_immutable_fields_` to terms (unfortunately have to specify all the terms of the class hierarchy in each class)
- use arrays in `Context` and some upfront analysis for determining slots to use. Maybe a ~30% time reduction:

  ```
  PYPYLOG=jit:e2-1511412269.log time bin/e2 src/main/sumprimes.e2
  76127
  4.38user 0.11system 0:04.49elapsed 99%CPU (0avgtext+0avgdata 123444maxresident)k
  0inputs+1424outputs (0major+45923minor)pagefaults 0swaps
  ```

  ```
  PYPYLOG=jit:e2-1511844456.log time bin/e2 src/main/sumprimes.e2
  76127
  3.40user 0.06system 0:03.46elapsed 99%CPU (0avgtext+0avgdata 120224maxresident)k
  0inputs+1448outputs (0major+26645minor)pagefaults 0swaps
  ```
 
- add `@unroll_safe` to `Context` methods
