import datetime
import pandas as pd

class TimeRecord:
    def __init__(self):
        """
        dict_current_overall_measurement ... here we save the measurement of the current iteration
        dict_current_agent_measurement ... the measuremement of the current agent
        df_agent_measurements ... this is the df which collects all measurements of each agent for one step,
        df_overall_computational_times ... measurements of all iterations of one case (columns='Step', 'agent_duration',
        'agent_duration_seconds', 'overall_duration', 'overall_duration_seconds')

        """
        self.computational_time_dict = None
        self.current_iteration = 0
        self.list_agent_measurements_sec = []
        self.df_overall_computational_times = pd.DataFrame()
        self.current_step = None
        self.overall_measurement_active = False
        self.agent_measurement_active = False
        self.start_time_overall = None
        self.start_time_agent = None
        self.overall_duration_sec = None

    def add_new_iteration(self):
        self.current_iteration +=1

    def start_measurement(self, step):
        if self.overall_measurement_active:
            self.stop_measurement()
        self.overall_measurement_active = True
        self.current_step = step
        self.start_time_overall = datetime.datetime.now()

    def stop_measurement(self):
        end_time = datetime.datetime.now()
        self.overall_duration_sec = (end_time - self.start_time_overall).total_seconds()
        self.overall_measurement_active = False
        if self.agent_measurement_active:
            self.stop_agent_measurement()
        self.add_measurement_to_overall_df()
        self.list_agent_measurements_sec = []

    def add_measurement_to_overall_df(self):
        sr_measurement = pd.Series({
            'step': self.current_step,
            'iteration': self.current_iteration,
            'overall_duration': self.overall_duration_sec,
            'max_duration_agent': self.get_max_duration_agents()})
        self.df_overall_computational_times = pd.concat([self.df_overall_computational_times,
                                                    sr_measurement.to_frame().T], ignore_index=True)

    def start_agent_measurement(self):
        if self.agent_measurement_active:
            self.stop_agent_measurement()
        self.agent_measurement_active = True
        self.start_time_agent = datetime.datetime.now()

    def stop_agent_measurement(self):
        end_time_agent = datetime.datetime.now()
        duration = (end_time_agent - self.start_time_agent).total_seconds()
        self.list_agent_measurements_sec.append(duration)
        self.agent_measurement_active = False

    def get_max_duration_agents(self):
        max_duration = 0.0
        if len(self.list_agent_measurements_sec) > 0:
            max_duration = max(self.list_agent_measurements_sec)
        return max_duration

    def set_case_name_and_id_to_df(self, case_name, case_id):
        self.df_overall_computational_times.loc[:, 'case_name'] = case_name
        self.df_overall_computational_times.loc[:, 'case_id'] = case_id

    def get_df_computation_time(self):
        return self.df_overall_computational_times.copy()





