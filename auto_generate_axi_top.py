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
import logging
logger=logging.getLogger('auto_AXI_verilog_logger')
#from auto_AXI_verilog.generate_top import generate_top
from auto_generate_top import generate_top
#from auto_AXI_verilog.auto_AXI_verilog import *
from auto_bus_verilog import *

class generate_axi_top(generate_top):
    def __init__(self,src):
        super().__init__(src)
        logger.debug("length of self.modules:")
        logger.debug(len(self.modules))
        self.arbitrators = [{}]#[{"type":, "master_module_name":,"slave_module_name":, "" }]
        self.masters = []
        self.slaves = []
    def gen_axi_top(self):
        arbitrator_code = ""
        slave_port_code = ""
        master_port_code = ""
        wire_code = ""
        master_inst_code = ""
        slave_inst_code = ""

        arbitrator_code = self.gen_axi_arbitrator_inst()
        for j in range(0,len(self.modules)):
            slave_inst_code += self.gen_axi_slave_inst(self.modules[j],str(j))#must be generated first! Cause this will set the ADDR_WIDTH and DATA_WIDTH.
        slave_port_code = super().gen_port()[0:-3]+",\n"#the external port of slave module
        wire_code = self.gen_axi_wire()
        master_inst_code = self.gen_master_inst()
        master_port_code = self.gen_master_port_code()

        dst_code = slave_port_code + master_port_code + wire_code + master_inst_code + arbitrator_code + slave_inst_code + "\nendmodule\n"
        with open("top.v","w", encoding = 'utf-8') as dst_file:
            dst_file.writelines(dst_code)

    def gen_axi_slave_inst(self,o_auto_AXI_verilog,index):#index is string
        o_auto_AXI_verilog.UI_set()
        o_auto_AXI_verilog.instance = None
        #generate parameter
        if o_auto_AXI_verilog.parameter==[]:
            o_auto_AXI_verilog.instance = "%s %s_i (\n" %(o_auto_AXI_verilog.module_name,o_auto_AXI_verilog.module_name)
        else:
            o_auto_AXI_verilog.instance = "%s \n#(" %(o_auto_AXI_verilog.module_name)
            for i in range(0, len(o_auto_AXI_verilog.parameter)):
                o_auto_AXI_verilog.instance += ".%s(%s),\n" %(o_auto_AXI_verilog.parameter[i][0],str(o_auto_AXI_verilog.set_parameter[i]))
            o_auto_AXI_verilog.instance = o_auto_AXI_verilog.instance[0:-2]+(")\n%s_i(\n" %o_auto_AXI_verilog.module_name+"_i")

        #input port internal
        for i in range (0,len(o_auto_AXI_verilog.input_port_internal)):
            o_auto_AXI_verilog.instance += ".%s( slave_%s_%s ),\n" %(o_auto_AXI_verilog.input_port_internal[i][1],index,o_auto_AXI_verilog.input_port_internal[i][1])
        #output port internal
        for i in range (0,len(o_auto_AXI_verilog.output_port_internal)):
            o_auto_AXI_verilog.instance += ".%s( slave_%s_%s ),\n" %(o_auto_AXI_verilog.output_port_internal[i][1],index,o_auto_AXI_verilog.output_port_internal[i][1])
        #input port external
        for i in range (0,len(o_auto_AXI_verilog.input_port_extern)):
            o_auto_AXI_verilog.instance += ".%s( %s ),\n" %(o_auto_AXI_verilog.input_port_extern[i][1],o_auto_AXI_verilog.input_port_extern[i][1])
        #output port external
        for i in range (0,len(o_auto_AXI_verilog.output_port_extern)):
            o_auto_AXI_verilog.instance += ".%s( %s ),\n" %(o_auto_AXI_verilog.output_port_extern[i][1],o_auto_AXI_verilog.output_port_extern[i][1])
        o_auto_AXI_verilog.instance = o_auto_AXI_verilog.instance[0:-2]+");\n"
        logger.debug(o_auto_AXI_verilog.instance)
        return o_auto_AXI_verilog.instance

    def gen_axi_arbitrator_inst(self):
        with open("axi_master_arbitrator.v","r",encoding = "utf-8") as src_file:
            src_code = src_file.read()
        o_auto_AXI_verilog = auto_bus_verilog(src_code)
        o_auto_AXI_verilog.UI_set()
        self.addr_width = o_auto_AXI_verilog.set_parameter[0]
        self.data_width = o_auto_AXI_verilog.set_parameter[1]
        arbitrator_inst = ""
        arbitrator_inst += o_auto_AXI_verilog.gen_instance_parameter_code()
        arbitrator_inst+= self.gen_axi_arbitrator_one_master_bus()
        for j in range(0,len(self.modules)):
            arbitrator_inst+= self.gen_axi_arbitrator_one_slave_bus(str(j))
        arbitrator_inst = arbitrator_inst[0:-2]+");\n"
        return arbitrator_inst

    def gen_axi_arbitrator_one_slave_bus(self, index):#generate one slave port instance of arbitrator
        one_slave_inst_code = ""
        one_slave_inst_code+=(".slave_%s_AXI_AWREADY( slave_%s_AXI_AWREADY ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_WREADY( slave_%s_AXI_WREADY ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_BRESP( slave_%s_AXI_BRESP ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_BVALID( slave_%s_AXI_BVALID ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_ARREADY( slave_%s_AXI_ARREADY ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_RDATA( slave_%s_AXI_RDATA ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_RRESP( slave_%s_AXI_RRESP ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_RVALID( slave_%s_AXI_RVALID ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_AWADDR( slave_%s_AXI_AWADDR ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_AWPROT( slave_%s_AXI_AWPROT ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_AWVALID( slave_%s_AXI_AWVALID ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_WDATA( slave_%s_AXI_WDATA ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_WSTRB( slave_%s_AXI_WSTRB ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_WVALID( slave_%s_AXI_WVALID ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_BREADY( slave_%s_AXI_BREADY ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_ARADDR( slave_%s_AXI_ARADDR ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_ARPROT( slave_%s_AXI_ARPROT ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_ARVALID( slave_%s_AXI_ARVALID ),\n" %(index,index))
        one_slave_inst_code+=(".slave_%s_AXI_RREADY( slave_%s_AXI_RREADY ),\n" %(index,index))
        return one_slave_inst_code

    def gen_axi_arbitrator_one_master_bus(self):
        arbitrator_master_port_inst_code = ""
        arbitrator_master_port_inst_code+=".AXI_ACLK(AXI_ACLK),\n"
        arbitrator_master_port_inst_code+=".AXI_ARESETN(AXI_ARESETN),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_AWREADY( processor_AXI_AWREADY ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_WREADY( processor_AXI_WREADY ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_BRESP( processor_AXI_BRESP ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_BVALID( processor_AXI_BVALID ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_ARREADY( processor_AXI_ARREADY ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_RDATA( processor_AXI_RDATA ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_RRESP( processor_AXI_RRESP ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_RVALID( processor_AXI_RVALID ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_AWADDR( processor_AXI_AWADDR ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_AWPROT( processor_AXI_AWPROT ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_AWVALID( processor_AXI_AWVALID ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_WDATA( processor_AXI_WDATA ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_WSTRB( processor_AXI_WSTRB ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_WVALID( processor_AXI_WVALID ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_BREADY( processor_AXI_BREADY ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_ARADDR( processor_AXI_ARADDR ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_ARPROT( processor_AXI_ARPROT ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_ARVALID( processor_AXI_ARVALID ),\n"
        arbitrator_master_port_inst_code+=".processor_AXI_RREADY( processor_AXI_RREADY ),\n"
        return arbitrator_master_port_inst_code

    def gen_axi_wire(self):#generate the the wire of all the slave bus
        axi_wire_code = "//bus wire code:\n"
        #master port code
        axi_wire_code += "wire  processor_AXI_AWREADY;\n"
        axi_wire_code += "wire processor_AXI_WREADY;\n"
        axi_wire_code += "wire [1:0] processor_AXI_BRESP;\n"
        axi_wire_code += "wire processor_AXI_BVALID;\n"
        axi_wire_code += "wire processor_AXI_ARREADY;\n"
        axi_wire_code += "wire [%d-1:0] processor_AXI_RDATA;\n" %(self.data_width)
        axi_wire_code += "wire [1:0] processor_AXI_RRESP;\n"
        axi_wire_code += "wire processor_AXI_RVALID;\n"
        axi_wire_code += "wire [%d-1:0] processor_AXI_AWADDR;\n" %(self.addr_width)
        axi_wire_code += "wire [2:0] processor_AXI_AWPROT;\n"
        axi_wire_code += "wire processor_AXI_AWVALID;\n"
        axi_wire_code += "wire [%d-1:0] processor_AXI_WDATA;\n" %(self.data_width)
        axi_wire_code += "wire [%d/8-1:0] processor_AXI_WSTRB;\n" %(self.data_width)
        axi_wire_code += "wire processor_AXI_WVALID;\n"
        axi_wire_code += "wire processor_AXI_BREADY;\n"
        axi_wire_code += "wire [%d-1:0] processor_AXI_ARADDR;\n" %(self.addr_width)
        axi_wire_code += "wire [2:0] processor_AXI_ARPROT;\n"
        axi_wire_code += "wire processor_AXI_ARVALID;\n"
        axi_wire_code += "wire processor_AXI_RREADY;\n"
        #slave port code
        for j in range(0,len(self.modules)):#total 19 ports
            axi_wire_code += "wire  slave_%s_AXI_AWREADY;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_WREADY;\n" %(str(j))
            axi_wire_code += "wire [1:0] slave_%s_AXI_BRESP;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_BVALID;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_ARREADY;\n" %(str(j))
            axi_wire_code += "wire [%d-1:0] slave_%s_AXI_RDATA;\n" %(self.data_width,str(j))
            axi_wire_code += "wire [1:0] slave_%s_AXI_RRESP;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_RVALID;\n" %(str(j))
            axi_wire_code += "wire [%d-1:0] slave_%s_AXI_AWADDR;\n" %(self.addr_width,str(j))
            axi_wire_code += "wire [2:0] slave_%s_AXI_AWPROT;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_AWVALID;\n" %(str(j))
            axi_wire_code += "wire [%d-1:0] slave_%s_AXI_WDATA;\n" %(self.data_width,str(j))
            axi_wire_code += "wire [%d/8-1:0] slave_%s_AXI_WSTRB;\n" %(self.data_width,str(j))
            axi_wire_code += "wire slave_%s_AXI_WVALID;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_BREADY;\n" %(str(j))
            axi_wire_code += "wire [%d-1:0] slave_%s_AXI_ARADDR;\n" %(self.addr_width,str(j))
            axi_wire_code += "wire [2:0] slave_%s_AXI_ARPROT;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_ARVALID;\n" %(str(j))
            axi_wire_code += "wire slave_%s_AXI_RREADY;\n" %(str(j))
        logger.debug("axi wire code:\n"+axi_wire_code)
        return axi_wire_code
    def gen_master_inst(self):
        master_inst_code = '''EMIFA_reg_axi
#(.ADDR_WIDTH(%d),
.DATA_WIDTH(%d))
EMIFA_reg_axi_i(
.AXI_ACLK( AXI_ACLK ),
.AXI_ARESETN( AXI_ARESETN ),
.AXI_AWREADY( processor_AXI_AWREADY ),
.AXI_WREADY( processor_AXI_WREADY ),
.AXI_BRESP( processor_AXI_BRESP ),
.AXI_BVALID( processor_AXI_BVALID ),
.AXI_ARREADY( processor_AXI_ARREADY ),
.AXI_RDATA( processor_AXI_RDATA ),
.AXI_RRESP( processor_AXI_RRESP ),
.AXI_RVALID( processor_AXI_RVALID ),
.i_EMIFA_addr( i_EMIFA_addr ),
.i_EMIFA_data_in( i_EMIFA_data_in ),
.i_EMIFA_ce_n( i_EMIFA_ce_n ),
.i_EMIFA_we_n( i_EMIFA_we_n ),
.i_EMIFA_re_n( i_EMIFA_re_n ),
.i_EMIFA_oe_n( i_EMIFA_oe_n ),
.AXI_AWADDR( processor_AXI_AWADDR ),
.AXI_AWPROT( processor_AXI_AWPROT ),
.AXI_AWVALID( processor_AXI_AWVALID ),
.AXI_WDATA( processor_AXI_WDATA ),
.AXI_WSTRB( processor_AXI_WSTRB ),
.AXI_WVALID( processor_AXI_WVALID ),
.AXI_BREADY( processor_AXI_BREADY ),
.AXI_ARADDR( processor_AXI_ARADDR ),
.AXI_ARPROT( processor_AXI_ARPROT ),
.AXI_ARVALID( processor_AXI_ARVALID ),
.AXI_RREADY( processor_AXI_RREADY ),
.o_EMIFA_data_out( o_EMIFA_data_out ),
.o_EMIFA_rdy( o_EMIFA_rdy ));
''' %(self.addr_width,self.data_width)
        logger.debug(master_inst_code)
        return master_inst_code
    def gen_master_port_code(self):#wei wan cheng??????????????????????????????
        master_port_code = '''input [%s-1:0] i_EMIFA_addr,
	input [%s-1:0] i_EMIFA_data_in,
	output wire [%s-1:0] o_EMIFA_data_out,
	input i_EMIFA_ce_n,
	input i_EMIFA_we_n,
	input i_EMIFA_re_n,
	input i_EMIFA_oe_n,
	output wire o_EMIFA_rdy);\n\n''' %(self.addr_width,self.data_width,self.data_width)
        return master_port_code

    def UI_set_connection(self):#?????????????
        print("tell me all the master:")
        for i in range(0,len(self.modules)):
            print("%d: %s" %(i, self.modules[i].module_name))
        uset_input = input()
        import re
        index_module_name = re.findall(r"\d+",uset_input)#return a list of Index of extern port
        for j in range(0,len(index_module_name)):#get the external port name
            index_module_name[j] = int(index_module_name[j])
            self.master_module.append(self.modules[index_module_name[j]].module_name)

    def gen_connection_tree(self,connect):
        '''cnct = [master_module_name,slave_module_names],
         "slave_module_names" can be a single string, or a list of slave module names,
         the function return a list of
         '''
        if len(connect[1])>1:
            tmp = connect[1]
            connect[1] = "arbitrator_%s" %connect[0]
        self.arbitrators.append()
def UI_set_IP_info(o_auto_AXI_verilog):
    """set the infomation of axi module"""
    IP_info = {}
    o_auto_AXI_verilog.UI_set()
    IP_info["module_name"] = o_auto_AXI_verilog.module_name
    IP_info["output_port"] = o_auto_AXI_verilog.output_port
    IP_info["input_port"] = o_auto_AXI_verilog.input_port
    IP_info["parameter"] = o_auto_AXI_verilog.parameter
    IP_info["set_parameter"] = o_auto_AXI_verilog.set_parameter
    IP_info["output_port_extern"] = o_auto_AXI_verilog.output_port_extern
    IP_info["input_port_extern"] = o_auto_AXI_verilog.input_port_extern
    IP_info["output_port_internal"] = o_auto_AXI_verilog.output_port_internal
    IP_info["input_port_internal"] = o_auto_AXI_verilog.input_port_internal

    for i in range(0,len(o_auto_AXI_verilog.input_port)):
            print("%d: %s" %(i, o_auto_AXI_verilog.input_port[i]))
    print('choose the "clock" port')
    index = input()
    if index=="":
        IP_info["clock"] = ""
    else:
        IP_info["clock"] = o_auto_AXI_verilog.input_port[int(index)]
    print('choose the "rst/rst_n" port')
    index = input()
    if index=="":
        IP_info["rst/rst_n"] = ""
    else:
        IP_info["rst/rst_n"] = o_auto_AXI_verilog.input_port[int(index)]
    return IP_info

