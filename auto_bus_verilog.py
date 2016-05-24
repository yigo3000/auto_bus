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

#This code can't do:
#1. not support parameter in the logic region, only support in the "module XXX #(...)"
#2. not support hex number
#3. do not support '`define' in the port region
#4. only support declare the port width in the port region, e.g., module XXX ( input wire [2:0] data, ...);
#5. "clk" and "reset" must be choose as "external port", both in auto_bus_generate_bus and generate_top
#enable log

import logging
logger=logging.getLogger('auto_bus_verilog_logger')
handler=logging.FileHandler("auto_bus_verilog_logger.txt",encoding ='utf-8' )

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')#set the format
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
def readFile(path):
    import os
    if (not os.path.isfile(path)):
        return None
    data = None
    with open(path) as file:
        data = file.read()
    return data
def choose_in_list(input_list):
    output_list = []
    import re
    for i in range(0,len(input_list)):
            print("%d: %s" %(i, input_list[i]))
    user_input = input()
    index_input_list = re.findall(r"\d+",user_input)
    for j in range(0,len(index_input_list)):
        index_input_list[j] = int(index_input_list[j])
        output_list.append(input_list[index_input_list[j]])
    return output_list

class auto_bus_verilog:
    '''get Verilog module from source sode.'''
    def __init__(self, src):
        #define the member
        self.module_name = []
        self.output_port = []
        self.input_port = []
        self.parameter = []#parameter[][0]:param name; parameter[][1] default value
        self.set_parameter = []
        self.output_port_extern = []# e.g.: [('[15:0]','port name'),(...),(...),...]
        self.input_port_extern = []
        self.output_port_internal = []
        self.input_port_internal = []
        indent = "\t"
        if (not src):
            print('source is NULL!')
            return None
        import re
        # try to remove comments, but no escape character or quotation marks are considered.
        src = re.sub(r"(\/\*(\s|.)*?\*\/)|(\/\/.*)", "", src)
        #results = []
        macro = []
        for module_match in re.finditer(r"\bmodule\s+.*?\s+endmodule\b", src, re.S):# support multiple modules. Do it in everyone.
            module_pattern = re.compile(r'''module\s+
            (\w+)\s*                            #group(1) module name
            (?P<para>\#\s*\([^\(\)]*\)\s*)?         #group(2) parameter region
            \((?P<sig>[^\(\)]*\))\s*           #group(3) signal region
            ;(.*)                   #group(3) logic description part the module'''
            ,re.S|re.X)
            text = module_pattern.match(module_match.group())
            if (not text):
                continue
            #result = [None, [], []]  # name, parameters, signals
            self.module_name = text.group(1)#group(1):give the 1st word in the match. group(0): give the whole match
            print("module", self.module_name)
            # support macro nesting, but do not check the correctness
            #macro_pattern = re.compile(r"(`ifn?def\s*\w+|`endif)\s*")
            output_port_pattern = re.compile(r"((output|inout)\s+(reg|wire)?\s*(?P<width>\[[^:]+:[^:]+\])?)?\s*(?P<name>\w+)\s*(\=[^,\)]*)?[,\)]\s*")
            input_port_pattern =  re.compile(r"((input)\s+(reg|wire)?\s*(?P<width>\[[^:]+:[^:]+\])?)?\s*(?P<name>\w+)\s*(\=[^,\)]*)?[,\)]\s*")
            #param_group_pattern = re.compile(r"self.parameter\s+([^;]*;)")
            param_pattern = re.compile(r"(\w+)\s*=\s*(.*)\s*[,]?\s*")#group(1):parameter name; group(2):parameter value
            # process signals
            signals_define = text.group('sig').strip()
            #print(signals_define)
            signal_index = 0;#begin of region searched. when find one, signal_index move to the position to the end of the fit.
            last_signal = None
            while (signal_index != len(signals_define)):
                signal_match = output_port_pattern.match(signals_define, pos=signal_index)
                if (signal_match):
                    self.output_port.append((signal_match.group("width"),signal_match.group("name")))#find one, put it to the append. {0}:put the string in format in here
                    print("output signal", self.output_port[-1])#print the last self.output_port
                    signal_index = signal_match.end()
                else:
                    signal_match = input_port_pattern.match(signals_define, pos=signal_index)
                    if (signal_match):
                        self.input_port.append((signal_match.group("width"),signal_match.group("name")))#
                        print("input signal", self.input_port[-1])#print the last self.output_port
                        signal_index = signal_match.end()
                    else:
                        self.input_port.append("!ERROR!")
                        print("signal", self.input_port[-1])
                        break
            # process parameters
            params_define = text.group('para')#parameter define text, eg:"#(parameter SSSS=8)"
            #print("Parameter code: %s" %params_define)
            if params_define==None :
                print("No parameter found.")
            else:
                params_define.strip()
                param_index = 0
                last_param = None
                while (param_index != len(params_define)):
                    param_match = param_pattern.search(params_define, pos=param_index)
                    if (param_match):
                        self.parameter.append((param_match.group(1), param_match.group(2)))
                        print("parameter %s = %s" %(self.parameter[-1][0],self.parameter[-1][1]))
                        param_index = param_match.end()
                    else:
                        break
                # if (last_param):
                    # result[1][last_param-1] = result[1][last_param-1].rstrip(",")
    def UI_set(self):
        #set parameter
        for i in range(0, len(self.parameter)):
            print("Set the parameter(decimal): %s" %self.parameter[i][0])
            input_set_parameter = input()
            if input_set_parameter == "":
                self.set_parameter.append(int(self.parameter[i][1].rstrip(",")))
            else:
                self.set_parameter.append(int(input_set_parameter))
        #choose the extern port
        #choose the input extern port
        import re
        for i in range(0,len(self.input_port)):
            print("%d: %s" %(i, self.input_port[i]))
        print("Choose the external port.\n Type the number of the port, with blank for multiple select, e.g. '3 4 6':")
        input_extern_port = input()
        index_extern_port = re.findall(r"\d+",input_extern_port)#return a list of Index of extern port
        for j in range(0,len(index_extern_port)):#get the external port name
            index_extern_port[j] = int(index_extern_port[j])
            self.input_port_extern.append(self.input_port[index_extern_port[j]])
        for j in range(0,len(self.input_port)):#get the internal port name
            if (j not in index_extern_port):
                self.input_port_internal.append(self.input_port[j])
        logger.debug("input port extern: ")
        logger.debug(self.input_port_extern)
        logger.debug("input port intern:")
        logger.debug(self.input_port_internal)
        index_extern_port = None
        #choose the output extern port
        for i in range(0,len(self.output_port)):
            print("%d: %s" %(i, self.output_port[i]))
        print("Choose the external port.\n Type the number of the port, with blank for multiple select, e.g. '3 4 6':")
        output_extern_port = input()
        index_extern_port = re.findall(r"\d+\s*",output_extern_port)#return a list of string
        for j in range(0,len(index_extern_port)):#get the external port name
            index_extern_port[j] = int(index_extern_port[j])
            self.output_port_extern.append(self.output_port[index_extern_port[j]])
        for j in range(0,len(self.output_port)):#get the internal port name
            if (j not in index_extern_port):
                self.output_port_internal.append(self.output_port[j])
        logger.debug("output port extern port:")
        logger.debug(self.output_port_extern)
        logger.debug('output port internal:')
        logger.debug(self.output_port_internal)
        logger.debug(self.set_parameter)
    def gen_instance(self):
        self.UI_set()
        self.instance = None
        #generate parameter
        # if self.parameter==[]:
            # self.instance = "%s %s_i (\n" %(self.module_name,self.module_name)
        # else:
            # self.instance = "%s \n#(" %(self.module_name)
            # for i in range(0, len(self.parameter)):
                # self.instance += ".%s(%s),\n" %(self.parameter[i][0],str(self.set_parameter[i]))
            # self.instance = self.instance[0:-2]+(")\n%s_i(\n" %self.module_name)
        self.instance = self.gen_instance_parameter_code()

        #input port
        for i in range (0,len(self.input_port)):
            self.instance += ".%s( %s ),\n" %(self.input_port[i][1],self.input_port[i][1])
        for i in range (0,len(self.output_port)):
            self.instance += ".%s( %s ),\n" %(self.output_port[i][1],self.output_port[i][1])
        self.instance = self.instance[0:-2]+");\n"
        logger.debug(self.instance)
        return self.instance
        
    def gen_instance_parameter_code(self):
        if self.parameter==[]:
            inst_parameter_code = "%s %s_i (\n" %(self.module_name,self.module_name)
        else:
            inst_parameter_code = "%s \n#(" %(self.module_name)
            for i in range(0, len(self.parameter)):
                inst_parameter_code += ".%s(%s),\n" %(self.parameter[i][0],str(self.set_parameter[i]))
            inst_parameter_code = inst_parameter_code[0:-2]+(")\n%s_i(\n" %self.module_name)
        return inst_parameter_code
    def __del__(self):
        logger.debug(self.module_name)
        logger.debug(self.input_port)
        logger.debug(self.output_port)
        logger.debug(self.parameter)
        #logger.debug(self.extern_port)

