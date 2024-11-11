class bram:
    
    def __init__(self,interface):
        inter = []
        for i in range(interface):
            inter.append(0)
        self.read_buffer = [inter,inter]


    def test_read(self,read_request):
        read_num = 0
        for i in range(len(read_request)):
            if(read_request[i]==1) and read_num < 2:
                read_num += 1
            else:
                read_request[i] = 0
        return read_request
    
    def test_write(self,write_request):
        write_num = 0
        for i in range(len(write_request)):
            if(write_request[i]==1) and write_num < 2:
                write_num += 1
            else:
                write_request[i] = 0
        return write_request

    def step(self,read_request,write_request):
        read_num = 0
        for i in range(len(read_request)):
            if(read_request[i]==1) and read_num < 2:
                read_num += 1
            else:
                read_request[i] = 0

        self.read_buffer.pop(0)
        self.read_buffer.append(read_request)

        write_num = 0
        for i in range(len(write_request)):
            if(write_request[i]==1) and write_num < 2:
                write_num += 1
            else:
                write_request[i] = 0

        return read_request, write_request, self.read_buffer[0]

class bram_reader:
    def __init__(self):
        self.input_buffer = []
        self.reading_mb = False
        
    def input(self, length):
        self.input_buffer.append(length)
        self.reading_mb = True
    def step(self,valid):
        self.reading_mb = False
        if self.input_buffer:
            if valid:
                if(self.input_buffer[0] == 1):
                    self.input_buffer.pop(0)
                    if(self.input_buffer):
                        self.reading_mb = True
                else:
                    self.input_buffer[0] = self.input_buffer[0] - 1
                    self.reading_mb = True

if __name__ == '__main__':
    cycle_num = 0
    bram0 = bram()

    for i in range(10):
        read_valid, write_valid, read_out = bram0.step([1,1,1], [1,0,1])
        print(cycle_num, read_valid, write_valid, read_out)
        # print(ETE0.process_target_buffer)
        cycle_num = cycle_num + 1
