class ETE:
    
    def __init__(self):
        self.input_buffer = []
        self.input_last_buffer = []

        self.process_target_buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.adder_cycle = 0
        self.adder_num = 0
        self.adder_processing = False
        self.adder_buffer = []

        self.output_buffer = []
        self.input_buffer_empty = True
        self.output_buffer_empty = True
        self.target = None

    def input(self, input_data, last):
       self.input_buffer.append(input_data)
       self.input_last_buffer.append(last)
       self.input_buffer_empty = False
    
    def output(self, out_num):
        if len(self.output_buffer) >= out_num:
            self.output_buffer = self.output_buffer[out_num:]
            return out_num
        else:
            return None

    def step(self):
        if self.input_last_buffer:
            self.process_target_buffer.pop(0)
            if(self.input_last_buffer[0] and self.input_buffer[0] == 1):
                self.process_target_buffer.append(2)
            else:
                self.process_target_buffer.append(1)
            
        else:
            self.process_target_buffer.pop(0)
            self.process_target_buffer.append(0)


        # input process
        if self.input_buffer:
            if(self.input_buffer[0] == 1):
                self.input_buffer.pop(0)
                self.input_last_buffer.pop(0)
            else:
                self.input_buffer[0] = self.input_buffer[0] - 1
        else:
            pass

        # adder process
        
        if self.process_target_buffer[0] != 0:
            self.adder_buffer.append(self.process_target_buffer[0])

        # print("ETE", self.adder_num,self.adder_cycle,self.adder_processing,self.adder_buffer)
        # print('======',self.process_target_buffer[0],self.adder_num,self.adder_cycle,self.adder_processing)
        if self.adder_buffer:
            # print(self.adder_buffer[0])
            if self.adder_processing == False:
                self.adder_num += 1
                if(self.adder_num>=2):
                    self.adder_cycle += 11 #adder_cycle
            if self.adder_processing == False and self.adder_buffer[0] == 2: 
                self.adder_processing = True
                self.adder_buffer.pop(0)

            if self.adder_processing == False:
                self.adder_buffer.pop(0)

        if self.adder_cycle >0 :
            self.adder_cycle -= 1
        elif self.adder_processing == True:
            self.adder_processing = False
            self.adder_num = 0
            self.output_buffer.append(1)
        
        # empty judge
        if self.input_buffer:
            self.input_buffer_empty = False
        else:
            self.input_buffer_empty = True
        
        if self.output_buffer:
            self.output_buffer_empty = False
        else:
            self.output_buffer_empty = True

class controller:
    def __init__(self):
        self.input_data_buffer = 0
        self.pi_buffer = []
        self.instruction_buffer = []
        self.reading_mb = False
        
    def input(self, data_ready, pi, instruction):
        if(data_ready):
            self.input_data_buffer+=1
        if(pi is not None):
            self.pi_buffer.append(pi)
            self.instruction_buffer.append(instruction)
    def output(self):
        # if
        return self.pi_buffer.pop(0), self.instruction_buffer.pop(0)
    def step(self,ETE_ready):
        if ETE_ready:
            if(self.input_data_buffer>0):
                self.input_data_buffer-=1
                return True
        return False


if __name__ == '__main__':
    cycle_num = 0
    ETE0 = ETE()
    ETE0.input(3,1)
    ETE0.input(2,0)
    ETE0.input(3,1)

    for i in range(80):
        ETE0.step()
        print(cycle_num, ETE0.output(1))
        # print(ETE0.process_target_buffer)
        cycle_num = cycle_num + 1
