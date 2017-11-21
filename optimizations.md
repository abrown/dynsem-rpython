Optimizations
=============

This is a record of the optimizations applied:

- removed string operations by guarding the debug print statements behind an `if self.debug: ...`; I attempted to wrap this logic inside a `self.log(format, *args)` but RPython expects format operations with `%` to have a constant string on the left side.
- 
