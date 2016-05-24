from auto_bus_verilog import *
import logging
import sys
import crash_on_ipy
if __name__ == "__main__":
    data = None
    if (len(sys.argv) > 1):
        print("reading source file")
        data = readFile(sys.argv[1])
    if(data != None):
        
        my_verilog = auto_bus_verilog(data)
        logger=logging.getLogger("auto_bus_verilog_logger")
        logger.debug("now logging")
        print(my_verilog.gen_instance())