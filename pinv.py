class pinv:
    
    def __init__(self):
        self.input_buffer = 0
        self.process_buffer = 0

        self.output_buffer = []
        self.adder_buffer = []

        self.output_buffer_empty = True
        self.Done = True

    def input(self, input_data):
        self.input_buffer += input_data
    
    def output(self, out_num):
        if len(self.output_buffer) >= out_num:
            self.output_buffer = self.output_buffer[out_num:]
            return out_num
        else:
            return None

    def step(self):
        if self.process_buffer == 0 and self.input_buffer != 0:
            self.process_buffer = 10 # process time
            self.input_buffer -= 1
        elif self.process_buffer != 0:
            self.process_buffer -= 1
            if self.process_buffer==0 :
                self.output_buffer.append(1)

        if self.output_buffer:
            self.output_buffer_empty = False
        else:
            self.output_buffer_empty = True
        
        if self.input_buffer == 0 and self.process_buffer == 0 and not self.output_buffer:
            self.Done = True
        else:
            self.Done = False
        
            # print("FTF: ",self.input_buffer,all(k==0 for k in self.process_target_buffer),self.output_buffer)


if __name__ == '__main__':
    cycle_num = 0
    pinv0 = pinv()
    pinv0.input(2)

    for i in range(2020):
        pinv0.step()
        # print(pinv0.output_buffer_empty,cycle_num)
        if(not pinv0.output_buffer_empty):
            print(pinv0.output_buffer_empty,cycle_num)
            pinv0.output(1)
        # print(FTF0.process_target_buffer)
        cycle_num = cycle_num + 1
