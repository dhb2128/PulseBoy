from PyQt5 import QtCore
from time import sleep
import daqface.DAQ as daq
from pypulse import PulseInterface
import scipy.io as sio
import numpy as np


class QueueWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    trial_start = QtCore.pyqtSignal()

    def __init__(self, parent, experiment, get_global_params, get_hardware_params, get_export_params):
        super(self.__class__, self).__init__(None)
        self.parent = parent
        self.experiment = experiment
        self.get_global_params = get_global_params
        self.get_hardware_params = get_hardware_params
        self.get_export_params = get_export_params

    @QtCore.pyqtSlot()
    def trial(self):
        while True:
            sleep(0.05)
            if self.parent.should_run:
                self.trial_start.emit()

                trial_params = self.experiment.arraydata[self.experiment.current_trial][1]
                hardware_params = self.get_hardware_params()
                global_params = self.get_global_params()
                export_params = self.get_export_params()

                pulses, t = PulseInterface.make_pulse(hardware_params['samp_rate'],
                                                      global_params['global_onset'],
                                                      global_params['global_offset'],
                                                      trial_params)

                self.trial_daq = daq.DoAiMultiTask(hardware_params['analog_dev'], hardware_params['analog_channels'],
                                                   hardware_params['digital_dev'], hardware_params['samp_rate'],
                                                   len(t) / hardware_params['samp_rate'], pulses,
                                                   hardware_params['sync_clock'])

                self.analog_data = self.trial_daq.DoTask()

                # Save data
                save_string = export_params['export_path'] + str(self.experiment.current_trial) + \
                              export_params['export_suffix'] + '.mat'
                sio.savemat(save_string, {'analog_data': self.analog_data, 'pulses': pulses, 't': t})

                if self.experiment.total_trials() - self.experiment.current_trial == 1:
                    self.parent.should_run = False
                    self.experiment.reset_trials()

                if self.parent.should_run:
                    self.experiment.advance_trial()

                self.finished.emit()


class QueueController(QtCore.QObject):
    trial_start = QtCore.pyqtSignal()

    def __init__(self, experiment, get_global_params, get_hardware_params, get_export_params):
        super(self.__class__, self).__init__(None)
        self.experiment = experiment
        self.get_global_params = get_global_params
        self.get_hardware_params = get_hardware_params
        self.get_export_params = get_export_params
        self.prepare_thread()

        self.should_run = False

    def prepare_thread(self):
        self.thread = QtCore.QThread()
        self.worker = QueueWorker(self, self.experiment, self.get_global_params, self.get_hardware_params,
                                  self.get_export_params)
        self.worker.moveToThread(self.thread)
        self.worker.trial_start.connect(self.trial_start.emit)
        self.thread.started.connect(self.worker.trial)

        self.thread.start()

    def start(self):
        if not self.should_run:
            self.should_run = True

    def pause(self):
        if self.should_run:
            self.should_run = False
            self.experiment.advance_trial()

    def stop(self):
        if self.should_run:
            self.should_run = False

        self.experiment.reset_trials()

    def run_selected(self, trial):
        if not self.should_run:
            self.should_run = True
            self.experiment.current_trial = trial
            sleep(0.05)
            self.should_run = False

    def finished(self):
        print("not implemented")

