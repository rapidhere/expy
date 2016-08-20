EXPY - A Expression Executor for Python
===

>
> Yet another toy, but for learning bytecode this time
>

[![Build Status](https://travis-ci.org/rapidhere/expy.svg?branch=master)](https://travis-ci.org/rapidhere/expy)

Usage
---

```
$ python expy.py "a + b * 3.0" --variables="a=2,b=3" --print-dis
byte code disassamble Info:
  1           0 LOAD_GLOBAL              1 (a)
              3 STORE_FAST               0 (a)
              6 LOAD_GLOBAL              2 (b)
              9 STORE_FAST               1 (b)
             12 LOAD_FAST                0 (a)
             15 LOAD_FAST                1 (b)
             18 LOAD_CONST               1 (3.0)
             21 BINARY_MULTIPLY
             22 BINARY_ADD
             23 STORE_GLOBAL             0 (__ret__)
             26 LOAD_CONST               0 (None)
             29 RETURN_VALUE

variables:
  a = 2
  b = 3

execute `a + b * 3.0`

  > 11.0

```

A simple benchmark
---
```
>>> benchmark on: long multiply
expy: 0.00170ms
eval: 0.03360ms
py_expression_eval: 0.02980ms
simpeeval: 0.10370ms
asteval: 0.14570ms

>>> benchmark on: large power
expy: 60.05000ms
eval: 60.25000ms
py_expression_eval: N/A
simpeeval: 60.05000ms
asteval: N/A
```

Run test
---

```
pip install -r requirements.txt
python test/run.py
```

LICENSE
---
LGPL-v3.0