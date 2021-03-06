SPI Master driver
=================

Overview
--------

The ESP32 has four SPI peripheral devices, called SPI0, SPI1, HSPI and VSPI. SPI0 is entirely dedicated to
the flash cache the ESP32 uses to map the SPI flash device it is connected to into memory. SPI1 is
connected to the same hardware lines as SPI0 and is used to write to the flash chip. HSPI and VSPI
are free to use. SPI1, HSPI and VSPI all have three chip select lines, allowing them to drive up to
three SPI devices each as a master. The SPI peripherals also can be used in slave mode, driven from 
another SPI master.

The spi_master driver
^^^^^^^^^^^^^^^^^^^^^

The spi_master driver allows easy communicating with SPI slave devices, even in a multithreaded environment.
It fully transparently handles DMA transfers to read and write data and automatically takes care of 
multiplexing between different SPI slaves on the same master

Terminology
^^^^^^^^^^^

The spi_master driver uses the following terms:

* Host: The SPI peripheral inside the ESP32 initiating the SPI transmissions. One of SPI, HSPI or VSPI. (For 
  now, only HSPI or VSPI are actually supported in the driver; it will support all 3 peripherals 
  somewhere in the future.)
* Bus: The SPI bus, common to all SPI devices connected to one host. In general the bus consists of the
  miso, mosi, sclk and optionally quadwp and quadhd signals. The SPI slaves are connected to these 
  signals in parallel.

  - miso - Also known as q, this is the input of the serial stream into the ESP32

  - mosi - Also known as d, this is the output of the serial stream from the ESP32

  - sclk - Clock signal. Each data bit is clocked out or in on the positive or negative edge of this signal

  - quadwp - Write Protect signal. Only used for 4-bit (qio/qout) transactions.

  - quadhd - Hold signal. Only used for 4-bit (qio/qout) transactions.

* Device: A SPI slave. Each SPI slave has its own chip select (CS) line, which is made active when
  a transmission to/from the SPI slave occurs.
* Transaction: One instance of CS going active, data transfer from and/or to a device happening, and
  CS going inactive again. Transactions are atomic, as in they will never be interrupted by another
  transaction.


SPI transactions
^^^^^^^^^^^^^^^^

A transaction on the SPI bus consists of five phases, any of which may be skipped:

* The command phase. In this phase, a command (0-16 bit) is clocked out.
* The address phase. In this phase, an address (0-64 bit) is clocked out.
* The read phase. The slave sends data to the master.
* The write phase. The master sends data to the slave.

In full duplex, the read and write phases are combined, causing the SPI host to read and
write data simultaneously.

The command and address phase are optional in that not every SPI device will need to be sent a command
and/or address. Tis is reflected in the device configuration: when the ``command_bits`` or ``data_bits``
fields are set to zero, no command or address phase is done.

Something similar is true for the read and write phase: not every transaction needs both data to be written
as well as data to be read. When ``rx_buffer`` is NULL (and SPI_USE_RXDATA) is not set) the read phase 
is skipped. When ``tx_buffer`` is NULL (and SPI_USE_TXDATA) is not set) the write phase is skipped.

Using the spi_master driver
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Initialize a SPI bus by calling ``spi_bus_initialize``. Make sure to set the correct IO pins in
  the ``bus_config`` struct. Take care to set signals that are not needed to -1.

- Tell the driver about a SPI slave device conencted to the bus by calling spi_bus_add_device. 
  Make sure to configure any timing requirements the device has in the ``dev_config`` structure.
  You should now have a handle for the device, to be used when sending it a transaction.

- To interact with the device, fill one or more spi_transaction_t structure with any transaction 
  parameters you need. Either queue all transactions by calling ``spi_device_queue_trans``, later
  quering the result using ``spi_device_get_trans_result``, or handle all requests synchroneously
  by feeding them into ``spi_device_transmit``.

- Optional: to unload the driver for a device, call ``spi_bus_remove_device`` with the device
  handle as an argument

- Optional: to remove the driver for a bus, make sure no more drivers are attached and call 
  ``spi_bus_free``.


Transaction data
^^^^^^^^^^^^^^^^

Normally, data to be transferred to or from a device will be read from or written to a chunk of memory
indicated by the ``rx_buffer`` and ``tx_buffer`` members of the transaction structure. The SPI driver
may decide to use DMA for transfers, so these buffers should be allocated in DMA-capable memory using 
``pvPortMallocCaps(size, MALLOC_CAP_DMA)``.

Sometimes, the amount of data is very small making it less than optimal allocating a separate buffer
for it. If the data to be transferred is 32 bits or less, it can be stored in the transaction struct
itself. For transmitted data, use the ``tx_data`` member for this and set the ``SPI_USE_TXDATA`` flag
on the transmission. For received data, use ``rx_data`` and set ``SPI_USE_RXDATA``. In both cases, do
not touch the ``tx_buffer`` or ``rx_buffer`` members, because they use the same memory locations
as ``tx_data`` and ``rx_data``.

Application Example
-------------------
 
Display graphics on the ILI9341-based 320x240 LCD: `examples/peripherals/spi_master <https://github.com/espressif/esp-idf/tree/master/examples/peripherals/spi_master>`_.

API Reference
-------------

Header Files
^^^^^^^^^^^^

  * `driver/include/driver/spi_master.h <https://github.com/espressif/esp-idf/blob/master/components/driver/include/driver/spi_master.h>`_

Macros
^^^^^^

.. doxygendefine:: SPI_DEVICE_TXBIT_LSBFIRST
.. doxygendefine:: SPI_DEVICE_RXBIT_LSBFIRST
.. doxygendefine:: SPI_DEVICE_BIT_LSBFIRST
.. doxygendefine:: SPI_DEVICE_3WIRE
.. doxygendefine:: SPI_DEVICE_POSITIVE_CS
.. doxygendefine:: SPI_DEVICE_HALFDUPLEX
.. doxygendefine:: SPI_DEVICE_CLK_AS_CS

.. doxygendefine:: SPI_TRANS_MODE_DIO
.. doxygendefine:: SPI_TRANS_MODE_QIO
.. doxygendefine:: SPI_TRANS_MODE_DIOQIO_ADDR
.. doxygendefine:: SPI_TRANS_USE_RXDATA
.. doxygendefine:: SPI_TRANS_USE_TXDATA

Type Definitions
^^^^^^^^^^^^^^^^

.. doxygentypedef:: spi_device_handle_t

Enumerations
^^^^^^^^^^^^

.. doxygenenum:: spi_host_device_t

Structures
^^^^^^^^^^

.. doxygenstruct:: spi_transaction_t
  :members:

.. doxygenstruct:: spi_bus_config_t
  :members:

.. doxygenstruct:: spi_device_interface_config_t
  :members:



Functions
---------

.. doxygenfunction:: spi_bus_initialize
.. doxygenfunction:: spi_bus_free
.. doxygenfunction:: spi_bus_add_device
.. doxygenfunction:: spi_bus_remove_device
.. doxygenfunction:: spi_device_queue_trans
.. doxygenfunction:: spi_device_get_trans_result
.. doxygenfunction:: spi_device_transmit

