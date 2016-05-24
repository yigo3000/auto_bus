`timescale 1ns/1ps
module axi_lite_slave
(
input  AXI_ACLK,
input  AXI_ARESETN,
input  wire [ADDR_WIDTH - 1:0]  AXI_AWADDR,
input 	wire [2:0]                      AXI_AWPROT,
input     wire                          AXI_AWVALID,
output                                  AXI_AWREADY,
input  wire [DATA_WIDTH-1:0]     AXI_WDATA,
input  wire [DATA_WIDTH/8-1:0]   AXI_WSTRB,
input    wire                           AXI_WVALID,
output                                  AXI_WREADY,
output  [1:0]                           AXI_BRESP,
output                                  AXI_BVALID,
input    wire                           AXI_BREADY,
input wire [ADDR_WIDTH - 1:0]  AXI_ARADDR,
input [2:0]	                            AXI_ARPROT,
input                                   AXI_ARVALID,
output                                  AXI_ARREADY,
output  [DATA_WIDTH-1:0]         AXI_RDATA,
output  [1:0]                           AXI_RRESP,
output                                   AXI_RVALID,
input                                    AXI_RREADY
);
/////////////////////////////////////////////////////////////
//custom define parameters.
    /* jhi_auto */localparam ADDR_WIDTH = 32;
    /* jhi_auto */localparam DATA_WIDTH = 32;
    /* jhi_auto */localparam NUM_OF_TOTAL_WORDS = 8;
    /* jhi_auto */localparam NUM_OF_WRITE_READ_WORDS = 5;
////////////////////////////////////////////////////////////////////////////
// function called clogb2 that returns an integer which has the
// value of the ceiling of the log base 2.
function integer clogb2 (input integer bd);
integer bit_depth;
begin
  bit_depth = bd;
  for(clogb2=0; bit_depth>0; clogb2=clogb2+1)
    bit_depth = bit_depth >> 1;
  end
endfunction
////////////////////////////////////////////////////////////////////////////
// local parameter for addressing 32 bit / 64 bit C_AXI_DATA_WIDTH
// ADDR_LSB is used for addressing 32/64 bit registers/memories
// ADDR_LSB = 2 for 32 bits (n downto 2)
// ADDR_LSB = 3 for 64 bits (n downto 3)
////////////////////////////////////////////////////////////////////////////
// Width ofaxi_bus.AXI data bus. The slave accepts write data and issues read data
localparam integer ADDR_LSB = clogb2(DATA_WIDTH/8)-1;
localparam integer ADDR_MSB = clogb2(NUM_OF_TOTAL_WORDS);
localparam integer NUM_OF_READ_ONLY_WORDS = NUM_OF_TOTAL_WORDS-NUM_OF_WRITE_READ_WORDS;
////////////////////////////////////////////////////////////////////////////
// AXI4 Lite internal signals

////////////////////////////////////////////////////////////////////////////
// read response
reg [1 :0]                   axi_rresp;
////////////////////////////////////////////////////////////////////////////
// write response
reg [1 :0]                   axi_bresp;
////////////////////////////////////////////////////////////////////////////
// write address acceptance
reg                          axi_awready;
////////////////////////////////////////////////////////////////////////////
// write data acceptance
reg                          axi_wready;
////////////////////////////////////////////////////////////////////////////
// write response valid
reg                          axi_bvalid;
////////////////////////////////////////////////////////////////////////////
// read data valid
reg                          axi_rvalid;
////////////////////////////////////////////////////////////////////////////
// write address
reg [ADDR_MSB-1:0] axi_awaddr;
////////////////////////////////////////////////////////////////////////////
// read address valid
reg [ADDR_MSB-1:0] axi_araddr;
////////////////////////////////////////////////////////////////////////////
// read data
reg [DATA_WIDTH-1:0] axi_rdata;
////////////////////////////////////////////////////////////////////////////
// read address acceptance
reg                          axi_arready;

////////////////////////////////////////////////////////////////////////////
// Example-specific design signals


////////////////////////////////////////////////////////////////////////////
// Signals for user logic chip select generation

////////////////////////////////////////////////////////////////////////////
// Signals for user logic register space example
// Four slave register

////////////////////////////////////////////////////////////////////////////
// Slave register 0

reg [DATA_WIDTH-1:0] slv_reg[0:NUM_OF_TOTAL_WORDS-1];//slg_reg[0:NUM_OF_WRITE_READ_WORDS-1]: can be write and read, used on some of the input port; slg_reg[NUM_OF_WRITE_READ_WORDS:NUM_OF_TOTAL_WORDS-1]: read only, for some of the output port.
wire [DATA_WIDTH-1:0] slv_reg_read_only[0:NUM_OF_READ_ONLY_WORDS-1];
////////////////////////////////////////////////////////////////////////////
// Slave register read enable
wire                            slv_reg_rden;
////////////////////////////////////////////////////////////////////////////
// Slave register write enable
wire                            slv_reg_wren;
////////////////////////////////////////////////////////////////////////////
// register read data
reg [DATA_WIDTH-1:0]    reg_data_out;

integer                         byte_index;

////////////////////////////////////////////////////////////////////////////
//I/O Connections assignments

////////////////////////////////////////////////////////////////////////////
//Write Address Ready (AWREADY)
assign AXI_AWREADY = axi_awready;

////////////////////////////////////////////////////////////////////////////
//Write Data Ready(WREADY)
assign AXI_WREADY  = axi_wready;

////////////////////////////////////////////////////////////////////////////
//Write Response (BResp)and response valid (BVALID)
assign AXI_BRESP  = axi_bresp;
assign AXI_BVALID = axi_bvalid;

////////////////////////////////////////////////////////////////////////////
//Read Address Ready(AREADY)
assign AXI_ARREADY = axi_arready;

////////////////////////////////////////////////////////////////////////////
//Read and Read Data (RDATA), Read Valid (RVALID) and Response (RRESP)
assign AXI_RDATA  = axi_rdata;
assign AXI_RVALID = axi_rvalid;
assign AXI_RRESP  = axi_rresp;


////////////////////////////////////////////////////////////////////////////
// Implement axi_awready generation
//
//  axi_awready is asserted for oneaxi_bus.AXI_ACLK clock cycle when both
// AXI_AWVALID andaxi_bus.AXI_WVALID are asserted. axi_awready is
//  de-asserted when reset is low.

  always @( posedge AXI_ACLK )
  begin
    if (AXI_ARESETN == 1'b0 )
      begin
        axi_awready <= 1'b0;
      end
    else
      begin
        if (~axi_awready && AXI_AWVALID && AXI_WVALID)
          begin
            ////////////////////////////////////////////////////////////////////////////
            // slave is ready to accept write address when
            // there is a valid write address and write data
            // on the write address and data bus. This design
            // expects no outstanding transactions.
            axi_awready <= 1'b1;
          end
        else
          begin
            axi_awready <= 1'b0;
          end
      end
  end

////////////////////////////////////////////////////////////////////////////
// Implement axi_awaddr latching
//
//  This process is used to latch the address when both
// AXI_AWVALID andaxi_bus.AXI_WVALID are valid.

  always @( posedge AXI_ACLK )
  begin
    if (AXI_ARESETN == 1'b0 )
      begin
        axi_awaddr <= 0;
      end
    else
      begin
        if (~axi_awready && AXI_AWVALID && AXI_WVALID)
          begin
            ////////////////////////////////////////////////////////////////////////////
            // address latching
            axi_awaddr <= AXI_AWADDR;
          end
      end
  end

////////////////////////////////////////////////////////////////////////////
// Implement axi_wready generation
//
//  axi_wready is asserted for oneaxi_bus.AXI_ACLK clock cycle when both
// AXI_AWVALID andaxi_bus.AXI_WVALID are asserted. axi_wready is
//  de-asserted when reset is low.

  always @( posedge AXI_ACLK )
  begin
    if (AXI_ARESETN == 1'b0 )
      begin
        axi_wready <= 1'b0;
      end
    else
      begin
        if (~axi_wready && AXI_WVALID && AXI_AWVALID)
          begin
            ////////////////////////////////////////////////////////////////////////////
            // slave is ready to accept write data when
            // there is a valid write address and write data
            // on the write address and data bus. This design
            // expects no outstanding transactions.
            axi_wready <= 1'b1;
          end
        else
          begin
            axi_wready <= 1'b0;
          end
      end
  end

////////////////////////////////////////////////////////////////////////////
// Implement memory mapped register select and write logic generation
//
// The write data is accepted and written to memory mapped
// registers (slv_reg0, slv_reg1, slv_reg2, slv_reg3) when axi_wready,
//axi_bus.AXI_WVALID, axi_wready andaxi_bus.AXI_WVALID are asserted. Write strobes are used to
// select byte enables of slave registers while writing.
// These registers are cleared when reset (active low) is applied.
//
// Slave register write enable is asserted when valid address and data are available
// and the slave is ready to accept the write address and write data.
assign slv_reg_wren = axi_wready && AXI_WVALID && axi_awready && AXI_AWVALID;
genvar h;//i: num of words. j:num of read only words.
generate for(h=0; h<NUM_OF_WRITE_READ_WORDS; h=h+1) begin: read_write_words
	always @( posedge AXI_ACLK ) begin
			if ( AXI_ARESETN == 1'b0 ) slv_reg[h]<=0;
			else begin
				if (slv_reg_wren) begin
					if(axi_awaddr[ADDR_MSB-1:ADDR_LSB] == h) begin
						for ( byte_index = 0; byte_index <= (DATA_WIDTH/8)-1; byte_index = byte_index+1 )
							if (AXI_WSTRB[byte_index] == 1 ) slv_reg[h][(byte_index*8) +: 8] <= AXI_WDATA[(byte_index*8) +: 8];
					end
					else begin
                        slv_reg[h] <= slv_reg[h];
                    end
				end
			end
    end
end
endgenerate
genvar i;//i: num of words. j:num of read only words.
generate for(i=0; i<NUM_OF_READ_ONLY_WORDS; i=i+1) begin: read_only_words
	always @( posedge AXI_ACLK ) begin
			if ( AXI_ARESETN == 1'b0 ) slv_reg[i+NUM_OF_WRITE_READ_WORDS]<=0;
			else slv_reg[i+NUM_OF_WRITE_READ_WORDS] <= slv_reg_read_only[i];
    end
end
endgenerate
////////////////////////////////////////////////////////////////////////////
// Implement write response logic generation
//
//  The write response and response valid signals are asserted by the slave
//  when axi_wready,axi_bus.AXI_WVALID, axi_wready andaxi_bus.AXI_WVALID are asserted.
//  This marks the acceptance of address and indicates the status of
//  write transaction.

  always @( posedge AXI_ACLK )
  begin
    if ( AXI_ARESETN == 1'b0 )
      begin
        axi_bvalid  <= 0;
        axi_bresp   <= 2'b0;
      end
    else
      begin
        if (axi_awready && AXI_AWVALID && ~axi_bvalid && axi_wready && AXI_WVALID)
          begin
            // indicates a valid write response is available
            axi_bvalid <= 1'b1;
            axi_bresp  <= 2'b0; // 'OKAY' response
          end                   // work error responses in future
        else
          begin
            if ( AXI_BREADY && axi_bvalid)
              //check if bready is asserted while bvalid is high)
              //(there is a possibility that bready is always asserted high)
              begin
                axi_bvalid <= 1'b0;
              end
          end
      end
  end


////////////////////////////////////////////////////////////////////////////
// Implement axi_arready generation
//
//  axi_arready is asserted for oneaxi_bus.AXI_ACLK clock cycle when
// AXI_ARVALID is asserted. axi_awready is
//  de-asserted when reset (active low) is asserted.
//  The read address is also latched whenaxi_bus.AXI_ARVALID is
//  asserted. axi_araddr is reset to zero on reset assertion.

  always @( posedge AXI_ACLK )
  begin
    if ( AXI_ARESETN == 1'b0 )
      begin
        axi_arready <= 1'b0;
        axi_araddr  <= {ADDR_MSB{1'b0}};
      end
    else
      begin
        if (~axi_arready && AXI_ARVALID)
          begin
            // indicates that the slave has acceped the valid read address
            axi_arready <= 1'b1;
            axi_araddr  <= AXI_ARADDR;
          end
        else
          begin
            axi_arready <= 1'b0;
          end
      end
  end

////////////////////////////////////////////////////////////////////////////
// Implement memory mapped register select and read logic generation
//
//  axi_rvalid is asserted for oneaxi_bus.AXI_ACLK clock cycle when both
// AXI_ARVALID and axi_arready are asserted. The slave registers
//  data are available on the axi_rdata bus at this instance. The
//  assertion of axi_rvalid marks the validity of read data on the
//  bus and axi_rresp indicates the status of read transaction.axi_rvalid
//  is deasserted on reset (active low). axi_rresp and axi_rdata are
//  cleared to zero on reset (active low).

  always @( posedge AXI_ACLK )
  begin
    if (AXI_ARESETN == 1'b0 )
      begin
        axi_rvalid <= 0;
        axi_rresp  <= 0;
      end
    else
      begin
        if (axi_arready && AXI_ARVALID && ~axi_rvalid)
          begin
            // Valid read data is available at the read data bus
            axi_rvalid <= 1'b1;
            axi_rresp  <= 2'b0; // 'OKAY' response
          end
        else if (axi_rvalid && AXI_RREADY)
          begin
            // Read data is accepted by the master
            axi_rvalid <= 1'b0;
          end
      end
  end


////////////////////////////////////////////////////////////////////////////
// Slave register read enable is asserted when valid address is available
// and the slave is ready to accept the read address.
  assign slv_reg_rden = axi_arready & AXI_ARVALID & ~axi_rvalid;
integer j;
  always @(*)
  begin
    if ( AXI_ARESETN == 1'b0 )
      begin
        reg_data_out <= {DATA_WIDTH{1'b0}};
      end
    else
      begin
        // Read address mux
			for(j=0; j<NUM_OF_TOTAL_WORDS; j=j+1) begin
				if(axi_araddr[ADDR_MSB-1:ADDR_LSB] == j) reg_data_out <= slv_reg[j];
			end
      end
  end

  always @( posedge AXI_ACLK )
  begin
    if ( AXI_ARESETN == 1'b0 )
      begin
        axi_rdata  <= 0;
      end
    else
      begin
        ////////////////////////////////////////////////////////////////////////////
        // When there is a valid read address (S_AXI_ARVALID) with
        // acceptance of read address by the slave (axi_arready),
        // output the read dada
        if (axi_arready && AXI_ARVALID && ~axi_rvalid)
          begin
            axi_rdata <= reg_data_out;     // register read data
          end
      end
  end

//add your custom module here. Set the read_only register to the output port.
/* jhi_auto */
endmodule