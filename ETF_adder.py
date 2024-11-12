class ETF:
    
    def __init__(self):
        self.input_buffer = []
        self.instruction_buffer = []

        self.adder_cycle = 0
        self.adder_num = 0
        self.adder_processing = False
        self.adder_buffer = []

        self.output_buffer = []

        self.reading_mb = False
        self.writing_mb = False
        self.output_buffer_empty = True

    def input(self, input_data,instruction):
        self.input_buffer.append(input_data)
        self.instruction_buffer.append(instruction)
        self.reading_mb = True
    
    def output(self):
        if self.output_buffer:
            self.output_buffer.pop(0)
            inst_out = self.instruction_buffer.pop(0)
            return 1, inst_out
        else:
            return None,None

    def step(self, valid):

        if self.input_buffer:
            if valid:
                if(self.input_buffer[0] == 1):
                    self.input_buffer.pop(0)
                    self.adder_buffer.append(2)
                else:
                    self.input_buffer[0] = self.input_buffer[0] - 1
                    self.adder_buffer.append(1)

        # adder process

        # print('======',self.process_target_buffer[0],self.adder_num,self.adder_cycle,self.adder_processing)
        if self.adder_buffer:
            # print(self.adder_buffer[0])
            if self.adder_processing == False:
                self.adder_num += 1
                if(self.adder_num>=2):
                    self.adder_cycle += 11 #adder_cycle
            if self.adder_buffer[0] == 2: 
                self.adder_processing = True

            if self.adder_processing == False or self.adder_buffer[0] == 2:
                self.adder_buffer.pop(0)

        if self.adder_cycle >0 :
            self.adder_cycle -= 1
        elif self.adder_processing == True and self.adder_num != 1:
            self.adder_processing = False
            self.adder_num = 0
            self.output_buffer.append(1)

        # empty judge
        if self.input_buffer:
            self.reading_mb = True
        else:
            self.reading_mb = False
        
        if self.output_buffer:
            self.writing_mb = True
        else:
            self.writing_mb = False
        
        if self.output_buffer or self.adder_cycle > 0:
            self.output_buffer_empty = False
        else:
            self.output_buffer_empty = True


if __name__ == '__main__':
    cycle_num = 0
    ETF0 = ETF()
    ETF0.input(3,100)
    ETF0.input(2,101)
    ETF0.input(1,102)

    for i in range(80):
        ETF0.step(1)
        print(cycle_num, ETF0.output())
        print(ETF0.input_buffer,ETF0.instruction_buffer,ETF0.output_buffer)
        cycle_num = cycle_num + 1
