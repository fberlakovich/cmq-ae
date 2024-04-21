def find_provenance_backward_stack_position(instructions, initial_stack, initial_ip, stack_position):
    last_provenance = {}

    model_stack = initial_stack[:]
    stack_ptr = len(model_stack) - 1
    ip = initial_ip

    while ip >= 0:
        instruction = instructions[ip]
        operation, pop_count, push_count = instruction

        # Update the sources of the model_stack positions
        for i in range(push_count):
            if push_count > 0:
                last_provenance[stack_ptr - i] = instruction

        stack_ptr = stack_ptr - push_count + pop_count

        if stack_position in last_provenance:
            return last_provenance[stack_position]



        # Update the instruction pointer
        ip -= 1

    return None  # Stack position not found

# Example instructions: (operation, pop_count, push_count)
instructions = [
    ('LOAD_GLOBAL', 0, 1),
    ('LOAD_ATTR', 1, 1),
    ('LOAD_FAST', 0, 1),
    ('LOAD_FAST', 0, 1),
    ('LOAD_CONST', 0, 1),
    ('BINARY_OP', 2, 1),
    ('BINARY_OP', 2, 1),
]

initial_stack = [5, 4, 3, 2, 1]
initial_ip = len(instructions) - 1  # Current instruction pointer
stack_position_to_find = 3  # Indexing from the top of the stack

provenance = find_provenance_backward_stack_position(instructions, initial_stack, initial_ip, stack_position_to_find)

if provenance:
    print(f"The stack position {stack_position_to_find} came from instruction: {provenance}")
else:
    print(f"The stack position {stack_position_to_find} does not have a known provenance.")
