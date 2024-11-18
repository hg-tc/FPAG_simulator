class PE:
    
    def __init__(self,mission_type):
        self.input_buffer = []
        self.input_target_buffer = []
        self.input_instruction_buffer = []

        if(mission_type==1 or mission_type==2):
            self.process_target_buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            self.process_instruction_buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        else:
            self.process_target_buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            self.process_instruction_buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.output_buffer = []
        self.output_instruction_buffer = []
        self.input_buffer_empty = True
        self.output_buffer_empty = True
        self.target = None

    def input(self, input_data, target, instruction):
        if(input_data):
            self.input_buffer.append(input_data)
            self.input_target_buffer.append(target)
            self.input_instruction_buffer.append(instruction)
            self.input_buffer_empty = False
    
    def output(self, out_num):
        # print("PE_OUT_NOW: ", out_num, self.output_buffer, self.output_instruction_buffer)
        instruction_out = 0
        if len(self.output_buffer) >= out_num and self.output_buffer and out_num != 0:
            instruction_out = self.output_instruction_buffer[0]
            self.output_buffer = self.output_buffer[out_num:]
            self.output_instruction_buffer = self.output_instruction_buffer[out_num:]
            # print("PE_OUT_inst: ", instruction_out)
            return out_num, instruction_out
        else:
            return None,None

    def step(self):
        
        if self.input_target_buffer:
            self.process_target_buffer.pop(0)
            self.process_target_buffer.append(self.input_target_buffer[0])
            self.process_instruction_buffer.pop(0)
            if(self.input_buffer and self.input_buffer[0]==1):
                self.process_instruction_buffer.append(self.input_instruction_buffer[0])
            else:
                self.process_instruction_buffer.append(None)
        else:
            self.process_target_buffer.pop(0)
            self.process_target_buffer.append(0)
            self.process_instruction_buffer.pop(0)
            self.process_instruction_buffer.append(None)
        
        # if self.input_instruction_buffer:
        #     self.process_instruction_buffer.pop(0)
        #     self.process_instruction_buffer.append(self.input_instruction_buffer[0])
        # else:
        #     self.process_instruction_buffer.pop(0)
        #     self.process_instruction_buffer.append(0)


        # input process
        if self.input_buffer:
            if(self.input_buffer[0] <= 1 ):
                self.input_buffer.pop(0)
                self.input_target_buffer.pop(0)
                self.input_instruction_buffer.pop(0)
            else:
                self.input_buffer[0] = self.input_buffer[0] - 1
        else:
            pass



        # output process
        if self.process_target_buffer[0]!= 0:
            self.output_buffer.append(self.process_target_buffer[0])
            self.output_instruction_buffer.append(self.process_instruction_buffer[0])

        # if self.process_instruction_buffer[0]!= 0:
        #     self.output_instruction_buffer.append(self.process_instruction_buffer[0])


        if self.output_buffer:
            self.target = self.output_buffer[0]
        else:
            self.target = None

        # empty judge
        if self.input_buffer:
            self.input_buffer_empty = False
        else:
            self.input_buffer_empty = True
        
        if self.output_buffer or not all(k==0 for k in self.process_target_buffer):
            self.output_buffer_empty = False
        else:
            self.output_buffer_empty = True
        
        # print("PE_STEP_NOW: ", self.input_buffer, self.input_target_buffer, self.input_instruction_buffer,self.process_target_buffer,self.process_instruction_buffer,self.output_buffer)
    def state(self):
        input_work = 0
        if(self.input_buffer):
            for ele in range(len(self.input_buffer)):
                input_work  += self.input_buffer[ele]
        output_work = 0
        if(self.output_buffer):
            for ele in range(len(self.output_buffer)):
                output_work  += self.output_buffer[ele]
        
        return input_work,output_work




        
class PE_array:

    def __init__(self, PE_num, mission_type):
        self.input_buffer_empty = True
        self.output_buffer_empty = True
        self.Done = True
        self.target = None

        self.PE_num = PE_num
        self.PE_list = []
        for i in range(self.PE_num):
            self.PE_list.append(PE(mission_type))
    
    def input(self, input_data, target,instruction):
        for i in range(self.PE_num):
            self.PE_list[i].input(input_data[i], target[i],instruction[i])
            

    def output(self, out_num):
        output_list = []
        inst_list = []
        for i in range(self.PE_num):
            out, inst = (self.PE_list[i].output(out_num[i]))
            output_list.append(out)
            inst_list.append(inst)
        
        return output_list, inst_list

    def step(self):
        for i in range(self.PE_num):
            self.PE_list[i].step()
        
        self.input_buffer_empty = all(self.PE_list[i].input_buffer_empty for i in range(self.PE_num))
        self.output_buffer_empty = all(self.PE_list[i].output_buffer_empty for i in range(self.PE_num))
        self.Done = self.input_buffer_empty and self.output_buffer_empty
        self.target = [self.PE_list[i].target for i in range(self.PE_num)]

    def state(self):
        output_list = []
        output_list2 = []
        for i in range(self.PE_num):
            input_work, output_work = self.PE_list[i].state()
            output_list.append(input_work)
            output_list2.append(output_work)
        return output_list, output_list2

class GTG_controller:
    def __init__(self):
        self.input_buffer = []
        self.adder_buffer = []
        self.output_buffer = []
        self.adder_processing = False
        self.adder_num = 0
        self.adder_cycle = 0
    def input(self, length):
        self.input_buffer.append(length)
    
    def output(self, out_num):
        if len(self.output_buffer) >= out_num:
            self.output_buffer = self.output_buffer[out_num:]
            return out_num
        else:
            return None

    def step(self, valid):

        if self.input_buffer:
            if valid:
                if(self.input_buffer[0] == 1):
                    self.input_buffer.pop(0)
                    self.adder_buffer.append(2)
                else:
                    self.input_buffer[0] = self.input_buffer[0] - 1
                    self.adder_buffer.append(1)
        if self.adder_buffer:
            # print(self.adder_buffer[0])
            if self.adder_processing == False:
                self.adder_num += 1
                self.adder_cycle += self.adder_num #adder_cycle

            if self.adder_buffer[0] == 2: 
                self.adder_processing = True

            if self.adder_processing == False or self.adder_buffer[0] == 2:
                self.adder_buffer.pop(0)

        if self.adder_cycle >0 :
            self.adder_cycle -= 1
            self.output_buffer.append(1)
        elif self.adder_processing == True :
            self.adder_processing = False
            self.adder_num = 0
    

            
            


if __name__ == '__main__':
    cycle_num = 0
    PE0 = PE_array(3)
    PE0.input([6,6,1],[1,2,3])
    while(not (PE0.input_buffer_empty and PE0.output_buffer_empty)):
        PE0.step()
        print(cycle_num, PE0.output([1,1,1]))
        print(PE0.target)
        # print(PE0.process_target_buffer)
        cycle_num = cycle_num + 1
