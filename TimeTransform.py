# Module that allows the user to transform miliseconds features to minutes features
# and datetime features to two separate hour and month features.
# This package can be used as library if placed in the same repository of the files that
# will use this module.

# For example, to import this class as a module, you will just have to type :
# from TimeTransform import TimeTransform

# Then, if you want to specifically use a method inside of the class, let's say, 
# split the datetime to hours and months, you'll have to :
# time_transform = TimeTransform(df, dt_feature)
# df_time = time_transform.datetime_split()

### Import libraries

import pandas as pd

### Contents of the class

class TimeTransform(object):
    """
    Class that aims to transform both time and datetime based features to 
    exploitable features (for example, ms -> min, datetime -> hour; month; day).
    """
    
    def second_to_minutes(self, time):
        """
        Method that allows to convert time from miliseconds to minutes.
        ------
        Parameters:
            - time: time of the song in ms to convert on minutes
        """
        
        self.time_new = divmod(time, 60000)
        self.minutes = self.time_new[0]
        self.seconds = self.time_new[1]
        self.final_time = str(self.minutes) + '.' + str(self.seconds)

        return self.final_time
    
    def datetime_split(self, df, dt_feature):
        """
        Method that aims to allows the user to extract specific elements from a datetime feature 
        such as : time, date, hour and to create separate features with them.

        Parameters:
            - df: Input DataFrame that contains the feature in datetime format.
            - dt_feature: The datetime feature that we want to split.
        """

        self.df = df
        self.dt_feature = dt_feature

        self.df[self.dt_feature] = self.df[self.dt_feature].replace('T', ' ', regex=True).replace('Z', '', regex=True)
        self.df[self.dt_feature] = pd.to_datetime(self.df[self.dt_feature], format='%Y-%m-%d %H:%M:%S')
        self.df['added_hour'] = self.df[self.dt_feature].dt.hour
        self.df['added_month'] = self.df[self.dt_feature].dt.month
        self.df_2 = self.df.drop(columns=[self.dt_feature], axis=1)

        return self.df_2