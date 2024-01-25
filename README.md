# PyOpcodeObfuscation
Scripts for obfuscating Python opcodes &amp; for modifying interpreter code based on custom opcodes


I've commented out the os.system call (better ways of executing system commands, but will leave that up to you to decide) so it won't compile, to hopefully handle multiple platforms. 

Executing the scrambler is simple, simply pass the folder containing the core Python 3.11 files (should literally be Python 3.11.4 on extraction from the archive) as the first argument. This has only been tested and designed for 3.11.4, so you may have some issues when running on other versions of Python.

For the fixer.py file, the first argument is a clean Python 3.11 codebase, while the second argument is a file containing the output of the opcode.opmap command from a modified interpreter.
