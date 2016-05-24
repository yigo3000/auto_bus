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
from auto_AXI_verilog.auto_AXI_verilog import auto_AXI_verilog

class generate_top():
    def __init__(self,src):
        self.modules = []#build a object for every source file
        for i in range(0,len(src)):
            self.modules.append(auto_AXI_verilog(src[i]))
    def gen_top(self):
        dst_code = ""
        for j in range(0,len(self.modules)):
            dst_code += self.modules[j].gen_instance()
        port_code = self.gen_port()
        dst_code = port_code + dst_code
        with open("top.v","w", encoding = 'utf-8') as dst_file:
            dst_file.writelines(dst_code)
    def gen_port(self):#must be used after use gen_instance() or UI_set()
        port_code ="module top(\n"
        logger.debug("length of self.modules in gen_port")
        logger.debug(len(self.modules))
        for j in range(0,len(self.modules)):
            #generate port
            for i in range(0,len(self.modules[j].input_port_extern)):
                    if self.modules[j].input_port_extern[i][0]==None:
                        port_code += "input %s,\n" %self.modules[j].input_port_extern[i][1]
                    else:
                        port_code += "input %s %s,\n" %(self.modules[j].input_port_extern[i][0],self.modules[j].input_port_extern[i][1])
            for i in range(0,len(self.modules[j].output_port_extern)):
                if self.modules[j].output_port_extern[i][0]==None:
                    port_code += "output wire %s,\n" %self.modules[j].output_port_extern[i][1]
                else:
                    port_code += "output wire %s %s,\n" %(self.modules[j].output_port_extern[i][0],self.modules[j].output_port_extern[i][1])
        port_code = port_code[0:-2]+");\n"
        logger.debug(port_code)
        return port_code

