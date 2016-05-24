from auto_generate_axi_top import *
import logging
import sys
import crash_on_ipy
# if __name__ == "__main__":
    # data = None
    # if (len(sys.argv) > 1):
        # print("reading source file")
        # data = readFile(sys.argv[1])
    # if(data != None):
        # my_verilog = auto_AXI_generate_bus(data)
        # logger=logging.getLogger("auto_AXI_verilog_logger")
        # logger.debug("now logging")
        # my_verilog.UI_set()
        # if(my_verilog.bus_type=="a"):
            # my_verilog.gen_axi_lite_slave()
        # else:
            # pass
            
        
        # my_verilog = auto_AXI_verilog(data)
        # logger=logging.getLogger("auto_AXI_verilog_logger")
        # logger.debug("now logging")
        # print(my_verilog.gen_instance())
        
# if __name__ == "__main__":
    # data = []
    # if (len(sys.argv) > 1):
        # print("reading source file")
        # temp = ""
        # for i in range(0,len(sys.argv)-1):
            # with open(sys.argv[i+1],"r",encoding = 'utf-8') as temp:
                # data.append(temp.read())
        # my_verilog = generate_top(data)
        # my_verilog.gen_top()
        
if __name__ == "__main__":
    '''
    generate top level logic for AXI
    生成顶层逻辑。包括顶层端口、模块例化、自动生成仲裁、自动连接模块...
    '''
    data = []
    if (len(sys.argv) > 1):
        print("reading source file")
        temp = ""
        for i in range(0,len(sys.argv)-1):
            with open(sys.argv[i+1],"r",encoding = 'utf-8') as temp:
                data.append(temp.read())
        my_verilog = generate_axi_top(data)
        # my_verilog.gen_axi_arbitrator_inst()
        # my_verilog.gen_axi_wire()
        my_verilog.gen_axi_top()