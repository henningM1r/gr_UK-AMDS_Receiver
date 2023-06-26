# -*- coding: iso-8859-1 -*-

import zmq
from crccheck.crc import Crc13Bbc
from bitstring import Bits


class Class_DecodeUKAMDS():

    def __init__(self):
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]
        self.leap_year = ["This year is a leap year",
                          "Last year was a leap year",
                          "Leap year two or more years away",
                          "Next year is a leap year"]

        self.filler_code = [1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                            1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                            0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1]

    def decode_BCD(self, bits, length):
        list1 = [bits[i] for i in range(0, length)]
        if 3 in list1:
            return "?"

        str1 = ''.join(str(e) for e in list1)
        val = int(str1, 2)

        return val

    def CRC_compute(self, bitstream32):
        data = bytearray.fromhex(bitstream32)

        crcinst = Crc13Bbc()
        crcinst.process(data)
        crchex = crcinst.finalhex()

        return crchex

    def CRC_comparison(self, bitstream):
        output = ""

        # CRC
        # received message bits
        msg_in_bin = list(map(str, bitstream[5:37]))
        # print("MSG_in (bin):", msg_in_bin)
        msg_in_bin = "".join(msg_in_bin)
        # msg_in_hex = hex(int(msg_in_bin, 2))
        msg_in_dec = int(msg_in_bin, 2)
        msg_in_hex = format(msg_in_dec, '04x')
        msg_in_hex = str(msg_in_hex).zfill(8)
        # output += f"MSG_in  (hex): 0x" + msg_in_hex + "\n"

        # received CRC bits
        crc_in_bin = list(map(str, bitstream[37:50]))
        # print("CRC_in (bin): ", crc_in_bin)
        crc_in_bin = "".join(crc_in_bin)
        crc_in_dec = int(crc_in_bin, 2)
        crc_in_hex = format(crc_in_dec, '04x')
        crc_in_hex = str(crc_in_hex).zfill(4)
        # output += "CRC_in  (hex): 0x" + crc_in_hex + "\n"

        # compute CRC from message bits
        crc_out_hex = self.CRC_compute(bitstream32=msg_in_hex)
        crc_out_dec = int(crc_out_hex, 16)
        crc_out_hex = format(crc_out_dec, '04x')
        crc_out_hex = str(crc_out_hex).zfill(4)
        # output += "CRC_out (hex): 0x" + crc_out_hex + "\n"

        if crc_in_hex == crc_out_hex:
            output += "CRC comparison is valid.\n"
            return [True, output]
        else:
            output += "CRC invalid.\n"

        return [False, output]

    def decode_time_bitstream(self, bitstream):
        output = "01-05: Time-Header detected.\n"

        [crc_valid, info] = self.CRC_comparison(bitstream)

        if not crc_valid:
            output += info
            output += "CRC comparison failed.\n"

        elif crc_valid:
            output += "00: Start-bit is 1.\n"

            # leap year
            leap_year = self.decode_BCD([bitstream[6], bitstream[7]], 2)
            output += f"06-07: {self.leap_year[leap_year]}.\n"

            # start day
            start_weekday = self.decode_BCD([bitstream[8], bitstream[9],
                                             bitstream[10]], 3)
            output += "17-19: First weekday of year: " + \
                      f"{self.weekdays[start_weekday - 1]}.\n"

            # week
            week = self.decode_BCD([bitstream[11], bitstream[12],
                                    bitstream[13], bitstream[14],
                                    bitstream[15], bitstream[16]], 6)
            output += f"11-16: Week {week}.\n"

            # day of week
            weekday = self.decode_BCD([bitstream[17], bitstream[18],
                                       bitstream[19]], 3)
            output += f"17-19: Weekday: {self.weekdays[weekday - 1]}.\n"

            # hour
            hour = self.decode_BCD([bitstream[20], bitstream[21],
                                    bitstream[22], bitstream[23],
                                    bitstream[24]], 5)
            output += f"20-24: Hour {hour:02d}.\n"

            # minute
            minute = self.decode_BCD([bitstream[25], bitstream[26],
                                      bitstream[27], bitstream[28],
                                      bitstream[29], bitstream[30]], 6)

            output += f"25-30: Minute {minute:02d}.\n"

            # local offset
            l_offset = self.decode_BCD([bitstream[32],
                                        bitstream[33], bitstream[34],
                                        bitstream[35], bitstream[36]], 5)
            if bitstream[31] == 0:
                output += "Time incl. offset: " + \
                          f"{hour + l_offset:02d}:{minute:02d}h\n"

            elif bitstream[31] == 1:
                # read bitstream block as binary
                # two's complement representation
                l_offset_bits = "".join(str(s) for s in bitstream[31:37])
                l_offset = Bits(bin=l_offset_bits)
                output += "Time incl. offset: " + \
                          f"{hour + l_offset.int:02d}:{minute:02d}h\n"

        output += f"{bitstream}\n"

        return output

    def decode_filler_bitstream(self, bitstream):
        output = ""
        if bitstream == self.filler_code:
            output = "Received filler code."

        return output

    def decode_other_bitstream(self, bitstream):
        output = "Received other application code.\n"
        output += f"{bitstream}"

        return output

    def decode_bitstream(self, bitstream):
        output = ""

        if len(bitstream) != 50:
            output += f"Decoding error\nReceived bits: {len(bitstream)}\n"
            bitstream_str = list(map(str, bitstream))
            output += "".join(bitstream_str) + "\n"
            return output

        output += "\n"

        # check sync bit
        if bitstream[0] == 0:
            # should never happen, as this is already taken care of by framer
            output += "00: Start-bit is 0 instead of 1!\n"

        elif bitstream[0] == 1:
            if bitstream[1:6] == [0, 0, 0, 0, 0]:
                output += self.decode_time_bitstream(bitstream)

            elif bitstream[1:6] == [0, 0, 0, 0, 1]:
                output += self.decode_filler_bitstream(bitstream)

            # These other application codes were observed aside the
            # two codes above. Unfortunately, the specification of
            # those codes is not publicly available.
            elif bitstream[1:6] == [0, 1, 0, 1, 0]:
                output += self.decode_other_bitstream(bitstream)

            elif bitstream[1:6] == [0, 1, 0, 1, 1]:
                output += self.decode_other_bitstream(bitstream)

            elif bitstream[1:6] == [1, 1, 1, 0, 1]:
                output += self.decode_other_bitstream(bitstream)

            else:
                output += "Unknown application code.\n"

        return output

    def consumer(self):
        context = zmq.Context()

        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect("tcp://127.0.0.1:55555")

        while True:
            data = consumer_receiver.recv()
            received_msg = data.decode('ascii')[3:]

            # print(f"received frame: {received_msg[1:-1]}")

            # convert received string to list
            bitstream = received_msg[1:-1].replace('\n', '')
            bitstream = bitstream.split(",")
            bitstream = list(map(int, bitstream))

            output = self.decode_bitstream(bitstream)

            print(output)

