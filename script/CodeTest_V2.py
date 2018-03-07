from picosdk import ps6000
from ctypes import *
import matplotlib.pyplot as plt
import numpy as np
import threading
import time

ps_picoscope =  ps6000.Device()
statusopen = ps_picoscope.open_unit('ET300/013')
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
#Samples = 500000000
bufflen = 500000000

data = {}
data[0]["max"] = np.empty(bufflen, dtype=c_int16)
data[1]["max"] = np.empty(bufflen, dtype=c_int16)

ps_picoscope.release_all_buffers()
status_bufferA = ps_picoscope._set_data_buffers(line=0, buffer_max=data["max"].ctypes,buffer_min=None,bufflen=bufflen,segment=0,mode=ps_picoscope.m.RatioModes.raw)
print(status_bufferA)

#
# # Trigger
triggerChannel = ps_picoscope.m.TriggerChannels.A
direction = ps_picoscope.m.ThresholdDirections.rising
thresholdVoltage = 0

status_trigger = ps_picoscope.set_simple_trigger(enabled=True, source=triggerChannel, threshold=thresholdVoltage, direction=direction, waitfor=1000)

ps_picoscope._collect_cb_type = ps_picoscope._block_ready()
ps_picoscope._collect_cb_func = ps_picoscope._collect_cb_type(ps_picoscope._collect_cb)
status=ps_picoscope._run_block(pretrig=0,posttrig=bufflen,timebase=7,oversample=0,ref_time=None,segment=0,ref_cb=ps_picoscope._collect_cb_func,ref_cb_param=None)
print(status)
ps_picoscope._collect_event.wait()

print('triggerDone')
#
# tupl= (0,0)
# status = ps_picoscope._get_buffer_values(tupl)
# # print(status)
#
overvoltaged = c_int16(0)
samples = c_uint32(1000)

a = ps_picoscope._get_values(start=100, ref_samples=byref(samples),ratio=1, mode=ps_picoscope.m.RatioModes.none, segment=0,ref_overflow=byref(overvoltaged))
print(a)
#
plt.plot(data["max"])
plt.show()
# #
# status, infoA_I = ps_picoscope.get_buffer_info(index=0)
# print(status)
# infoA = ps_picoscope.get_buffer_volts(index=0)[1][100:1000]
# print(status)
# print(infoA_I)
#
# #x = infoA_I["real_interval"] * np.asarray(range(0,infoA_I["samples"]))
# plt.plot(infoA,color = 'blue')
# plt.show()