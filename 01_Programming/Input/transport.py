import pandas as pd


class Transport:
    def __init__(self, df_transport=pd.DataFrame()):
        self.df_transport = df_transport

    def get_travel_time(self, origin, destination):
        travel_time = float(self.df_transport[self.df_transport["destination"] == destination][origin].iloc[0])
        return travel_time
