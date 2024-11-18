class FTF:
    
    def __init__(self):
        self.input_buffer = 0

        self.process_target_buffer = [0,0,0,0,0,0,0,0,0,0,0]
        self.output_buffer = []

        self.reading_mb = False
        self.reading_fb = False
        self.writing_fb = False

        self.mb_data_num = 0
        self.fb_data_num = 0

        self.Done = True

    def input(self, input_data):
        self.input_buffer += input_data
        if(input_data != 0):
            self.reading_mb = True
    
    def output(self, out_num):
        if len(self.output_buffer) >= out_num:
            self.output_buffer = self.output_buffer[out_num:]
            return out_num
        elif len(self.output_buffer) != 0:
            self.output_buffer = []
            return len(self.output_buffer)
        else:
            return None

    def step(self, mbvalid, fbvalid):
        if mbvalid:
            self.mb_data_num += mbvalid
        if fbvalid:
            self.fb_data_num += 6
        
        if(self.mb_data_num > 0 and self.fb_data_num > 0 and self.input_buffer != 0):
            process_num = min(self.input_buffer,self.mb_data_num,self.fb_data_num,6)
            # process_num = 100
            self.input_buffer -= process_num
            self.mb_data_num -= process_num
            self.fb_data_num -= process_num
            if(self.input_buffer < 0):
                self.input_buffer=0
            if(self.mb_data_num < 0):
                self.mb_data_num=0
            if(self.fb_data_num < 0):
                self.fb_data_num=0

            self.process_target_buffer.append(1)
        else:
            self.process_target_buffer.append(0)
        self.process_target_buffer.pop(0)

        # output process
        if self.process_target_buffer[0]!= 0:
            self.output_buffer.append(self.process_target_buffer[0])


        # empty judge
        if self.input_buffer > self.mb_data_num:
            self.reading_mb = True
        else:
            self.reading_mb = False
        
        if self.input_buffer > self.fb_data_num:
            self.reading_fb = True
        else:
            self.reading_fb = False

        if self.output_buffer:
            self.writing_mb = True
        else:
            self.writing_mb = False
        
        if(self.input_buffer == 0 and all(k==0 for k in self.process_target_buffer) and not self.output_buffer):
            self.Done = True
        else:
            self.Done = False
            # print("FTF: ",self.input_buffer,all(k==0 for k in self.process_target_buffer),self.output_buffer)


if __name__ == '__main__':
    cycle_num = 0
    FTF0 = FTF()
    FTF0.input(3)
    FTF0.input(2)
    FTF0.input(3)

    for i in range(80):
        FTF0.step(1)
        print(cycle_num, FTF0.output(1))
        # print(FTF0.process_target_buffer)
        cycle_num = cycle_num + 1
