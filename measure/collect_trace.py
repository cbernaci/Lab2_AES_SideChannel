import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from WF_SDK import device, scope, wavegen, tools, error   # import instruments


try:
    # connect to the device
    device_data = device.open()

    # initialize the scope with default settings
    # TODO change frequency to 100MHz?
    scope.open(device_data, sampling_frequency=20e06, amplitude_range=5)

    # set up triggering on scope channel 1
    scope.trigger(device_data, enable=True,
                  source=scope.trigger_source.none, channel=1)

    # generate a 10KHz sine signal with 2V amplitude on channel 1
    wavegen.generate(device_data, channel=1, function=wavegen.function.sine,
                     offset=0, frequency=10e03, amplitude=2)
 
    # record data with the scope on channel 1
    buffer = scope.record(device_data, channel=1)
    # buffer len is 8192

    # # generate buffer for time moments
    # time = []
    # for index in range(len(buffer)):
    #     # convert time to ms
    #     time.append(index * 1e03 / scope.data.sampling_frequency)

    """-----------------------------------"""
    # # Set up the plot
    # fig, ax = plt.subplots()
    # line, = ax.plot(buffer)
    # ax.set_xlabel('time')
    # ax.set_ylabel('voltage [V]')
    # ax.set_ylim(-3.3, 3.3)
    
    total_buff = []
    
    while True:
        buffer = scope.record(device_data, channel=1)
        total_buff.append(buffer)

    # # Define the update function for the animation
    # def update(frame):
    #     # Update the line data
    #     buffer = scope.record(device_data, channel=1)
    #     total_buff.append(buffer)
    #     line.set_ydata(buffer)
    #     return line,

    # # Create the animation
    # ani = FuncAnimation(fig, update, frames=100,
    #                     interval=0, blit=True)

    # plt.show()

except KeyboardInterrupt:
    print("KeyboardInterrupt, program stopped")
except error as e:
    raise e
finally:
    # reset the scope
    scope.close(device_data)
    # reset the wavegen
    wavegen.close(device_data)
    # close the connection
    device.close(device.data)

    # save data
    total_buff = np.array(total_buff).flatten()
    np.save('total_buff.npy', total_buff)

    print("savely exited")
