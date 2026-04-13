import os
import sys

# static class
class My_Logger:
    file_name = 'log.txt'
    file = None
    def __init__(self, file_name='log.txt', case_name='default'):
        self.file_name = file_name
        # check if file exists
        # if not, create file
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w') as file:
                file.write(f"\n========================== Log file for {case_name} =========================\n")
        else:
            with open(self.file_name, 'a') as file:
                file.write(f"\n========================== Log file for {case_name} =========================\n")


    def log(self, message):
        print(message)

    def log_to_file(self, message):
        with open(self.file_name, 'a') as file:
            file.write(message)