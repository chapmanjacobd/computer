#!/usr/bin/python3
# https://github.com/opensource25/Syncthing-Audit-Log-Viewer/blob/main/audit-log-viewer.py
from datetime import datetime, timedelta
import argparse
import platform
import json
import gzip
import os
import re
import sys


class log_viewer():
    def __init__(self):
        self.devices = {}
        self.counter = 0
        self.queue = []

    def read(self, log_folder, date_start, date_end, filter_name, filter_action):
        files = os.listdir(log_folder)
        files.sort()
        start_date = datetime.strptime(str(date_start), "%Y%m%d")
        end_date = datetime.strptime(str(date_end), "%Y%m%d")
        for file in files:
            if file.startswith("audit"):
                path = os.path.join(log_folder, file)
                if file.endswith(".log"):
                    with open(path, "r") as log_file:
                        self.analyse_file(end_date, filter_name, filter_action, log_file, start_date)
                if file.endswith(".log.gz"):
                    with gzip.open(path, "r") as log_file:
                        self.analyse_file(end_date, filter_name, filter_action, log_file, start_date)

        self.printer(end_of_log=True)

    def analyse_file(self, end_date, filter_name, filter_action, log_file, start_date):
        for line in log_file:
            self.log_dict = json.loads(line)
            self.first_filter(filter_name, filter_action, start_date, end_date)

    def first_filter(self, filter_name, filter_action, date_start, date_end):
        if self.log_dict["type"] == "DeviceConnected":
            id = self.log_dict["data"]["id"][:7]
            deviceName = self.log_dict["data"]["deviceName"]
            self.devices[id] = deviceName

        elif self.log_dict["type"] == "Starting":
            myID = self.log_dict["data"]["myID"][:7]
            self.devices[myID] = "Me"

        elif str(self.log_dict["type"]).endswith("ChangeDetected") and self.name_filter(filter_name) and self.action_filter(filter_action) and self.date_filter(date_start, date_end):
            self.counter = self.counter + 1
            modifiedBy = self.log_dict["data"]["modifiedBy"]
            data = {
                "time" : self.log_dict["time"], #[0:22]
                "change_type" : self.log_dict["type"][:-14],
                "action" : self.log_dict["data"]["action"],
                "folderID" : self.log_dict["data"]["label"],
                "device_name" : self.devices.get(modifiedBy, modifiedBy),
                "data_type" : self.log_dict["data"]["type"],
                "file" : self.log_dict["data"]["path"]
            }

            self.queue.append(data)
            self.printer()


    def stats(self):
        data = {
            "entries" : self.counter
        }
        print("Einträge: {entries}".format(**data))
        # print(self.tempcount)

    def date_filter(self, start_date, end_date):
        file_date = datetime.strptime(self.log_dict["time"][:10], "%Y-%m-%d")
        if file_date >= start_date and file_date <= end_date:
            return True
        else:
            return False

    def name_filter(self, filter_name):
        if filter_name == None:
            return True
        else:
            if re.search(filter_name, self.log_dict["data"]["path"]):
                return True
            else:
                return False

    def action_filter(self, filter_action):
        if filter_action == None:
            return True
        else:
            if re.search(filter_action, self.log_dict["data"]["action"]):
                return True
            else:
                return False

    def printer(self, end_of_log=False):
        #   "time": "2021-04-18T13:06:50.623615083+02:00"

        if len(self.queue) > 0:
            first_element_unixtime = datetime.strptime(self.convert_time(self.queue[0]["time"]), "%Y-%m-%dT%H:%M:%S%z")
            latest_element_unixtime = datetime.strptime(self.convert_time(self.queue[-1]["time"]), "%Y-%m-%dT%H:%M:%S%z")

            while (latest_element_unixtime - first_element_unixtime > timedelta(seconds=30) or end_of_log) and len(self.queue) > 0:
                print("{time:<22}; {change_type:>8}; {action:>10}; {folderID:>15}; {device_name:>8}; {data_type:>7}; {file:>5}".format(**self.queue[0]))
                self.queue.pop(0)


    def convert_time(self, input_time):
        #print(input_time)
        input_expression = r"(^[0-9-]{10}T[0-9:]{8}).{1,10}(\+[0-9]{2}):([0-9]{2})"
        output_expression = r"\g<1>\g<2>\g<3>"
        return re.sub(input_expression, output_expression, input_time)




def default_path():
    win_path = r"%LOCALAPPDATA%\Syncthing"
    mac_path = "$HOME/Library/Application Support/Syncthing"
    linux_path = "$HOME/.config/syncthing"

    os = platform.system()
    if os == "Windows":
        return win_path
    elif os == "Darwin":
        return mac_path
    elif os == "Linux":
        return linux_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Bitte gebe einen Pfad zu dem Ordner mit den Log-Dateien an.", type=str, default=os.path.expandvars(default_path()))
    parser.add_argument("--from", type=int, default="20000101")
    parser.add_argument("--to", type=int, default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--name", type=str, default=None, help="Nach gesyncter Datei filtern mit Regular expression (Hilfe dazu auf: https://docs.python.org/3/library/re.html#regular-expression-syntax)")
    parser.add_argument("--action", type=str, default=None, help="Nach Aktion filtern mit Regular expression (Hilfe dazu auf: https://docs.python.org/3/library/re.html#regular-expression-syntax)")
    parser.add_argument("--stats")

    args = parser.parse_args()
    viewer = log_viewer()
    viewer.read(args.path, getattr(args, "from"), getattr(args, "to"), getattr(args, "name"), getattr(args, "action"))
    viewer.stats()
    if viewer.counter == 0:
        sys.exit(1)
