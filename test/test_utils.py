import os
import os.path
import unittest
import json

from cmdstanpy import TMPDIR
from cmdstanpy.lib import StanData
from cmdstanpy.utils import cmdstan_path, set_cmdstan_path, validate_cmdstan_path, check_csv


datafiles_path = os.path.join('test', 'data')

rdump = ('''N <- 10
y <- c(0, 1, 0, 0, 0, 0, 0, 0, 0, 1)
''')


class CmdStanPathTest(unittest.TestCase):
    def test_default_path(self):
        abs_rel_path = os.path.expanduser(os.path.join('~', '.cmdstanpy', 'cmdstan'))
        self.assertEqual(abs_rel_path, cmdstan_path())

    def test_set_path(self):
        abs_rel_path = os.path.expanduser(os.path.join('~', '.cmdstanpy', 'cmdstan'))
        self.assertEqual(abs_rel_path, cmdstan_path())
        install_version = os.path.expanduser(
            os.path.join('~', '.cmdstanpy', 'cmdstan-2.19.1'))
        set_cmdstan_path(install_version)
        self.assertEqual(install_version, cmdstan_path())

    def test_validate_path(self):
        abs_rel_path = os.path.expanduser(os.path.join('~', '.cmdstanpy', 'cmdstan'))
        validate_cmdstan_path(abs_rel_path)
        path_foo = os.path.abspath(os.path.join('releases', 'foo'))
        with self.assertRaisesRegex(ValueError, 'no such CmdStan directory'):
            validate_cmdstan_path(path_foo)
        path_test = os.path.abspath('test')
        with self.assertRaisesRegex(ValueError, 'no CmdStan binaries'):
            validate_cmdstan_path(path_test)



class StanDataTest(unittest.TestCase):
    def test_standata_existing(self):
        rdump = os.path.join(datafiles_path, 'bernoulli.data.R')
        standata = StanData(rdump)
        self.assertEqual(standata.data_file, rdump)

    def test_standata_new(self):
        json_file = os.path.join(datafiles_path, 'bernoulli.data.json')
        with open(json_file, 'r') as fd:
            dict = json.load(fd)
        rdump_file = os.path.join(TMPDIR, 'bernoulli.data2.R')
        standata = StanData(rdump_file)
        standata.write_rdump(dict)
        with open(rdump_file, 'r') as myfile:
            new_data = myfile.read()
        self.assertEqual(rdump, new_data)

    def test_standata_bad(self):
        with self.assertRaises(Exception):
            standata = StanData('/no/such/path')


class ReadStanCsvTest(unittest.TestCase):
    def test_check_csv_1(self):
        csv_good = os.path.join(datafiles_path, 'bernoulli_output_1.csv')
        dict = check_csv(csv_good)
        self.assertEqual('bernoulli_model', dict['model'])
        self.assertEqual('10', dict['num_samples'])
        self.assertFalse('save_warmup' in dict)
        self.assertEqual(10, dict['draws'])
        self.assertEqual(8, len(dict['column_names']))

    def test_check_csv_2(self):
        csv_bad = os.path.join(datafiles_path, 'no_such_file.csv')
        with self.assertRaises(Exception):
            dict = check_csv(csv_bad)

    def test_check_csv_3(self):
        csv_bad = os.path.join(datafiles_path, 'output_bad_cols.csv')
        with self.assertRaisesRegex(Exception, '8 items'):
            dict = check_csv(csv_bad)

    def test_check_csv_4(self):
        csv_bad = os.path.join(datafiles_path, 'output_bad_rows.csv')
        with self.assertRaisesRegex(Exception, 'found 9'):
            dict = check_csv(csv_bad)

    def test_check_csv_metric_1(self):
        csv_bad = os.path.join(datafiles_path, 'output_bad_metric_1.csv')
        with self.assertRaisesRegex(Exception,
                                   'expecting metric'):
            dict = check_csv(csv_bad)

    def test_check_csv_metric_2(self):
        csv_bad = os.path.join(datafiles_path, 'output_bad_metric_2.csv')
        with self.assertRaisesRegex(Exception, 'invalid stepsize'):
            dict = check_csv(csv_bad)

    def test_check_csv_metric_3(self):
        csv_bad = os.path.join(datafiles_path, 'output_bad_metric_3.csv')
        with self.assertRaisesRegex(Exception,
                                    'invalid or missing mass matrix specification'):
            dict = check_csv(csv_bad)

    def test_check_csv_metric_3(self):
        csv_bad = os.path.join(datafiles_path, 'output_bad_metric_4.csv')
        with self.assertRaisesRegex(Exception,
                                    'invalid or missing mass matrix specification'):
            dict = check_csv(csv_bad)


if __name__ == '__main__':
    unittest.main()
