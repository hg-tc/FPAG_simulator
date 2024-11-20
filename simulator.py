from PE import PE_array
from ETE import ETE,controller,sfm_ETE
from FTF import FTF
from ETF_accum import ETF
from bram import bram, bram_reader
from pinv import pinv

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib as mpl



def simulator(mission_type_in, PE_num_in,only_back, show):
    mission_type = mission_type_in
    # param
    input_data_range = 10000
    readdata_speed = 256

    PE_num = PE_num_in
    PE_array0 = PE_array(PE_num, mission_type)
    GTG_array0 = PE_array(PE_num, mission_type)
    GTG_controller = controller()
    if(mission_type == 1 or mission_type == 2):
        ETE0 = ETE()
    elif(mission_type == 3 or mission_type == 4):
        ETE0 = pinv()
    sfm_ETE0 = sfm_ETE()
    ETF0 = ETF(mission_type)
    FTF0 = FTF()
    pinv0 = pinv()
    element_reader = bram_reader()
    element_multi = controller()
    G_reader0 = bram_reader()
    mbm = bram(3)
    wbm = bram(2)

    instruction_set = []
    file_path = 'data/Inst_012085.txt'
    if(mission_type==1):
        file_path = 'data/Inst_mono.txt'
    elif(mission_type==2):
        file_path = 'data/Inst_fusion.txt'
    elif(mission_type==3):
        file_path = 'data/Inst_sfm2.txt'
    elif(mission_type==4):
        file_path = 'data/Inst_sfm3.txt'
    with open(file_path,'r') as file:
        instruction = file.readline()
        counts = 0
        while instruction:
            #
            instruction_set.append(instruction)
            instruction = file.readline()
            counts += 1
        print(counts,"instructions are loaded")
    
    print(instruction_set)
    # generate small instruction
    instruction_set2 = []
    LOAD_num = 0
    ADD_num = 0
    multi_num = 0
    GTG_num = 0
    ptr = 0
    while ptr < len(instruction_set):
        instruction_now = instruction_set[ptr]
        if instruction_now[0:4] == '0001':
            pi = int(instruction_now[4:8],2)
            rbs = int(instruction_now[8:17],2)
            mbd = int(instruction_now[8:17],2)
            length = int(instruction_now[17:30],2)
            last = 0
            inst_last = 0
            for i in range(length):
                if(i == length - 1):
                    inst_last = int(instruction_now[31])
                    last = int(instruction_now[30])
                instruction_set2.append([1,pi,rbs+i,mbd+i*6,last,inst_last])
                LOAD_num += 1
            # print('===============Load================')
            pass
        elif instruction_now[0:4] == '0010':
            mbs = int(instruction_now[4:13],2)
            last = int(instruction_now[13])
            code = instruction_now[14:]
            add_num = 0
            for i in range(9):
                if(code[i*2 : 2+i*2]) != '00' :
                    add_num += 1
                    # print(code, 'plus')
            instruction_set2.append([2,last,add_num])
            ADD_num += 1
            # print('===============Add================')
            pass
        elif instruction_now[0:4] == '0011':
            pi = int(instruction_now[4:8],2)
            length = int(instruction_now[8:],2)
            for i in range(length):
                if(i == length-1):
                    instruction_set2.append([3,pi,1])
                    multi_num += 1
                else:
                    instruction_set2.append([3,pi,0])
                    multi_num += 1
                # print('===============Element_nulti================')
            pass
        elif instruction_now[0:4] == '0100':
            pi = int(instruction_now[4:8],2)
            length = int(instruction_now[8:],2)
            length = int(length*(length + 1) / 2)
            for i in range(length):
                if(i == length-1):
                    instruction_set2.append([4,pi,1])
                    GTG_num += 1
                else:
                    instruction_set2.append([4,pi,0])
                    GTG_num += 1
                # print('===============GTG================')
            pass
        elif instruction_now[0:4] == '0101':
            instruction_set2.append([5])
            pass
        elif instruction_now[0:4] == '0110':
            instruction_set2.append([6])
            # print('===============Write================')
            pass
        else:
            # print('===============processing================')
            pass
        ptr += 1
        

    rbram_data_length = 2048
    inst_read = 0
    inst_write = 0
    print(instruction_set2)
    count = 0
    # executing
    inst_num=len(instruction_set2)
    excuted_table=[0]*len(instruction_set2)
    inst_ptr = 0
    waiting_buffer  =[]
    next_ptr_buffer = []
    necessery_ptr_buffer = []

    instruction_processing = np.zeros(4)
    PE_in_workload = np.zeros(PE_num)
    PE_out_workload = np.zeros(PE_num)
    GTG_in_workload = np.zeros(PE_num)
    GTG_out_workload = np.zeros(PE_num)

    instruction_processing.reshape(4,1)
    PE_in_workload.reshape(PE_num,1)
    PE_out_workload.reshape(PE_num,1)
    GTG_in_workload.reshape(PE_num,1)
    GTG_out_workload.reshape(PE_num,1)

    FTF_workload = np.zeros(3)
    FTF_workload.reshape(3,1)

    PE_load_in_state = np.zeros(PE_num)
    PE_load_in_state.reshape(PE_num,1)
    PE_ele_in_state = np.zeros(PE_num)
    PE_ele_in_state.reshape(PE_num,1)

    GTG_in_state = np.zeros(PE_num)
    GTG_in_state.reshape(PE_num,1)

    ETE_add_workload = [0]
    Instruction_process_list = []
    Instruction_group = []
    GTG_pi = []
    changing_pi = 0
    changing_pi2 = 0

    # LOAD_IN = []
    ELE_IN = []
    GTG_IN = []

    for i in range(PE_num):
        # LOAD_IN.append(None)
        ELE_IN.append(None)
        GTG_IN.append(0)


    data = []
    load_num = 0
    acc_num = 0
    ete_num = 0
    gtg_num = 0

    Jacobian_comp = 0
    # executing
    print("num ", LOAD_num, ADD_num, multi_num, GTG_num, inst_num)
    processed = []
    for i in range(len(instruction_set2)):
        processed.append(False)

    pre_inst_ptr = 0
    count936 = 0

    GTG_read_num = 0
    processed_Load = 0
    processed_ADD = 0
    processed_multi = 0
    processed_GTG = 0

    pallel_num = 0

    while(1) :
        if(inst_ptr is not None):
            instruction_now = instruction_set2[inst_ptr]
        else:
            instruction_now = None
        print("inst", inst_ptr,instruction_now,count)

        # if(inst_ptr==1903):
        #     break

        n = 24-PE_num*2
        num_one_time = n*30
        cycle_one_time = num_one_time * 13 * 12 / n
        if(not only_back):
            if(count%cycle_one_time < num_one_time and count >=cycle_one_time):
                rbram_data_length += 1024
        # rbram_data_length += 256

        instruction_valid = 0

        if(instruction_now):
            if instruction_now[0] == 1:
                jump = None
                if(instruction_now[5] == 1):
                    jump = inst_ptr+1
                if(rbram_data_length > 1024):
                    load_num+=1
                    if(only_back):
                        rbram_data_length  = rbram_data_length 
                    else:
                        rbram_data_length  -= 1024 
                    pi = instruction_now[1]
                    mission_list = []
                    target_list = []
                    ETE_inst_list = []
                    for i in range(PE_num):
                        dis = (i-pi)%PE_num
                        if(mission_type==1 or mission_type==2):
                            # if(i==pi or dis==1):
                            #     if(mission_type==1 or mission_type==2):
                            #         mission_list.append(1)
                            #     else:
                            #         mission_list.append(3)
                            # elif(dis==2 or dis==3 or dis==4):
                            #     mission_list.append(6)
                            # else:
                            #     mission_list.append(0)

                            # if(i==pi or dis==1):
                            #     target_list.append(1)
                            # elif(dis==2 or dis==3 or dis==4):
                            #     target_list.append(2)
                            # else:
                            #     target_list.append(0)
                            if(i==pi):
                                mission_list.append([1,1,6,6,6])
                                target_list.append([1,1,2,2,2])
                            else:
                                mission_list.append([0,0,0,0,0])
                                target_list.append([0,0,0,0,0])      
                            if(i==pi):
                                ETE_inst_list.append([jump,None,None,None,None])
                            else:
                                ETE_inst_list.append([None,None,None,None,None])
                        elif(mission_type==3):
                            # if(i==pi):
                            #     mission_list.append(3)
                            # elif(dis==1):
                            #     mission_list.append(3)
                            # else:
                            #     mission_list.append(0)

                            # if(i==pi):
                            #     target_list.append(1)
                            # elif(dis==1):
                            #     target_list.append(2)
                            # else:
                            #     target_list.append(0)

                            if(i==pi):
                                mission_list.append([3,3])
                                target_list.append([1,2])
                            else:
                                mission_list.append([0,0])
                                target_list.append([0,0])

                            if(i==pi):
                                ETE_inst_list.append([jump,None])
                            else:
                                ETE_inst_list.append([None,None])
                                
                        elif(mission_type==4):
                            if(i==pi):
                                mission_list.append([3,3,6,6,6])
                                target_list.append([1,1,2,2,2])
                            else:
                                mission_list.append([0,0,0,0,0])
                                target_list.append([0,0,0,0,0])

                            if(i==pi):
                                ETE_inst_list.append([jump,None,None,None,None])
                            else:
                                ETE_inst_list.append([None,None,None,None,None])
                    mission_list = np.array(mission_list).T
                    target_list = np.array(target_list).T
                    ETE_inst_list = np.array(ETE_inst_list).T
                    # print(mission_list)
                    for i in range(mission_list.shape[0]):
                        PE_array0.input(mission_list[i],target_list[i],ETE_inst_list[i])
                    # print("PE_INPUT: ",mission_list,target_list,ETE_inst_list)
                    # LOAD_IN = mission_list
                    # PE_array0.input([1,1,6,6,6,0],[1,1,2,2,2,0],[jump,None,None,None,None,None])
                    if(mission_type == 1 or mission_type == 2):
                        ETE0.input(1, instruction_now[4])
                        if(instruction_now[4]):LOAD_num+=1 
                    elif(mission_type == 3 or mission_type == 4):
                        multi_num,add_num = sfm_ETE0.input(2, instruction_now[4])
                        if(multi_num != None):
                            mission_list2 = []
                            target_list2 = []
                            instruction_jump = []
                            for i in range(PE_num):
                                if(i==pi):
                                    mission_list2.append(multi_num*3)
                                    target_list2.append(3)
                                    instruction_jump.append(None)
                                else:
                                    mission_list2.append(0)
                                    target_list2.append(0)
                                    instruction_jump.append(None)
                            PE_array0.input(mission_list2,target_list2,instruction_jump)
                            
                    instruction_valid = 1
                print('===============Load================')
                pass
            elif instruction_now[0] == 2:
                acc_num += 1
                jump = None
                if(instruction_now[1]==1):
                    jump = inst_ptr+1
                ETF0.input(instruction_now[2],jump)
                instruction_valid = 1
                print('===============Add================')
                pass
            elif instruction_now[0] == 3:
                ete_num += 1
                # while 1:
                pallel_num += 1
                jump = None
                if(instruction_now[2]==1):
                    jump = inst_ptr+1
                element_reader.input(1)
                element_multi.input(0,instruction_now[1],jump)
                # element_multi.input(0,changing_pi2,jump)
                # changing_pi2 = (changing_pi2 + 1)%6
                instruction_valid = 1
                    # Instruction_group.append(inst_ptr)
                    # if(inst_ptr+1<len(instruction_set2) and instruction_set2[inst_ptr+1][0]==3):
                    #     inst_ptr += 1
                    #     instruction_now = instruction_set2[inst_ptr]
                    # else:
                        # break

                # print("ETE_INST_BUFF",element_multi.instruction_buffer)
                print('===============Element_nulti================')
                pass
            elif instruction_now[0] == 4:
                gtg_num += 1
                # while 1:
                pallel_num += 1
                if(mission_type==1 or mission_type==2):
                    G_reader0.input(1)
                if(mission_type==3 or mission_type==4):
                    G_reader0.input(1)
                GTG_controller.input(0,instruction_now[1], None)
                # GTG_controller.input(0,changing_pi, None)
                # changing_pi = (changing_pi + 1)%6
                instruction_valid = 1
                    # Instruction_group.append(inst_ptr)
                    # if(inst_ptr+1<len(instruction_set2) and instruction_set2[inst_ptr+1][0]==4):
                    #     inst_ptr += 1
                    #     instruction_now = instruction_set2[inst_ptr]
                    # else:
                    #     break
                print('===============GTG================')

            elif instruction_now[0] == 5:
                inst_read = 1
                instruction_valid = 1
                print('===============Read================')
                pass
            elif instruction_now[0] == 6:
                inst_write =1
                instruction_valid = 1
                print('===============Write================')
                pass
            else:
                print('===============other================')
                pass
        else:
            instruction_valid = 1
            print('===============processing================')

        if(instruction_now and instruction_now[0]==4):
            GTG_pi.append(instruction_now[1])
        else:
            GTG_pi.append(-1)


        mb_read_request = [element_reader.reading_mb,G_reader0.reading_mb,ETF0.reading_mb]
        read_valid,_,read_out = mbm.step(mb_read_request,[])
        # print(mb_read_request, read_valid, read_out)

        element_reader.step(read_valid[0])
        G_reader0.step(read_valid[1])
        ETF0.step(read_valid[2]) #

            
        ETE0.step()
        element_multi.input(read_out[0]==1, None, None)
        multi_now = element_multi.step(not ETE0.output_buffer_empty)


        print('multi_now', multi_now, ETE0.output_buffer_empty)
        if(multi_now):
            mission_list = []
            target_list = []
            ETE_inst_list = []
            for i in range(PE_num):
                mission_list.append(0)
                target_list.append(0)
                ETE_inst_list.append(None)
            pi, ETE_inst = element_multi.output()
            # print("ETE_out", pi, ETE_inst)
            ETE_inst_list[pi] = ETE_inst
            if(mission_type==1 or mission_type==2):
                mission_list[pi] = 1 #VINS
                target_list[pi] = 1 #VINS
            elif(mission_type==3 or mission_type==4):
                mission_list[pi] = 3
                target_list[pi] = 3
            if(ETE_inst is not None):
                ETE0.output(1)
            PE_array0.input(mission_list,target_list,ETE_inst_list)
            ELE_IN = [i * 0.5 for i in mission_list]


        GTG_ready = 0
        # if(mission_type==3 or mission_type==4):
        #     if(read_out[1]==1):
        #         GTG_read_num += 1
        #     if(GTG_read_num >=3):
        #         GTG_read_num-=3
        #         GTG_ready = 1
        if(mission_type==1 or mission_type==2 or mission_type==3 or mission_type==4):
            GTG_ready = read_out[1]

        GTG_controller.input(GTG_ready, None, None)
        GTG_now = GTG_controller.step(1)

        print("GTG", GTG_now, GTG_read_num, GTG_ready)

        if(GTG_now):
            GTG_new = 1
        else:
            GTG_new = 0
        data.append(GTG_new)
        
        if(GTG_now):
            mission_list = []
            target_list = []
            GTG_inst_list = []
            for i in range(PE_num):
                mission_list.append(0)
                target_list.append(0)
                GTG_inst_list.append(None)
            pi, _ = GTG_controller.output()
            mission_list[pi] = 1 * 6#VINS
            target_list[pi] = 2 #VINS
            if(0):
                GTG_array0.input(mission_list,target_list,GTG_inst_list)
                GTG_IN = mission_list
            elif(mission_type == 3 or mission_type==4 or mission_type==1 or mission_type==2):
                PE_array0.input(mission_list,target_list,GTG_inst_list)


        
        FTF_mvalid = 0
        ETE_add = 0
        PE_array0.step()
        GTG_array0.step()
        GTG_output = []
        PE_write_mb = []
        PE_write_fb = []
        for i in range(PE_num):
            GTG_output.append(1)
            PE_write_mb.append(0)
            PE_write_fb.append(0)
        GTG_array0.output(GTG_output)
        
        for i in range(PE_num):
            if PE_array0.target[i] == 2:
                FTF_mvalid += 1
                PE_write_fb[i] = 1
            elif PE_array0.target[i] == 1:
                PE_write_mb[i] = 1
            elif PE_array0.target[i] == 3:
                PE_write_fb[i] = 1 #need new
                sfm_ETE0.add()
                
        ETE_result = sfm_ETE0.step()
        if(ETE_result):
            ETE0.input(1)
            LOAD_num+=1 
            

        for i in range(PE_num):
            if GTG_array0.target[i] == 2:
                FTF_mvalid += 1
                
        FTF0.input(FTF_mvalid)

        PE_write_mb.extend([ETF0.writing_mb])
        mb_write_valid = mbm.test_write(PE_write_mb)
        # print(PE_write_mb,mb_write_valid,PE_write_fb)
        # print([sum(x) for x in zip(mb_write_valid[:-1],PE_write_fb)])
        _ , PE_Done_list = PE_array0.output([x or y for x,y in zip(mb_write_valid[:-1],PE_write_fb)])
        for i in range(PE_num):
            if(PE_Done_list[i]):
                # print("jump_to: ", PE_Done_list[i])
                waiting_buffer.append(PE_Done_list[i])
                # if(PE_Done_list[i]==8040):
                #     count936 += 1
        # print("PE ", PE_Done_list, [x or y for x,y in zip(mb_write_valid[:-1],PE_write_fb)])
        # if count936==1:
        #     print("jump from PE")
        #     break

        _ , ADD_Done = ETF0.output()

        print("ETF ", ETF0.input_buffer, ETF0.instruction_buffer, ETF0.output_buffer)

        if(ADD_Done):
            waiting_buffer.append(ADD_Done)

                
        #FTF, wbram,wrte_mb
        FTF_read = FTF0.reading_fb
        FTF_write = FTF0.writing_fb
        wb_read_list = [inst_read, FTF_read]
        wb_write_list = [inst_write, FTF_write]

        wb_read_valid,wb_write_valid,wb_read_out = wbm.step(wb_read_list,wb_write_list)
        print("FTF_valid: ", FTF_mvalid)
        if FTF_mvalid>6:
            FTF0.step(6 ,wb_read_out[1])
        elif(FTF_mvalid != 0):
            FTF0.step(FTF_mvalid ,wb_read_out[1])
        elif FTF0.reading_mb:
            FTF0.step(3 ,wb_read_out[1])#process GTG first
        else: 
            FTF0.step(0 ,wb_read_out[1])
        
        # instruction process
        if(instruction_now and instruction_valid):
            if(instruction_now[0]==1):
                for i in range(inst_ptr+1,inst_num):
                    if(instruction_set2[i][0]==1):
                        next_ptr_buffer.append(i)   
                        break
            elif(instruction_now[0]==3 and instruction_now[2]==0 or instruction_now[0]==4 and instruction_now[2]==0 or instruction_now[0]==2 and instruction_now[1]==0):
                for i in range(inst_ptr+1,inst_num):
                    print(instruction_now ,"find",instruction_set2[i])
                    if(instruction_set2[i][0]==instruction_now[0]):
                        necessery_ptr_buffer.append(i)   
                        break
        # print("inst_now: ", inst_ptr)                
        # print("buffer_show",necessery_ptr_buffer,waiting_buffer,next_ptr_buffer)

        if(instruction_valid == 1):

            if(inst_ptr != None or Instruction_group):
                print(inst_ptr, Instruction_group)
                Instruction_process_list.append(instruction_now[0])
                if(Instruction_group):
                    for i in range(len(Instruction_group)):
                        if(processed[i]==False):
                            processed[i] = True
                        elif(processed[inst_ptr]==True):
                            print(instruction_now, inst_ptr, pre_inst_ptr)
                            for i in range(-10,10):
                                print(instruction_set2[inst_ptr+i],inst_ptr+i)
                            print("error")
                            break
                elif(inst_ptr != None):
                    if(processed[inst_ptr]==False):
                        processed[inst_ptr] = True
                        # print(inst_ptr,"--------------------------right--------------------")
                    elif(processed[inst_ptr]==True):
                        print(instruction_now, inst_ptr, pre_inst_ptr)
                        for i in range(-10,10):
                            print(instruction_set2[inst_ptr+i],inst_ptr+i)
                        print("error")
                        break

                if(instruction_now[0] == 1):
                    processed_Load += 1
                elif(instruction_now[0] == 2):
                    processed_ADD += 1
                elif(instruction_now[0] == 3):
                    processed_multi += pallel_num
                elif(instruction_now[0] == 4):
                    processed_GTG += pallel_num
            else:
                Instruction_process_list.append(0)

            if(necessery_ptr_buffer):
                print('exec necessery')
                inst_ptr = necessery_ptr_buffer.pop(0)
            elif(waiting_buffer):
                print('exec waiting')
                inst_ptr = waiting_buffer.pop(0)
                # if(inst_ptr==8040):
                #     print("jump")
                #     break
            elif(next_ptr_buffer):
                print('exec next')
                inst_ptr = next_ptr_buffer.pop(0)
            else:
                inst_ptr = None
            pre_inst_ptr = inst_ptr
        else:
            Instruction_process_list.append(0)

        pallel_num = 0
        Instruction_group = []
        print("FTF",FTF0.Done,FTF0.input_buffer,FTF0.mb_data_num,FTF0.fb_data_num,FTF0.output_buffer,FTF0.process_target_buffer)
        if(mission_type==3 or mission_type==4):
            print("pinv",ETE0.input_buffer,ETE0.process_buffer,ETE0.Done)
            print("controller ", element_multi.pi_buffer, element_multi.instruction_buffer)

        else:
            print("pinv",ETE0.input_buffer,ETE0.output_buffer,ETE0.process_target_buffer,ETE0.Done)
            print("controller ", element_multi.pi_buffer, element_multi.instruction_buffer)

        
        # for i in range(len(instruction_set2)):
        #     if(processed[i]==False and i < 21):
        #         print(i)
        # for i in range(-10,10):
        #         print(instruction_set2[10+i],10+i)

        # print(PE_array0.output_buffer_empty,ETF0.output_buffer_empty,FTF0.Done)
        all_excited = all(k==True for k in processed)

        print("all_excited ",all_excited)
        print("buffer ", waiting_buffer, next_ptr_buffer, necessery_ptr_buffer, inst_ptr)
        print("Done ", PE_array0.output_buffer_empty, ETF0.output_buffer_empty, FTF0.Done, ETE0.Done)

        if(count > 200000):
            for i in range(len(instruction_set2)):
                if(processed[i]==False and i < 50000):
                    print("error", i)
        # for i in range(-10,10):
        #         print(instruction_set2[2900+i],2900+i)

        if(not waiting_buffer and not next_ptr_buffer and not necessery_ptr_buffer and inst_ptr is None and PE_array0.Done and GTG_array0.Done and ETF0.output_buffer_empty and FTF0.Done and ETE0.Done and all_excited):
            # for i in range(len(instruction_set2)):
            #     if(processed[i]==False and i < 21):
            #         print("error", i)
            # for i in range(-10,10):
            #     print(instruction_set2[20+i],20+i)
            print(count)
            print("load_num ", load_num, acc_num, ete_num, gtg_num)
            break
        
        count+=1
        instruction_processing = np.c_[instruction_processing, [processed_Load,processed_ADD,processed_multi,processed_GTG]]

        PE_in_work,PE_out_work = PE_array0.state()
        GTG_in_work,GTG_out_work = GTG_array0.state()

        PE_in_workload=np.c_[PE_in_workload,PE_in_work]
        PE_out_workload=np.c_[PE_out_workload,PE_out_work]
        GTG_in_workload=np.c_[GTG_in_workload,GTG_in_work]
        GTG_out_workload=np.c_[GTG_out_workload,GTG_out_work]

        FTF_work = [FTF0.input_buffer,FTF0.mb_data_num,FTF0.fb_data_num]
        FTF_workload = np.c_[FTF_workload,FTF_work]

        # PE_load_in_state = np.c_[PE_load_in_state, LOAD_IN]
        
        PE_ele_in_state = np.c_[PE_ele_in_state, ELE_IN]

        GTG_in_state = np.c_[GTG_in_state, GTG_IN]

        ETE_add_workload.append(len(ETE0.adder_buffer))

        FTF0.output(6)

        # LOAD_IN = []
        ELE_IN = []
        GTG_IN = []

        for i in range(PE_num):
            # LOAD_IN.append(None)
            ELE_IN.append(None)
            GTG_IN.append(0)
        # print(FTF0.input_buffer,FTF0.mb_data_num,FTF0.fb_data_num,FTF0.reading_mb )
    x = np.linspace(0, count+1, count+1)
    y=[]

    fig, ax = plt.subplots()
    for i in range(PE_num):
        y = PE_in_workload[i]
        ax.plot(x,y, label="PE"+str(i))
    ax.set_title('PE_in_workload')
    ax.legend()

    # fig2, ax2 = plt.subplots()
    # for i in range(PE_num):
    #     y = PE_out_workload[i]
    #     ax2.plot(x,y)
    # ax2.set_title('PE_out_workload')


    fig3, ax3 = plt.subplots()
    for i in range(PE_num):
        y = GTG_in_workload[i]
        ax3.plot(x,y,label="PE"+str(i))
    ax3.set_title('GTG_in_workload')
    ax3.legend()


    # fig4, ax4 = plt.subplots()
    # for i in range(PE_num):
    #     y = GTG_out_workload[i]
    #     ax4.plot(x,y)
    # ax4.set_title('GTG_out_workload')

    fig5, ax5 = plt.subplots()
    for i in range(3):
        label = None
        if(i==0): label='input'
        elif(i==1): label='mb'
        else: label='fb'
        y = FTF_workload[i]
        ax5.plot(x,y, label=label)
    ax5.legend()
    ax5.set_title('FTF_workloadS')

    # fig, ax = plt.subplots()
    # for i in range(1):
    #     y = PE_load_in_state[i]
    #     y2 = PE_ele_in_state[i]
    #     ax.scatter(x,y,c='r')
    #     ax.scatter(x,y2,c='b')
    # ax.set_title('PE_in_state')

    
    # for i in range(PE_num):
    #     fig, ax = plt.subplots()
    #     y = GTG_in_state[i]
    #     ax.plot(x,y)
    # ax.set_title('GTG_in_state')

    fig, ax = plt.subplots()
    for i in range(4):
        label = None
        if(i==0): label='Load'
        elif(i==1): label='ADD'
        elif(i==2): label='multi'
        else: label='GTG'
        y = instruction_processing[i]
        ax.plot(x,y, label=label)
    ax.legend()
    ax.set_title('instruction_processing')

    fig, ax = plt.subplots()
    y = ETE_add_workload
    ax.plot(x,y)
    ax.set_title('ETE_add_workload')

    fig, ax = plt.subplots()
    y = Instruction_process_list
    ax.scatter(x,y,c='r',s=1)
    ax.set_title('instruction_process_list')

    fig, ax = plt.subplots()
    y = GTG_pi
    print(x.size, len(y))
    ax.scatter(x,y,c='b',s=1)
    ax.set_title('GTG_pi')
    if show:
        plt.show()

    return [count, load_num, acc_num, ete_num, gtg_num], PE_in_workload, GTG_in_workload, FTF_workload, instruction_processing, ETE_add_workload, Instruction_process_list, GTG_pi


import os

def run_sim_and_save(mission_type_in, PE_num_in, only_back_in, show_in):
    mission_type = mission_type_in
    PE_num = PE_num_in
    only_back = only_back_in
    show = show_in
    info = str(mission_type)+"_"+str(PE_num)+"_"+str(only_back)
    count, PE_in_workload, GTG_in_workload, FTF_workload, instruction_processing, ETE_add_workload, Instruction_process_list, GTG_pi = simulator(mission_type, PE_num, only_back, show)
    os.chdir(r'./log/')
    np.save('base_'+info, np.array(count))
    np.save('PE_in_workload_'+info, PE_in_workload)
    np.save('GTG_in_workload_'+info, GTG_in_workload)
    np.save('FTF_workload_'+info, FTF_workload)
    np.save('instruction_processing_'+info, instruction_processing)
    np.save('ETE_add_workload_'+info, ETE_add_workload)
    np.save('Instruction_process_list_'+info, Instruction_process_list)
    np.save('GTG_pi_'+info, GTG_pi)
    
import sys

if __name__ == '__main__':
    mission_type = 1
    PE_num = 6
    only_back = 1
    show = 1

    if(len(sys.argv)==5):
        mission_type = int(sys.argv[1])
        PE_num = int(sys.argv[2])
        only_back  = int(sys.argv[3])
        show  = int(sys.argv[4])
    # print(mission_type)
        run_sim_and_save(mission_type, PE_num, only_back, show)
    else:
        print("no parameter")
    # plt.show()