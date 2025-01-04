

# very much a crappy program so far ..
def tac_to_vm(tac_program):
    label_counter = 11  # start the label counter at 11?
    label_map = {}
    vm_code = []
    
    # 1: Process labels and jumps
    for line in tac_program:
        parts = line.split()
        
        if len(parts) == 4:  # special parts?
            # directly add the instruction
            vm_code.append(f"{parts[0]} {parts[1]} {parts[2]}")
        
        elif len(parts) == 3:  # assignments like t1 = x + y
            # arithmetic and assignments
            if parts[1] in ['+', '-', '*', '/']:
                vm_code.append(f"{parts[0]} {parts[1]} {parts[2]}")
            else:
                vm_code.append(f"{parts[0]} {parts[1]}")
        
        elif len(parts) == 5:  # jumps like 'if t7 goto L1'
            if parts[0] == "if":
                # replace with numeric label
                label = parts[4]  # "L1"
                if label not in label_map:
                    label_map[label] = label_counter
                    label_counter += 1
                vm_code.append(f"{parts[1]} {parts[2]} {label_map[label]}")
            elif parts[0] == "goto":  # "goto L2"
                label = parts[1]
                if label not in label_map:
                    label_map[label] = label_counter
                    label_counter += 1
                vm_code.append(f"GOTO {label_map[label]}")
        
        elif len(parts) == 2:  #  label and commands
            if parts[0] == "label":
                label = parts[1]
                label_map[label] = label_counter
                vm_code.append(f"LABEL {label_map[label]}")
            else:
                vm_code.append(f"{parts[0]} {parts[1]}")
    
    return vm_code

# testing instructions..
tac_program = [
    "x = 2025",
    "y = 1477",
    "t1 = x + y",
    "t2 = 16",
    "t3 = 5 * t2",
    "t4 = t3 / 2",
    "t5 = t1 - t4",
    "z = t5",
    "t6 = t1",
    "t7 = 0",
    "if t7 goto L1",
    "call func, 2",
    "param t6",
    "return t5",
    "write t7",
    "goto 17",
]

vm_code = tac_to_vm(tac_program)
for line in vm_code:
    print(line)
