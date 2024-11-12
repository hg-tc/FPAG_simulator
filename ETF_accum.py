class ETF:
    
    def __init__(self, mission_type):
        self.input_buffer = []
        self.instruction_buffer = []
        self.mission_type = mission_type

        self.process_buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

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
        out_num = 1
        if(self.mission_type==1 or self.mission_type==2):
            out_num = 1
        else:
            out_num = 3

        if len(self.output_buffer) >= out_num and self.output_buffer and out_num != 0:
            self.output_buffer = self.output_buffer[out_num:]
            inst_out = self.instruction_buffer.pop(0)
            return 1, inst_out

        else:
            return None,None

    def step(self, valid):
        if(self.mission_type==1 or self.mission_type==2):
            cycle_num = 1
        else:
            cycle_num = 3

        if self.input_buffer:
            if valid:
                if(self.input_buffer[0] <= 1):
                    self.input_buffer.pop(0)
                    for i in range(cycle_num):
                        self.adder_buffer.append(2)
                else:
                    self.input_buffer[0] = self.input_buffer[0] - 1
                    for i in range(cycle_num):
                        self.adder_buffer.append(1)

        # adder process

        # print('======',self.process_target_buffer[0],self.adder_num,self.adder_cycle,self.adder_processing)
        if self.adder_buffer:
            # print(self.adder_buffer[0])
            if self.adder_buffer[0]==2:
                self.process_buffer.append(1)
                self.process_buffer.pop(0)
            else:
                self.process_buffer.append(0)
                self.process_buffer.pop(0)
            
            self.adder_buffer.pop(0)
        else:
            self.process_buffer.append(0)
            self.process_buffer.pop(0)


        if self.process_buffer[0] == 1 :
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
        
        if self.output_buffer or not all(k==0 for k in self.process_buffer):
            self.output_buffer_empty = False
        else:
            self.output_buffer_empty = True


if __name__ == '__main__':
    cycle_num = 0
    ETF0 = ETF(3)
    ETF0.input(3,100)
    ETF0.input(2,101)
    ETF0.input(1,102)

    for i in range(80):
        ETF0.step(1)
        print(cycle_num, ETF0.output())
        print(ETF0.input_buffer,ETF0.instruction_buffer,ETF0.output_buffer, ETF0.adder_processing)
        print(ETF0.adder_buffer,ETF0.process_buffer,ETF0.adder_num,ETF0.adder_cycle)
        print("----------------------")
        cycle_num = cycle_num + 1
