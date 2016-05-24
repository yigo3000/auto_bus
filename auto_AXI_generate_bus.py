#-*- coding: UTF-8 -*-
# Software License Agreement (BSD License)
#
# Copyright (c) 2016, Terry Yu..
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Terry Yu nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

#This code can do:
#1. generate AXI BUS. 1st, you must have a module whose port is any kind.
#2. generate instance of the AXI bus we just generated.
#3. generate AXI bus of "vivado". Use function "gen_xilinx_axi_lite_slave()".
#
import logging
logger=logging.getLogger('auto_AXI_verilog_logger')
from auto_bus_verilog import auto_bus_verilog

class auto_AXI_generate_bus(auto_bus_verilog):
    def __init__(self,src):
        super().__init__(src)
        self.read_only_num_of_reg = []
        self.write_read_num_of_reg = []
        self.total_reg = 0

    def UI_set(self):
        super().UI_set()
        # user input: choose bus type
        while(True):
            self.bus_type = input(r'''Please choose a bus_type:
            a. AXI_LITE(slave)  b.Avalon_mm(slave)
            type 'a' or 'b'
            ''').lower()
            if self.bus_type == 'a':
                break
            elif self.bus_type=='b':
                break
            else:
                print('Error, unknown option.')
        #user input member: self.addr_width, self.data_width,
        while(True):
            self.addr_width = input(r'''Please set address width of the bus:
            type a integer in range [4-128], typically '8' or '32'
            ''').lower()
            if int(self.addr_width) >= 4 and int(self.addr_width)<= 128:
                break
            else:
                print('Error, value too large or too small.')

        while(True):
            self.data_width = input(r'''Please set data width of the bus :
            type a integer in range [4-128], typically '8' or '32'
            ''').lower()
            if int(self.data_width) >= 4 and int(self.data_width)<= 128:
                break
            else:
                print('Error, value too large or too small.')


    def compute_reg(self, port_list,addr_width):#equation: num_of_reg= flat(  (port_width+addr_width-1)/addr_width  )
        #compute the reg needed by output port
        import re
        data_width_of_port = []
        num_of_reg = []
        for i in range(0, len(port_list)):
            if port_list[i][0]== None:
                data_width_of_port.append(1)
                num_of_reg.append(1)
            else:
                data_width_of_port.append(int((re.search(r"(\d*)\s*:",port_list[i][0])).group(1)) + 1)
                num_of_reg.append( (data_width_of_port[-1]+addr_width-1)//addr_width)#"//" rounded to minus infinity
        logger.debug(data_width_of_port)
        logger.debug(num_of_reg)
        return num_of_reg

    def compute_total_reg(self):
        self.read_only_num_of_reg = self.compute_reg(self.output_port_internal,int(self.addr_width))
        self.write_read_num_of_reg = self.compute_reg(self.input_port_internal,int(self.addr_width))
        self.total_reg = sum(self.read_only_num_of_reg)+sum(self.write_read_num_of_reg)
        logger.debug("total reg is:")
        logger.debug(self.total_reg)
    def gen_axi_lite_slave(self):
        self.compute_total_reg()
        #read in the axi_lite_slave template
        src_code = None
        with open("axi_lite_slave_template.v","r",encoding = 'utf-8') as src_file:
            src_code = src_file.readlines()
            src_code[1] = "module %s_axi\n" %self.module_name#every time change the template's line NO., must change the number in "[]"
            src_code[5] = "input  wire [%s - 1:0]  AXI_AWADDR,\n" %self.addr_width
            src_code[9] = "input  wire [%s-1:0]     AXI_WDATA,\n" %self.data_width
            src_code[10] = "input  wire [%s/8-1:0]   AXI_WSTRB,\n" %self.data_width
            src_code[16] = "input wire [%s - 1:0]  AXI_ARADDR,\n" %self.addr_width
            src_code[20] = "output  [%s-1:0]         AXI_RDATA,\n" %self.data_width

            src_code[27] = "localparam ADDR_WIDTH = %s;\n" %self.addr_width
            src_code[28] = "localparam DATA_WIDTH = %s;\n" %self.data_width
            src_code[29] = "localparam NUM_OF_TOTAL_WORDS = %s;\n" %self.total_reg
            src_code[30] = "localparam NUM_OF_WRITE_READ_WORDS = %s \n;" %str(sum(self.write_read_num_of_reg))
            #write down external port
            src_code[2] = "(\n"
            for i in range(0,len(self.input_port_extern)):
                if self.input_port_extern[i][0]==None:
                    src_code[2] += "input %s,\n" %self.input_port_extern[i][1]
                else:
                    src_code[2] += "input %s %s,\n" %(self.input_port_extern[i][0],self.input_port_extern[i][1])
            for i in range(0,len(self.output_port_extern)):
                if self.output_port_extern[i][0]==None:
                    src_code[2] += "output wire %s,\n" %self.output_port_extern[i][1]
                else:
                    src_code[2] += "output wire %s %s,\n" %(self.output_port_extern[i][0],self.output_port_extern[i][1])
            #write down instance
            src_code[406] = self.gen_instance_under_axi()
        with open(self.module_name+'_axi.v',"w",encoding = 'utf-8') as dst_file:
            dst_file.writelines(src_code)

    def gen_memory_map(self):
        pass

    def gen_instance_under_axi(self):#redefined function
        #self.compute_total_reg()
        self.instance = None
        #generate parameter
        if self.parameter==None:
            self.instance = "%s %s_i (\n" %(self.module_name,self.module_name)
        else:
            self.instance = "%s \n#(" %(self.module_name)
            for i in range(0, len(self.parameter)):
                self.instance += ".%s(%s),\n" %(self.parameter[i][0],str(self.set_parameter[i]))
            self.instance = self.instance[0:-2]+(")\n%s_i(\n" %self.module_name)
        reg_cnt = 0
        #generate write read port
        for i in range(0, len(self.input_port_internal)):
            self.instance += ".%s( {" %self.input_port_internal[i][1]
            for j in range (0,self.write_read_num_of_reg[i]):
                self.instance += "slv_reg[%s]," %str(reg_cnt)
                reg_cnt = reg_cnt+1
            self.instance = self.instance[0:-1]
            self.instance += "}),\n"
        #read only port
        reg_cnt = 0
        for i in range(0, len(self.output_port_internal)):
            self.instance += ".%s( {" %self.output_port_internal[i][1]
            for j in range (0,self.read_only_num_of_reg[i]):
                self.instance += "slv_reg_read_only[%s]," %str(reg_cnt)
                reg_cnt = reg_cnt+1
            self.instance = self.instance[0:-1]
            self.instance += "}),\n"
        #external port
        for i in range (0,len(self.input_port_extern)):
            self.instance += ".%s( %s ),\n" %(self.input_port_extern[i][1],self.input_port_extern[i][1])
        for i in range (0,len(self.output_port_extern)):
            self.instance += ".%s( %s ),\n" %(self.output_port_extern[i][1],self.output_port_extern[i][1])
        self.instance = self.instance[0:-2]+");\n"
        logger.debug(self.instance)
        return self.instance

    def xilinx_gen_instance_under_axi(self):
        '''only used for gen xilinx Vivado'''
        #self.compute_total_reg()
        self.instance = None
        #generate parameter
        if self.parameter == []:
            self.instance = "%s %s_i (\n" %(self.module_name,self.module_name)
        else:
            self.instance = "%s \n#(" %(self.module_name)
            for i in range(0, len(self.parameter)):
                self.instance += ".%s(%s),\n" %(self.parameter[i][0],str(self.parameter[i][0]))
            self.instance = self.instance[0:-2]+(")\n%s_i(\n" %self.module_name)
        reg_cnt = 0
        #generate write read port
        for i in range(0, len(self.input_port_internal)):
            self.instance += ".%s( {" %self.input_port_internal[i][1]
            logger.debug(self.write_read_num_of_reg)
            for j in range (0,self.write_read_num_of_reg[i]):
                self.instance += "slv_reg%s," %str(reg_cnt)
                reg_cnt = reg_cnt+1
            self.instance = self.instance[0:-1]
            self.instance += "}),\n"
        #external port
        for i in range (0,len(self.input_port_extern)):
            self.instance += ".%s( %s ),\n" %(self.input_port_extern[i][1],self.input_port_extern[i][1])
        for i in range (0,len(self.output_port_extern)):
            self.instance += ".%s( %s ),\n" %(self.output_port_extern[i][1],self.output_port_extern[i][1])
        self.instance = self.instance[0:-2]+");\n"
        logger.debug(self.instance)
        return self.instance
    def gen_xilinx_axi_lite_slave(self):
        '''only used for gen xilinx vivado ip. Generate two files: 1st, axi bus,'''
        self.compute_total_reg()
        #read in the xlinx axi template file
        src_code = None
        with open("xilinx_axi_lite_slave_template.v") as src_file:
            src_code = src_file.readlines()
            src_code[3] = "module %s_axi #\n" %self.module_name #write module name

            #write parameter
            for i in range(0, len(self.parameter)):
                src_code[6] += "parameter integer %s = %s,\n" %(self.parameter[i][0],str(self.set_parameter[i]))

            # write external port
            for i in range(0,len(self.input_port_extern)):
                if self.input_port_extern[i][0]==None:
                    src_code[17] += "input wire %s,\n" %self.input_port_extern[i][1]
                else:
                    src_code[17] += "input wire %s %s,\n" %(self.input_port_extern[i][0],self.input_port_extern[i][1])
            for i in range(0,len(self.output_port_extern)):
                if self.output_port_extern[i][0]==None:
                    src_code[17] += "output wire %s,\n" %self.output_port_extern[i][1]
                else:
                    src_code[17] += "output wire %s %s,\n" %(self.output_port_extern[i][0],self.output_port_extern[i][1])

            # write down instance
            src_code[392] = self.xilinx_gen_instance_under_axi()
        with open(self.module_name+"_axi.v","w",encoding = "utf-8") as dst_file:
            dst_file.writelines(src_code)
    def __del__(self):
        super().__del__()