# auto_bus
This tool helps engineers to generate bus (AXI/Avalon/Wishbone in Verilog) automatically.
1. Change a normal module's port into standard bus, eg. AXI/Avalon/Wishbone.
2. Generate instance automatically.
3. Generate top level logic automatically.
4. Generate arbitrator automatically.

Now, it can do these things:
1. Generate AXI bus for a module(Verilog).
2. Generate top level logic, connect several modules(AXI) together.
3. Generate arbitrator of several modules(AXI). 
4. Generate instance.

You can see the reference examples first whose name prefixed by "example".
1.  example_gen_axi.py (generate axi bus)
2. example_gen_inst.py (generate instance)
3. example_test.py (generate top level logic with AXI)
