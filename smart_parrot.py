# Logging library for automated log print registers
import logging
import time

import nltk

from Database.database import close_database, connect_database, delete_table_data
from Transmission.print_scheme import print_function
from Turing.persona import nltk_ignition
from Web.web_application import app

# Log parameters adjustment call
# _ Hour (24 hours format)
# _ Minutes
# _ Seconds
# _ Month-Day
# _ Level to print and above
# _ Message to show

# Print in software terminal
logging.basicConfig(level=logging.INFO,
                    format='[ %(asctime)s ] - %(levelname)s:  %(message)s',
                    datefmt='%H:%M:%S %m-%d-%y')


def application():
    """" All application has its initialization from here """
    logging.info('Main application is running!')

    """" Create a database connection to a SQLite database """
    connect_database()

    """ Download or/and update the language-neutral sentence segmentation tool """
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk_ignition()

    time.sleep(1)

    while True:
        # Run the application.

        print_function('OUT', '\n\n\n'
                              '\n(1) Rise the Monster!'
                              '\n(D) Delete all database data.'
                              '\n(E) Exit.')

        opt = print_function('IN', '\nChoose the next step:  ')

        if opt is '1':
            # dialog()

            app.run()
            while True:
                return True

        elif opt is 'D':
            delete_table_data()
        elif opt is 'E':
            close_database()
            exit()
        else:
            print_function('OUT', 'There is no such option number.\n\n')
