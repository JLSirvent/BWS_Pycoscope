from picosdk import ps6000
from ctypes import *
import matplotlib.pyplot as plt
import numpy as np
import threading
import time

ps_picoscope =  ps6000.Device()
statusopen = ps_picoscope.open_unit('ET300/013')
time.sleep(5)
print(statusopen)


# Scopes configuration:
# --------------------
s_A, state_A = ps_picoscope.get_channel_state(channel=ps_picoscope.m.Channels.A)

# Channel Config:
state_A.coupling = ps_picoscope.m.Couplings.dc50
state_A.bwlimit = ps_picoscope.m.BWLimit.bw_full
state_A.enabled = True
state_A.offset = 0
state_A.range = ps_picoscope.m.Ranges.r1v

status_A = ps_picoscope.set_channel(channel=ps_picoscope.m.Channels.A, state=state_A)
print(status_A)

# Buffers
status_bufferA, idx_bufferA = ps_picoscope.locate_buffer(channel=ps_picoscope.m.Channels.A, samples=10000,
                                                              segment=0, mode=ps_picoscope.m.RatioModes.raw,
                                                              downsample=0)
print(status_bufferA)

# Trigger
triggerChannel = ps_picoscope.m.TriggerChannels.A
direction = ps_picoscope.m.ThresholdDirections.rising
thresholdVoltage = 0

status_trigger = ps_picoscope.set_simple_trigger(enabled=True, source=triggerChannel, threshold=thresholdVoltage,
                                                      direction=direction, waitfor=1000)
print(status_trigger)

# Start Acquisition (TimeBase 7 --> Fs ~ 52.08Mhz)
ps_ready= threading.Event()
status_Acq = ps_picoscope.collect_segment(segment=0,timebase=7, block=False, event_handle=ps_ready)
ps_ready.wait()

# tupl= (0,0)
# status = ps_picoscope._get_buffer_values(tupl)
# print(status)

overvoltaged = c_int16(0)
start = c_uint32(10)
samples = c_uint32(1000)
ratio = c_uint32(0)
segment = c_uint32(0)
a=ps_picoscope._get_values(start=0, ref_samples=byref(samples),ratio=1,mode=ps_picoscope.m.RatioModes.raw, segment=0,ref_overflow=byref(overvoltaged))
print(a)

status, infoA_I = ps_picoscope.get_buffer_info(index=0)
print(status)
status, infoA = ps_picoscope.get_buffer_volts(index=0)
print(status)
print(infoA_I)

x = infoA_I["real_interval"] * np.asarray(range(0,infoA_I["samples"]))
plt.plot(x,infoA,color = 'blue')
plt.show()