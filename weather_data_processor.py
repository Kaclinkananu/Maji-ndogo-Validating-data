### START FUNCTION 
import re
import numpy as np
import pandas as pd
import logging
from data_ingestion import read_from_web_CSV

class WeatherDataProcessor:
    """Processes weather data based on configuration parameters.

    Args:
        config_params (dict): A dictionary containing configuration parameters.
        logging_level (str, optional): The logging level. Defaults to "INFO".

    Attributes:
        weather_station_data (str): The path to the weather station data CSV file.
        patterns (dict): A dictionary mapping measurement keys to regex patterns.
        weather_df (pandas.DataFrame): The DataFrame containing the weather data.
        logger (logging.Logger): The logger object.

    Methods:
        initialize_logging(logging_level): Initializes logging for the instance.
        weather_station_mapping(): Maps weather station data to the DataFrame.
        extract_measurement(message): Extracts measurements from messages using regex patterns.
        process_messages(): Processes messages to extract measurements.
        calculate_means(): Calculates mean values of measurements.
        process(): Executes the processing pipeline.

    """

    def __init__(self, config_params, logging_level="INFO"):
        """Initializes the WeatherDataProcessor instance.

        Args:
            config_params (dict): A dictionary containing configuration parameters.
            logging_level (str, optional): The logging level. Defaults to "INFO".

        """
        self.weather_station_data = config_params['weather_csv_path']
        self.patterns = config_params['regex_patterns']
        self.weather_df = None
        self.initialize_logging(logging_level)

    def initialize_logging(self, logging_level):
        """Sets up logging for the WeatherDataProcessor instance.

        Args:
            logging_level (str): The logging level.

        """
        logger_name = __name__ + ".WeatherDataProcessor"
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False

        if logging_level.upper() == "DEBUG":
            log_level = logging.DEBUG
        elif logging_level.upper() == "INFO":
            log_level = logging.INFO
        elif logging_level.upper() == "NONE":
            self.logger.disabled = True
            return
        else:
            log_level = logging.INFO

        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def weather_station_mapping(self):
        """Maps weather station data to the DataFrame."""
        self.weather_df = read_from_web_CSV(self.weather_station_data)
        self.logger.info("Successfully loaded weather station data from the web.") 

    def extract_measurement(self, message):
        """Extracts measurements from messages using regex patterns.

        Args:
            message (str): The message containing measurement information.

        Returns:
            tuple: A tuple containing the extracted measurement key and value.

        """
        for key, pattern in self.patterns.items():
            match = re.search(pattern, message)
            if match:
                self.logger.debug(f"Measurement extracted: {key}")
                return key, float(next((x for x in match.groups() if x is not None)))
        self.logger.debug("No measurement match found.")
        return None, None

    def process_messages(self):
        """Processes messages to extract measurements."""
        if self.weather_df is not None:
            result = self.weather_df['Message'].apply(self.extract_measurement)
            self.weather_df['Measurement'], self.weather_df['Value'] = zip(*result)
            self.logger.info("Messages processed and measurements extracted.")
        else:
            self.logger.warning("weather_df is not initialized, skipping message processing.")
        return self.weather_df

    def calculate_means(self):
        """Calculates mean values of measurements."""
        if self.weather_df is not None:
            means = self.weather_df.groupby(by=['Weather_station_ID', 'Measurement'])['Value'].mean()
            self.logger.info("Mean values calculated.")
            return means.unstack()
        else:
            self.logger.warning("weather_df is not initialized, cannot calculate means.")
            return None
    
    def process(self):
        """Executes the processing pipeline."""
        self.weather_station_mapping()
        self.process_messages()
        self.logger.info("Data processing completed.")

### END FUNCTION