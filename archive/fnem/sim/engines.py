import numpy as np
from utils.common_defs import DTYPE
from utils.common_defs import DEFAULT_COMMANDS


class SimulationMachine(object):
    '''
    intended operation:
    1. update the machine setting - use an action from the list of commands.
    2. step the machine
        a. step the data generator (generate data and advance the time)
        b. add noise
        c. update sensor values
        d. if logging, record machine state
    3. report the "heat" (difference between machine setting and true state)

    when finished, call `close_logger()` to zip the log file.
    '''

    def __init__(
        self, setting, data_generator, noise_model, logger=None, commands=None,
        maxsteps=None
    ):
        self._data_generator = data_generator
        self._noise_model = noise_model
        self._setting = setting
        self._heat = 0.0
        self._true_state = 0.0
        self._commands = commands or DEFAULT_COMMANDS
        self._sensors = np.zeros(4, dtype=DTYPE)
        self._logger = logger
        self._maxsteps = maxsteps
        self._nsteps = 0

    def update_machine(self, command):
        '''command is the index of the step change'''
        self._setting = self._setting + self._commands[command]

    def step(self):
        '''returns False if out of steps'''
        if self._maxsteps:
            if self._nsteps >= self._maxsteps:
                return False
        data = self._data_generator.step()
        self._true_state = np.sum(data)
        noise = self._noise_model.gen_noise(data)
        measured = data + noise
        self._sensors = measured
        if self._logger is not None:
            self._logger.write_data(self._data_generator.t, self._setting,
                                    measured, data)
        self._nsteps += 1
        return True

    def get_heat(self):
        return (self._true_state - self._setting) ** 2

    def get_time(self):
        return self._data_generator.t

    def get_setting(self):
        return self._setting

    def get_commands(self):
        return list(self._commands)

    def get_sensor_values(self):
        return list(self._sensors)

    def close_logger(self):
        self._logger.close()
