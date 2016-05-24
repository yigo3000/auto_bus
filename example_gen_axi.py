from auto_AXI_generate_bus import *
import logging
import sys
#import crash_on_ipy
if __name__ == "__main__":
    data = None
    if (len(sys.argv) > 1):
        print("reading source file")
        with open(sys.argv[1],"r",encoding="utf-8") as src_file:
            data = src_file.read()
    if(data != None):
        my_verilog = auto_AXI_generate_bus(data)
        logger=logging.getLogger("auto_AXI_verilog_logger")
        logger.debug("now logging")
        my_verilog.UI_set()
        if(my_verilog.bus_type=="a"):
            my_verilog.gen_axi_lite_slave()
        else:
            pass