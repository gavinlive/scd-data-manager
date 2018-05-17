import os, sys

import pydicom as pyd
import matplotlib.pyplot as plt
import collections
import pandas as pd

PatientRecord = collections.namedtuple('PatientRecord', ['patient_id', 'image_folder', 'original_id', 'gender', 'age', 'pathology', 'all_scans', 'scans', 'scans_list', 'scans_total'])
PatientScans = collections.namedtuple('PatientScans', ['files', 'prefixes', 'suffixes', 'total_number'])
DataRecord = collections.namedtuple('DataRecord', ['dicom_path', 'contour_path'])

class DataManager(object):
    def __config__(self):
        self.path = '.'
        self.patient_info_path = self.path + '/scd_patientdata.csv'
        self.meta_data_path = self.path + '/scd_patientdata.csv'
        self.images_path = self.path + '/SCD_DeidentifiedImages/'
        self.segmentations_path = self.path + '/SCD_ManualContours/'
    def __init__(self):
        self.__config__()
        self.__load_patient_info()
        self._patients = next(os.walk(self.images_path))[1]
        print(self._patients)
        self.__get_patient_images()
        if(self.__verify_scan_sets()==True): print("verified all scan sets")
        if(self.__verify_scan_numbers()==True): print("verified all scan numbers")


    def __import_contours(self, patient, suffixes, files):
        path = self.segmentations_path + patient + '/contours-manual/IRCCI-expert/'
        records_list=[]
        numbers_list = []
        for file in os.listdir(path):
            if file.endswith(".txt"):
                f=file.split("-")
                scan_number = int(f[2])
                f=f[3]
                if((f=="icontour") and (scan_number in suffixes)):
                    contour_filepath = path +'/' + file
                    indx = suffixes.index(scan_number)
                    dicom_filepath = files[indx]
                    records_list.append(DataRecord(dicom_filepath, contour_filepath))
                    numbers_list.append(scan_number)
        return records_list,numbers_list,len(records_list)

    def __load_patient_info(self):
        self.patient_info = pd.read_csv(self.patient_info_path)
    def __get_patient_info(self, patient):
        this = self.patient_info[self.patient_info['OriginalID']==patient].values.tolist()[0]
        print(this)
        cols = self.patient_info.columns.values.tolist()
        toget = ['Gender', 'Age', 'PathologyID', 'Pathology']
        toreturn=[]
        for t in toget:
            indx = cols.index(t)
            toreturn.append(this[indx])
        return toreturn

    def depre__import_contours(self):
        for patient in self._patients:
            path = self.segmentations_path + patient + '/contours-manual/IRCCI-expert/'
            records_list=[]
            numbers_list = []
            for file in os.listdir(path):
                if file.endswith(".txt"):
                    f=file.split("-")
                    scan_number = f[2]
                    f=f[3]
                    if((f=="icontour") and (scan_number in self.patient[patient].all_scans.suffixes)):
                        contour_filepath = path +'/' + file
                        indx = self.patient[patient].all_scans.suffixes.indx(scan_number)
                        dicom_filepath = self.patient[patient].all_scans.files[indx]
                        records_list.append(DataRecord(dicom_filepath, contour_filepath))
                        numbers_list.append(scan_number)
            self.patient[patient].scans=records_list
            self.patient[patient].scans_list=numbers_list
            self.patient[patient].scans_total = len(records_list)


    def __verify_scan_sets(self):
        for patient in self._patients:
            prefix_list = self.patient[patient].all_scans.prefixes
            b = [(x==1) for x in prefix_list]
            if False in b:
                print('Fault for patient: %s' % patient)
                return False
        return True
    def __verify_scan_numbers(self):
        for patient in self._patients:
            prefix_list = self.patient[patient].all_scans.suffixes
            b = [(prefix_list.count(x)==1) for x in prefix_list]
            if False in b:
                print('Fault for patient: %s' % patient)
                return False
        return True


    def __get_patient_images(self):
        self.patient = {}
        for patient in self._patients:
            #list_of_image_folders_for_patient = next(os.walk(self.images_path + patient))[1]
            #list_of_image_folders_for_patient_full_path = [self.images_path + patient + '/' + x for x in list_of_image_folders_for_patient]

            #self.patient[patient] = {"patient_id": patient, "images": list_of_image_folders_for_patient, "original_id": "",
            #"gender": "", "age": 0, "pathology": "" }


            def get_files(list_of_folders):
                file_list = []
                for folder in list_of_folders:
                    for file in os.listdir(folder):
                        if file.endswith(".dcm"):
                            file_list.append(folder +'/' + file)
                return file_list

            def get_prefix_suffix(files):
                prefixes = []
                suffixes = []
                for file in files:
                    f=file.split("-")
                    f=f[-2::]
                    f[1] = f[1].split(".")[0]
                    prefixes.append(int(f[0]))
                    suffixes.append(int(f[1]))
                return prefixes, suffixes

            files = get_files([self.images_path+patient+'/DICOM'])
            prefixes, suffixes = get_prefix_suffix(files)
            this_patient_scan_set = PatientScans(files, prefixes, suffixes, len(files))
            scans, scans_list, scans_total = self.__import_contours(patient, suffixes, files)
            gender, age, pathologyID, _ = self.__get_patient_info(patient)
            this_patient_record = PatientRecord(patient_id=patient, image_folder=self.images_path + patient, original_id="",
            gender=gender, age=age, pathology=pathologyID, all_scans=this_patient_scan_set, scans=scans, scans_list=scans_list, scans_total=scans_total)
            self.patient[patient] = this_patient_record

    def total_examples(self):
        count=0
        for patient in self._patients:
            count += self.patient[patient].scans_total
        return count

    def __call__(self, patient,scan_number):
        return self.patient[patient].all_scans.files[scan_number]

