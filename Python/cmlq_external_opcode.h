#if defined(Py_OPT_CMLQ_ENV) || defined(Py_OPT_CMLQ_ALWAYS)
int result = external_handlers[oparg](external_cache_pointer, &stack_pointer);
if (result == 2) {
    unsigned long offset = next_instr - 1 - _PyCode_CODE(frame->f_code);
    next_instr = _PyExternal_Deoptimize(next_instr - 1, frame);
    oparg = next_instr->op.arg;
    DISPATCH_SAME_OPARG();
}
#else
_PyErr_Format(tstate, PyExc_SystemError,
              "%U:%d: Opcode should not be reachable, CMLQ is disabled",
              frame->f_code->co_filename,
              PyUnstable_InterpreterFrame_GetLine(frame));
goto error;
#endif