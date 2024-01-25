import random, re, os, sys, subprocess


non_arg_mnemonics = [b"CACHE", b"POP_TOP", b"PUSH_NULL", b"NOP", b"UNARY_POSITIVE", b"UNARY_NEGATIVE", 
                     b"UNARY_NOT", b"UNARY_INVERT", b"BINARY_SUBSCR", b"GET_LEN", b"MATCH_MAPPING", 
                     b"MATCH_SEQUENCE", b"MATCH_KEYS", b"PUSH_EXC_INFO", b"CHECK_EXC_MATCH", 
                     b"CHECK_EG_MATCH", b"WITH_EXCEPT_START", b"GET_AITER", b"GET_ANEXT", 
                     b"BEFORE_ASYNC_WITH", b"BEFORE_WITH", b"END_ASYNC_FOR", b"STORE_SUBSCR", 
                     b"DELETE_SUBSCR", b"GET_ITER", b"GET_YIELD_FROM_ITER", b"PRINT_EXPR", 
                     b"LOAD_BUILD_CLASS", b"LOAD_ASSERTION_ERROR", b"RETURN_GENERATOR", b"LIST_TO_TUPLE", 
                     b"RETURN_VALUE", b"IMPORT_STAR", b"SETUP_ANNOTATIONS", b"YIELD_VALUE", b"ASYNC_GEN_WRAP", 
                     b"PREP_RERAISE_STAR", b"POP_EXCEPT"]

arg_mnemonics = [b"STORE_NAME", b"DELETE_NAME", b"UNPACK_SEQUENCE", b"STORE_ATTR", b"DELETE_ATTR", 
                 b"STORE_GLOBAL", b"DELETE_GLOBAL", b"SWAP", b"LOAD_NAME", b"BUILD_TUPLE", b"BUILD_LIST", 
                 b"BUILD_SET", b"BUILD_MAP", b"LOAD_ATTR", b"IMPORT_NAME", b"IMPORT_FROM", b"LOAD_GLOBAL", 
                 b"IS_OP", b"CONTAINS_OP", b"RERAISE", b"COPY", b"MAKE_FUNCTION", b"CALL_FUNCTION_EX", 
                 b"BUILD_STRING", b"CALL", b"LOAD_CONST"] 

# we won't be scrambling these as a lot require additional modifications to be made; and so cause errors
additional_mnemonics = [b"RAISE_VARARGS", b"POP_JUMP_FORWARD_IF_NOT_NONE", b"POP_JUMP_FORWARD_IF_NONE", 
                        b"JUMP_FORWARD", b"JUMP_IF_FALSE_OR_POP", b"JUMP_IF_TRUE_OR_POP", 
                        b"POP_JUMP_FORWARD_IF_FALSE", b"POP_JUMP_FORWARD_IF_TRUE", b"GET_AWAITABLE", 
                        b"UNPACK_EX", b"FOR_ITER", b"BUILD_SLICE", b"BINARY_OP", b"SEND", 
                        b"JUMP_BACKWARD_NO_INTERRUPT", b"JUMP_BACKWARD", b"EXTENDED_ARG", b"LIST_APPEND", 
                        b"SET_ADD", b"MAP_ADD", b"COPY_FREE_VARS", b"RESUME", b"MATCH_CLASS", b"FORMAT_VALUE", 
                        b"BUILD_CONST_KEY_MAP", b"LOAD_METHOD", b"LIST_EXTEND", b"SET_UPDATE", b"DICT_MERGE", 
                        b"DICT_UPDATE", b"PRECALL", b"POP_JUMP_BACKWARD_IF_NOT_NONE", 
                        b"POP_JUMP_BACKWARD_IF_NONE", b"POP_JUMP_BACKWARD_IF_FALSE", 
                        b"POP_JUMP_BACKWARD_IF_TRUE", b"COMPARE_OP", b"LOAD_FAST", b"STORE_FAST",
                        b"DELETE_FAST", b"MAKE_CELL", b"LOAD_CLOSURE", b"LOAD_DEREF", b"STORE_DEREF", 
                        b"DELETE_DEREF", b"LOAD_CLASSDEREF", b"KW_NAMES", b"BINARY_OP_ADAPTIVE", 
                        b"BINARY_OP_ADD_FLOAT", b"BINARY_OP_ADD_INT", b"BINARY_OP_ADD_UNICODE", 
                        b"BINARY_OP_INPLACE_ADD_UNICODE", b"BINARY_OP_MULTIPLY_FLOAT", 
                        b"BINARY_OP_MULTIPLY_INT", b"BINARY_OP_SUBTRACT_FLOAT", b"BINARY_OP_SUBTRACT_INT", 
                        b"BINARY_SUBSCR_ADAPTIVE", b"BINARY_SUBSCR_DICT", b"BINARY_SUBSCR_GETITEM", 
                        b"BINARY_SUBSCR_LIST_INT", b"BINARY_SUBSCR_TUPLE_INT", b"CALL_ADAPTIVE", 
                        b"CALL_PY_EXACT_ARGS", b"CALL_PY_WITH_DEFAULTS", b"COMPARE_OP_ADAPTIVE", 
                        b"COMPARE_OP_FLOAT_JUMP", b"COMPARE_OP_INT_JUMP", b"COMPARE_OP_STR_JUMP", 
                        b"EXTENDED_ARG_QUICK", b"JUMP_BACKWARD_QUICK", b"LOAD_ATTR_ADAPTIVE", 
                        b"LOAD_ATTR_INSTANCE_VALUE", b"LOAD_ATTR_MODULE", b"LOAD_ATTR_SLOT", 
                        b"LOAD_ATTR_WITH_HINT", b"LOAD_CONST__LOAD_FAST", b"LOAD_FAST__LOAD_CONST", 
                        b"LOAD_FAST__LOAD_FAST", b"LOAD_GLOBAL_ADAPTIVE", b"LOAD_GLOBAL_BUILTIN", 
                        b"LOAD_GLOBAL_MODULE", b"LOAD_METHOD_ADAPTIVE", b"LOAD_METHOD_CLASS", 
                        b"LOAD_METHOD_MODULE", b"LOAD_METHOD_NO_DICT", b"LOAD_METHOD_WITH_DICT", 
                        b"LOAD_METHOD_WITH_VALUES", b"PRECALL_ADAPTIVE", b"PRECALL_BOUND_METHOD", 
                        b"PRECALL_BUILTIN_CLASS", b"PRECALL_BUILTIN_FAST_WITH_KEYWORDS", 
                        b"PRECALL_METHOD_DESCRIPTOR_FAST_WITH_KEYWORDS", b"PRECALL_NO_KW_BUILTIN_FAST", 
                        b"PRECALL_NO_KW_BUILTIN_O", b"PRECALL_NO_KW_ISINSTANCE", b"PRECALL_NO_KW_LEN", 
                        b"PRECALL_NO_KW_LIST_APPEND", b"PRECALL_NO_KW_METHOD_DESCRIPTOR_FAST", 
                        b"PRECALL_NO_KW_METHOD_DESCRIPTOR_NOARGS", b"PRECALL_NO_KW_METHOD_DESCRIPTOR_O", 
                        b"PRECALL_NO_KW_STR_1", b"PRECALL_NO_KW_TUPLE_1", b"PRECALL_NO_KW_TYPE_1", 
                        b"PRECALL_PYFUNC", b"RESUME_QUICK", b"STORE_ATTR_ADAPTIVE", 
                        b"STORE_ATTR_INSTANCE_VALUE", b"STORE_ATTR_SLOT", b"STORE_ATTR_WITH_HINT", 
                        b"STORE_FAST__LOAD_FAST", b"STORE_FAST__STORE_FAST", b"STORE_SUBSCR_ADAPTIVE", 
                        b"STORE_SUBSCR_DICT", b"STORE_SUBSCR_LIST_INT", b"UNPACK_SEQUENCE_ADAPTIVE", 
                        b"UNPACK_SEQUENCE_LIST", b"UNPACK_SEQUENCE_TUPLE", b"UNPACK_SEQUENCE_TWO_TUPLE", 
                        b"DO_TRACING"]

structure_entry = "&&TARGET_{},"


class PythonRemap:

    def __init__(self, python_dir):
        self.non_arg_mnemonic_dict = {}
        self.arg_mnemonic_dict = {}
        self.additional_mnemonic_dict = {}

        self.remapped_non_arg_mnemonic_dict = {}
        self.remapped_arg_mnemonic_dict = {}

        self.python_path = os.path.join(os.getcwd(), python_dir)
        
        self.opcode_target = os.path.join(self.python_path, "Python", "opcode_targets.h")
        self.opcode_h = os.path.join(self.python_path, "Include", "opcode.h")
        self.opcode_py = os.path.join(self.python_path, "Lib", "opcode.py")

    @staticmethod
    def sort_dictionary_by_value(mnemonic_dict):
        return dict(sorted(mnemonic_dict.items(), key=lambda x: x[1]))


    @staticmethod
    def get_current_opcodes_from_file(opcode_file, mnemonic_list, mnemonic_dict):

        for line in opcode_file:
            match = re.search(r"#define\s+(\w+)\s+(\d+)", line)
            if match:
                string_name = match.group(1)
                integer_value = int(match.group(2))
                if string_name.encode() in mnemonic_list:
                    mnemonic_dict[string_name] = integer_value         

        return

    @staticmethod
    def remap_opcodes(mnemonic_dict):

        keys = list(mnemonic_dict.keys())
        shuffled_keys = random.sample(keys, len(keys))
        remapped_dict = {key: mnemonic_dict[shuffled_keys[i]] for i, key in enumerate(keys)}
        return remapped_dict

    @staticmethod
    def replace_opcode_h_information(opcode_file, remapped_mnemonic_dict):

        modified_content = []
        for line in opcode_file:
            match = re.search(r"#define\s+(\w+)\s+(\d+)", line)
            if match:
                string_name = match.group(1)
                if string_name in remapped_mnemonic_dict:
                    integer_value = remapped_mnemonic_dict[string_name]
                    modified_line = line.replace(match.group(2), str(integer_value))
                    modified_content.append(modified_line)
                else:
                    modified_content.append(line)
            else:
                modified_content.append(line)

        return modified_content
    
    @staticmethod
    def replace_opcode_py_information(opcode_file, remapped_mnemonic_dict):

        modified_content = []
        for line in opcode_file:
            match = re.search(r"([a-zA-Z_]+)\('([^']*)', (\d+)\)", line)
            if match:
                opcode_name = match.group(2)
                integer = int(match.group(3))
                updated_int = remapped_mnemonic_dict.get(opcode_name)
                if updated_int != None:
                    modified_line = line.replace(str(integer), str(updated_int))
                else:
                    modified_line = line
                modified_content.append(modified_line)

            else:
                modified_content.append(line)

        return modified_content

    @staticmethod
    def build_opcode_targets(mnemonic_dict):

        ordered_mnemonics = PythonRemap.sort_dictionary_by_value(mnemonic_dict)

        structure_entries = []
        for opcode_name in ordered_mnemonics:
            entry = structure_entry.format(opcode_name)
            structure_entries.append(entry)
            
        target_structure = '\n    '.join(structure_entries[:-1])
        target_structure += ("\n    &&_unknown_opcode," * 74)
        target_structure += "\n    &&TARGET_DO_TRACING"

        target_structure = "static void *opcode_targets[256] = {\n    " + target_structure + "\n};"

        return target_structure

def main():

    python_directory = sys.argv[1]

    pyRemap = PythonRemap(python_directory)

    with open(pyRemap.opcode_h, "r") as f:
        opcode_h_data = f.readlines()

        pyRemap.get_current_opcodes_from_file(opcode_h_data, non_arg_mnemonics, pyRemap.non_arg_mnemonic_dict)
        pyRemap.get_current_opcodes_from_file(opcode_h_data, arg_mnemonics, pyRemap.arg_mnemonic_dict)
        pyRemap.get_current_opcodes_from_file(opcode_h_data, additional_mnemonics, 
                                              pyRemap.additional_mnemonic_dict)


        pyRemap.remapped_non_arg_mnemonic_dict = pyRemap.remap_opcodes(pyRemap.non_arg_mnemonic_dict)
        pyRemap.remapped_arg_mnemonic_dict = pyRemap.remap_opcodes(pyRemap.arg_mnemonic_dict)

        opcode_h_data = pyRemap.replace_opcode_h_information(opcode_h_data, 
                                                             pyRemap.remapped_non_arg_mnemonic_dict)
        opcode_h_data = pyRemap.replace_opcode_h_information(opcode_h_data, 
                                                             pyRemap.remapped_arg_mnemonic_dict)

        with open(pyRemap.opcode_h, "w") as f1:
            f1.writelines(opcode_h_data)

        with open(pyRemap.opcode_py, "r") as f2:
            opcode_py_data = f2.readlines()

            combined_mnemonic_dict = {**pyRemap.remapped_non_arg_mnemonic_dict, 
                                      **pyRemap.remapped_arg_mnemonic_dict, 
                                      **pyRemap.additional_mnemonic_dict}

            opcode_py_data = pyRemap.replace_opcode_py_information(opcode_py_data, 
                                                                   combined_mnemonic_dict)
            
            with open(pyRemap.opcode_py, "w") as f3:
                f3.writelines(opcode_py_data)


            with open(pyRemap.opcode_target, "w") as f4:
                opcode_targets = pyRemap.build_opcode_targets(combined_mnemonic_dict)
                f4.writelines(opcode_targets)

    #os.chdir(python_directory)
    #os.system("./configure && make")

    return

if __name__ == "__main__":
    main()