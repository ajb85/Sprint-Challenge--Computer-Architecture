"""CPU functionality."""

import sys

ldi = 0b10000010
prn = 0b01000111
hlt = 0b00000001
call = 0b01010000
add = 0b10100000
ret = 0b00010001
mul = 0b10100010
push = 0b01000101
pop = 0b01000110
call = 0b01010000
add = 0b10100000
ret = 0b00010001

# sprint
cmp = 0b10100111
jeq = 0b01010101
jmp = 0b01010100
jne = 0b01010110

#alu
add = 0b10100000
and_gate = 0b10101000
xor_gate = 0b10101011
or_gate = 0b10101010
not_gate = 0b01101001
shl = 0b10101100
shr = 0b10101101
mod = 0b10100100

class RAM:
    def __init__(self, size):
        self.storage = [None] * size

    def pop(self, pointer):
        if(pointer >= 0 and pointer < len(self.storage)):
            value = self.storage[pointer]
            self.storage[pointer] = None
            return value
        return None

    def push(self, pointer, value):
        if(pointer >= 0 and pointer < len(self.storage)):
            if(self.storage[pointer] == None):
                self.storage[pointer] = value
                return True
            print(f"Possible Stack Overflow found at {pointer}: {self.storage[pointer]}")
        return False

    def read(self, address):
        return self.storage[address] if address < len(self.storage) else None

    def write(self, address, value):
        self.storage[address] = value

    def getSize(self):
        return len(self.storage)

class Commands:
    def __init__(self, cpu):
        self.list = {
            ldi:self.ldi, 
            prn:self.prn, 
            hlt:self.hlt, 
            mul:self.mul, 
            push:self.push, 
            pop:self.pop,
            call:self.call,
            add:self.add,
            cmp:self.cmp,
            jeq:self.jeq,
            jmp:self.jmp,
            jne:self.jne
        }
        self.cpu = cpu

    def cmp(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        val1 = self.cpu.register[op_a]
        val2 = self.cpu.register[op_b]
        flag = f"00000{'1' if val1 < val2 else '0'}{'1' if val1 > val2 else '0'}{'1' if val1 == val2 else '0'}"
        self.cpu.register[4] = int(flag,2)
        return 2

    def jmp(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        self.cpu.pc = self.cpu.register[op_a] - 1
        return 0
    
    def jne(self, op_a=None, op_b=None):
        if(self.cpu.register[4] % 2 == 0):
            self.jmp(op_a)
            return 0
        return 1

    def jeq(self, op_a=None, op_b=None):
        if(self.cpu.register[4] == 0b0000001):
            self.jmp(op_a)
            return 0
        return 1

    def call(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        address = self.cpu.register[op_a]
        while True:
            instruction = self.cpu.ram.read(address)
            if(instruction == ret or instruction == None):
                return 1
            inc = self.list[instruction](address+1, address+2)
            address += inc + 1

    def add(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)

        self.cpu.register[op_a] += self.cpu.register[op_b]
        return 2

    def ldi(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        self.cpu.register[op_a] = op_b
        return 2

    def prn(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        print(self.cpu.register[op_a])
        return 1
        
    def mul(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        print(self.cpu.ram.read(op_a) * self.cpu.ram.read(op_b))
        return 2

    def push(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        pointer = self.cpu.register[len(self.cpu.register) - 1]
        wasSuccessful = self.cpu.ram.push(pointer - 1, self.cpu.register[op_a])
        if(wasSuccessful):
            self.cpu.register[len(self.cpu.register) - 1] = pointer - 1
        return 1

    def pop(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        pointer = self.cpu.register[len(self.cpu.register) - 1]
        value = self.cpu.ram.pop(pointer)
        self.cpu.register[op_a] = value
        self.cpu.register[len(self.cpu.register) - 1] = pointer + 1
        return 1

    def hlt(self, op_a=None, op_b=None):
        return self.cpu.ram.getSize()

class ALUCommands:
    def __init__(self, cpu):
        self.list = {
            add:self.add,
            and_gate:self.and_gate,
            xor_gate:self.xor_gate,
            or_gate:self.or_gate,
            not_gate:self.not_gate,
            shl:self.shl,
            mod:self.mod
        }
        self.cpu = cpu

    def add(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        self.register[reg_a] += self.register[reg_b]
        return 2

    def and_gate(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        val1 = self.cpu.register[op_a]
        val2 = self.cpu.register[op_b]
        self.cpu.register[op_a] = val1 and val2
        print(f"AND gate evaluation: {val1 and val2}")
        return 2

    def xor_gate(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        self.cpu.register[op_a] = (val1 or val2) and not (val1 and val2)
        print(f"XOR gate evaluation: {(val1 or val2) and not (val1 and val2)}")
        return 2

    def or_gate(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        self.cpu.register[op_a] = val1 or val2
        print(f"OR gate evaluation: {val1 or val2}")
        return 2

    def not_gate(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        # op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        self.cpu.register[op_a] = not self.cpu.register[op_a]
        print(f"NOT gate evaluation: {not self.cpu.register[op_a]} is now {self.cpu.register[op_a]}")
        return 1

    def shl(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        val1 = self.cpu.register[op_a]
        val2 = self.cpu.register[ob_b]
        newValue = f"{bin(val1,2)}{'0' * val2}"
        if(len(newString) <= 8):
            self.cpu.register[op_a] = int(newString,2)
        else:
            print("ERROR: can't shift that far, value too large")
        return 2

    def shr(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        val1 = self.cpu.register[op_a]
        val2 = self.cpu.register[ob_b]
        newValue = f"{'0' * val2}{bin(val1,2)}"
        print(f"Shift right: {val1} to {newValue}")
        if(len(newString) <= 8):
            self.cpu.register[op_a] = int(newString,2)
        else:
            self.cpu.register[op_a] = int(newString[:8],2)
        return 2

    def mod(self, op_a=None, op_b=None):
        op_a = self.cpu.ram.read(self.cpu.pc + 1) if op_a == None else self.cpu.ram.read(op_a)
        op_b = self.cpu.ram.read(self.cpu.pc + 2) if op_b == None else self.cpu.ram.read(op_b)
        val1 = self.cpu.register[op_a]
        val2 = self.cpu.register[ob_b]
        newValue = val1 % val2
        self.cpu.register[op_a] = newValue
        print(f"MOD evaluation: {val1} MOD {val2} = {newValue}")
        return 2

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.ram = RAM(256)
        self.register[len(self.register) - 1] = self.ram.getSize() - 1
        self.pc = 0
        self.commands = Commands(self)
        self.aluCommands = ALUCommands(self)

    def load(self):
        """Load a program into memory."""
        with open(f"{sys.argv[1]}") as f:
            # Load user-specified file and save it in RAM
            i = 0
            for line in f:
                command = line.replace(" ", "")[:8]
                if(self.isValidCommand(command)):
                    self.ram.write(i, int(command, 2))
                    i += 1

    def alu(self, ir):
        """ALU operations."""
        self.aluCommands.list[ir]()
        
        # else:
        #     raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram.read(self.pc),
            self.ram.read(self.pc + 1),
            self.ram.read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        ir = self.ram.read(0)
        while True:
            if(ir == None):
                return
            if(ir in self.commands.list):
                inc = self.commands.list[ir]()
            elif(ir in self.aluCommands.list):
                inc = self.alu(ir)
            else:
                print(f"ERROR: Invalid command {ir} at command {self.pc}")
            
            self.pc += 1 + inc
            ir = self.ram.read(self.pc)
    
    def isValidCommand(self, command):
        for char in command:
            if(char != "0" and char !="1"):
                return False
        return True
