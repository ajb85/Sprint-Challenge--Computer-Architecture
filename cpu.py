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
            add:self.add
        }
        self.cpu = cpu

    def call(self):
        op_a = self.cpu.ram.read(self.cpu.pc + 1)
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

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.ram = RAM(256)
        self.register[len(self.register) - 1] = self.ram.getSize() - 1
        self.pc = 0
        self.commands = Commands(self)

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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

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
            else:
                print(f"ERROR: Invalid command {ir}")
            
            self.pc += 1 + inc
            ir = self.ram.read(self.pc)
    
    def isValidCommand(self, command):
        for char in command:
            if(char != "0" and char !="1"):
                return False
        return True
