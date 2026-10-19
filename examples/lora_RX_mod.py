#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lora Rx
# Author: Tapparel Joachim@EPFL,TCL
# GNU Radio version: 3.10.11.0

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gnuradio.lora_sdr as lora_sdr
import numpy as np
import threading


class lora_RX(gr.top_block):

    def __init__(self, input_file='input.cfile', sf=12, cr=4, soft_decoding=True, samp_rate=1000000, bw=125000, sync_word=52, ldro_mode=2, enable_lorasr=False, center_freq=868.1e6):
        gr.top_block.__init__(self, "Lora Rx", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.input_file = input_file
        self.sf = sf

        ##################################################
        # Variables
        ##################################################
        self.soft_decoding = soft_decoding
        self.samp_rate = samp_rate
        self.pay_len = pay_len = 0
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.cr = cr
        self.center_freq = center_freq
        self.bw = bw

        ##################################################
        # Blocks
        ##################################################

        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc, ldro_mode, True)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [sync_word], (int(samp_rate/bw)),8)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(soft_decoding, True, enable_lorasr=enable_lorasr)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif(self.cr, False)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, input_file, False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0.set_min_output_buffer(4000000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_header_decoder_0, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        
        # Connect source -> frame_sync
        self.connect((self.blocks_file_source_0, 0), (self.lora_sdr_frame_sync_0, 0))
        
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_mapping_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_mapping_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))


    def get_input_file(self):
        return self.input_file

    def set_input_file(self, input_file):
        self.input_file = input_file
        self.blocks_file_source_0.open(self.input_file, False)

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf

    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--input-file", dest="input_file", type=str, default='input.cfile',
        help="Set input_file [default=%(default)r]")
    parser.add_argument(
        "--sf", dest="sf", type=intx, default=12,
        help="Set sf [default=%(default)r]")
    parser.add_argument(
        "--cr", dest="cr", type=intx, default=4,
        help="Set coding rate [default=%(default)r]")
    parser.add_argument(
        "--soft-decoding", dest="soft_decoding", type=intx, default=1,
        help="Set soft decoding (0 or 1) [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=intx, default=1000000,
        help="Set sample rate [default=%(default)r]")
    parser.add_argument(
        "--bw", dest="bw", type=intx, default=125000,
        help="Set bandwidth [default=%(default)r]")
    parser.add_argument(
        "--sync-word", dest="sync_word", type=intx, default=52,
        help="LoRa sync word: 52=LoRaWAN (0x34), 18=raw LoRa (0x12) [default=%(default)r]")
    parser.add_argument(
        "--ldro-mode", dest="ldro_mode", type=intx, default=2,
        help="LDRO mode: 0=off, 1=on, 2=auto [default=%(default)r]")
    parser.add_argument(
        "--enable-lorasr", dest="enable_lorasr", action="store_true", default=False,
        help="Enable LoRaSR waveform reconstruction in fft_demod [default=%(default)r]")
    parser.add_argument(
        "--center-freq", dest="center_freq", type=float, default=868.1e6,
        help="Center frequency in Hz [default=%(default)r]")
    return parser


def main(top_block_cls=lora_RX, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(input_file=options.input_file, sf=options.sf, cr=options.cr,
                       soft_decoding=bool(options.soft_decoding),
                       samp_rate=options.samp_rate, bw=options.bw,
                       sync_word=options.sync_word, ldro_mode=options.ldro_mode,
                       enable_lorasr=options.enable_lorasr,
                       center_freq=options.center_freq)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    tb.wait()


if __name__ == '__main__':
    main()
