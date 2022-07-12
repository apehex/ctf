# Factory

> **Our infrastructure is under attack! The HMI interface went offline and we
> lost control of some critical PLCs in our ICS system. Moments after the attack
> started we managed to identify the target but did not have time to respond.
> The water storage facility's high/low sensors are corrupted thus setting the
> PLC into a halt state. We need to regain control and empty the water tank
> before it overflows. Our field operative has set a remote connection directly
> with the serial network of the system.**

## Interpreting the diagrams

The goal is to manually empty the tank to prevent an overflow.

The logic ladder diagram further informs us that the levels can be controled
with two valves: the in valve and the out valve.

Emptying the tank means:
1) closing the in-valve
2) opening the out-valve

This is done by sending the appropriate commands to the PLC, over modbus.

## Transmitting commands

### The actual interface

The challenge gives us an IP:
we send the commands over the network to a supervising computer which in turn
relays the message over a serial connection to the PLC.

The supervisor is accessible with `ncat`:

```
ncat 159.65.18.5 32345
Water Storage Facility Interface
1. Get status of system
2. Send modbus command
3. Exit
Select: 2
Modbus command: 520526DBFF00
Modbus command sent to the network!
```

What took me the longest was debunking the confusion between:
1) what I type: ASCII characters
2) the information of the message: hexadecimal values, written in ASCII
3) the actual bytes sent: the encoding of the ASCII characters

Example: typing "52", thinking `0x52` to refer to address 82 of the PLC
1) I type `5` and `2`
2) the information is `0x52` or `82`, ie **1 byte** of meaning
3) **BUT** what is sent over the network is the encoding values of "5" and "2":
  - `0x35` for "5"
  - `0x32` for "2"

In short, when wikipedia says "length: 2 bytes" for the address, it means:
`52` is right `0052` is wrong.
2 bytes of encoded data, 1 byte of meaning.

Through trial and error, I determined that the network interface doesn't expect
the "start", "LRC" nor "end" parts.

IE `:520526DBFF00A9` is a valid frame but the interface wants `520526DBFF00` only.

### The modbus protocol

The commands are encoded with the modbus protocol.

The page from [wikipedia][wikipedia-modbus-url] gives the format of the message
transmitted over the data link.

The data is expect to follow the "ASCII frame format":
- start: 1 byte, the ASCII character `:`
- address: 2 bytes, like `0x3532` for "52"
- function: 2 bytes, like "05"
- data: 2\*n bytes, depending on the function
- LRC: 2 bytes, as in "9A"
- end: 2 bytes, line feed (CR/LF) pair

The "start", "LRC" and "end" parts are actually omitted when talking to the
network interface.

Which actually simplifies matters quite a bit!.... if we knew it from the start (:

## Closing the in-valve

### Sending the close commands

To ensure that the in-valve is closed, whatever the status of the rest of the  system,
we need to activate the `stop-in` actuator.

According to the ladder diagram, this is equivalent to: `cutoff-in AND manual-mode`.

The PLC has the address 82, which is `0x0052 in hexadecimal`.
All the decimal values must be converted to hexadecimal to encode the message.

Activating `cutoff-in`:
- address: decimal 82 = `0x52`
- function: write single coil, decimal 5 = `0x05`
- data:
  - address: decimal 26 = `0x001A`
  - value: decimal 65280 = true = `0xFF00`
- message typed: `5205001AFF00`

Activating `manual-mode`:
- address: `0x52`
- function: `0x05`
- data:
  - address: decimal 9947 = `0x26DB`
  - value: `0xFF00`
- message typed: `520526DBFF00`

### Verifying the status of the valve

Perfomed by reading the value of `valve-in`:
- address: `0x52`
- function: read single coil, decimal 1 = `0x01`
- data:
  - address: decimal 12 = `0x000B`
  - value: read 2 inputs, decimal 2 = `0x0002`
- message typed: `5201000B0002`

Actually this doesn't work since the response of the PLC is not forwarded.
To check the status of the system, just select "1" from the menu.

## Opening the out-valve

Forcing the opening of the `out-valve` is a bit more involved ; it requires:
- enabling the `manual-mode`
- disabling the `stop-out`
- enabling the `force-start-out`

Manual mode is already on at this point. Two steps left!

`stop-out` is turned off from the get go.

Activating `force-out`:
- address: `0x52`
- function: `0x05`
- data:
  - address: decimal 52 = `0x0034`
  - value: `0xFF00`
- message typed: `52050034FF00`

Finally!!! As you can tell by the size of this write-up, I struggled here x\_x

[wikipedia-modbus-url]: https://en.wikipedia.org/wiki/Modbus#Modbus_ASCII_frame_format_(primarily_used_on_7-_or_8-bit_asynchronous_serial_lines)
