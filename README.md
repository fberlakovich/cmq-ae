This repository contains the CPython fork for the paper [Cross Module Quickening - The Curious Case of C Extensions](https://ucsrl.de/publications/cmq-ecoop24-preprint.pdf).
The code is a fork of [CPython](https://github.com/python/cpython) version `3.12.0` and adds the optimization interface described in the paper.
The optimization interface is entirely optional.
If no extension registers optimizations, everything should work as usual.

You can find the most important changes in [specialize.c](Python/specialize.c) (functions prefixed with `_PyExternal`) and in [ceval.c](Python/ceval.c) (opcode defintions ending with `_EXTERNAL`).
For details on how to build CPython, please refer to the [official documentation](https://devguide.python.org/setup/) as well as the [Dockerfile](https://github.com/fberlakovich/cmq-npbench-ae/blob/master/Dockerfile) in the `NPBench` repository.
The Dockerfile contains the specific build steps for this fork.
