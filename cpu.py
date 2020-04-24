import sys

#operations
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7

class CPU:
    
    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.pc = 0
        self.running = True
        self.flag = 0b00000001
        self.branch_table = {
            HLT: self.HALT,
            LDI: self.LOAD,
            PRN: self.PRINT,
            PUSH: self.PUSH,
            POP: self.POP,
            CALL: self.CALL,
            RET: self.RET,
            CMP: self.CMP,
            JMP: self.JMP,
            JEQ: self.JEQ,
            JNE: self.JNE
        }

    #Halt op
    def HALT(self, op_a, op_b):
        self.running = False

    #Load op
    def LOAD(self, op_a, op_b):
        self.reg[op_a] = op_b
        self.pc += 3

    #Print op
    def PRINT(self, op_a, op_b):
        print(self.reg[op_a])
        self.pc += 2

    def PUSH(self, op_a, op_b):
        self.push(self.reg[op_a])
        self.pc += 2

    def POP(self, op_a, op_b):
        self.reg[op_a] = self.pop()
        self.pc += 2

    def CALL(self, op_a, op_b):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2
        update_reg = self.ram[self.pc + 1]
        self.pc = self.reg[update_reg]

    def RET(self, op_a, op_b):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def CMP(self, op_a, op_b):
        self.alu('CMP', op_a, op_b)
        self.pc += 3

    def JMP(self, op_a, op_b):
        self.pc = self.reg[op_a]

    def JEQ(self, op_a, op_b):
        if self.flag & 0b00000001:
            self.pc = self.reg[op_a]
        else:
            self.pc += 2

    def JNE(self, op_a, op_b):
        if not self.flag & 0b00000001:
            self.pc = self.reg[op_a]
        else:
            self.pc += 2

    def push(self, value):
        self.reg[SP] -= 1
        self.ram_write(value, self.reg[7])

    def pop(self):
        value = self.ram_read(self.reg[7])
        self.reg[SP] += 1
        return value

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        address = 0
        with open(sys.argv[1]) as prog:
            for line in prog:
                #No comments
                no_comment = line.split("#")
                value = no_comment[0].strip()
                #Ignore Blank crap
                if value == "":
                    continue
                #set base 2
                num = int(value, 2)
                self.ram[address] = num
                address += 1

    def alu(self, op, reg_a, reg_b):
        if op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        while self.running:
            IR = self.ram_read(self.pc)
            op_a = self.ram_read(self.pc + 1)
            op_b = self.ram_read(self.pc + 2)
            if int(bin(IR), 2) in self.branch_table:
                self.branch_table[IR](op_a, op_b)
            else:
                raise Exception(f'Invalid')