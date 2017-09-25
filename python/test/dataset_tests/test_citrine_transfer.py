import unittest

from dataset import Public

class TestPifFormation(unittest.TestCase):
    def test_form_url(self):
        dataset_id = "74df8927-89a2-4759-90a5-c787686f78a0"
        public = Public()
        dataset = public.get_dataset(dataset_id)
        transform = 0
        measurement = 0
        print("Number of processes: " + str(len(dataset.processes)))
        for process in dataset.processes:
            if process.process_type == 'measurement':
                measurement += 1
            if process.does_transform or process.process_type == 'create' or process.process_type == 'sectioning':
                transform += 1
        print("Measurement: " + str(measurement))
        print("Transform: " + str(transform))

