from urh import constants
import numpy as np

import zmq

from urh.dev.gr.AbstractBaseThread import AbstractBaseThread
from urh.util.Logger import logger


class SpectrumThread(AbstractBaseThread):
    def __init__(self, freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, ip='127.0.0.1', parent=None):
        super().__init__(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, True, ip, parent)
        self.buf_size = constants.SPECTRUM_BUFFER_SIZE
        self.data = np.zeros(self.buf_size, dtype=np.complex64)
        self.x = None
        self.y = None
        self.my_all_data = []
    def run(self):
        logger.debug("Spectrum Thread: Init Process")
        self.initialize_process()
        logger.debug("Spectrum Thread: Process Intialized")
        self.init_recv_socket()
        logger.debug("Spectrum Thread: Socket initialized")

        recv = self.socket.recv
        rcvd = b""

        try:
            logger.debug("Spectrum Thread: Enter main loop")
            while not self.isInterruptionRequested():

                try:
                    rcvd += recv(32768)  # Receive Buffer = 32768 Byte
                except zmq.error.Again:
                    # timeout
                    continue
                except (zmq.error.ContextTerminated, ConnectionResetError):
                    self.stop("Stopped receiving, because connection was reset")
                    return
                except OSError as e:  # https://github.com/jopohl/urh/issues/131
                    logger.warning("Error occurred", str(e))

                if len(rcvd) < 8:
                    self.stop("Stopped receiving, because no data transmitted anymore")
                    return

                if len(rcvd) % 8 != 0:
                    continue

                try:
                    tmp = np.fromstring(rcvd, dtype=np.complex64)

                    len_tmp = len(tmp)

                    if self.data is None:
                        self.data = np.zeros(self.buf_size, dtype=np.complex64)  # type: np.ndarray

                    if self.current_index + len_tmp >= len(self.data):
                        self.data[self.current_index:] = tmp[:len(self.data) - self.current_index]
                        tmp = tmp[len(self.data) - self.current_index:]
                        w = np.abs(np.fft.fft(self.data))
                        freqs = np.fft.fftfreq(len(w), 1 / self.sample_rate)
                        idx = np.argsort(freqs)
                        self.x = freqs[idx].astype(np.float32)
                        self.y = w[idx].astype(np.float32)

                        self.data = np.zeros(len(self.data), dtype=np.complex64)
                        self.data[0:len(tmp)] = tmp
                        self.current_index = len(tmp)
                        continue

                    self.data[self.current_index:self.current_index + len_tmp] = tmp
                    self.current_index += len_tmp
                    return rcvd
                    rcvd = b""
                except ValueError:
                    self.stop("Could not receive data. Is your Hardware ok?")
        except RuntimeError as e:
            logger.error("Spectrum thread crashed", str(e.args))
