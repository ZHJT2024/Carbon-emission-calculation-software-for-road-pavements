import csv
import json
import os
import unittest

try:
    from .fun import (
        calc_LQ_A1,
        calc_LQ_A2,
        calc_LQ_A3,
        calc_LQ_B1,
        calc_LQ_B2,
        calc_JC_A1,
        calc_JC_A2,
        calc_JC_B2,
        calc_GNC_A1,
        calc_GNC_A2,
        calc_D1,
        calc_D2,
    )
except ImportError:
    from fun import (  # type: ignore
        calc_LQ_A1,
        calc_LQ_A2,
        calc_LQ_A3,
        calc_LQ_B1,
        calc_LQ_B2,
        calc_JC_A1,
        calc_JC_A2,
        calc_JC_B2,
        calc_GNC_A1,
        calc_GNC_A2,
        calc_D1,
        calc_D2,
    )


class TestCarbonProjectScheme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.csv_dir = os.path.join(os.path.dirname(__file__), 'csvs')

    def test_calc_lq_components(self):
        csv_path = os.path.join(self.csv_dir, 'calc_lq_components.csv')
        with open(csv_path, newline='', encoding='utf-8') as fp:
            for row in csv.DictReader(fp):
                p_ysb = float(row['p_ysb'])
                f_jhl = float(row['f_jhl'])
                kl_values = json.loads(row['kl_values'])
                a_lqmh = float(row['a_lqmh'])
                a_lqhd = float(row['a_lqhd'])
                area = float(row['area'])
                ys_kl_values = json.loads(row['ys_kl_values'])
                a_yj_jhl = float(row['a_yj_jhl'])
                expected_a1 = float(row['expected_a1'])
                expected_a2 = float(row['expected_a2'])
                expected_a3 = float(row['expected_a3'])

                self.assertAlmostEqual(
                    calc_LQ_A1(p_ysb, f_jhl, kl_values, a_lqmh, a_lqhd, area),
                    expected_a1,
                    places=6,
                )
                self.assertAlmostEqual(
                    calc_LQ_A2(p_ysb, ys_kl_values, a_yj_jhl, a_lqmh, a_lqhd, area),
                    expected_a2,
                    places=6,
                )
                self.assertAlmostEqual(
                    calc_LQ_A3(a_lqmh, a_lqhd, area),
                    expected_a3,
                    places=6,
                )

    def test_calc_lq_construction_phases(self):
        csv_path = os.path.join(self.csv_dir, 'calc_lq_construction.csv')
        with open(csv_path, newline='', encoding='utf-8') as fp:
            for row in csv.DictReader(fp):
                a_lqmh = float(row['a_lqmh'])
                a_lqhd = float(row['a_lqhd'])
                area = float(row['area'])
                expected_b1 = float(row['expected_b1'])
                expected_b2 = float(row['expected_b2'])

                self.assertAlmostEqual(
                    calc_LQ_B1(a_lqmh, a_lqhd, area),
                    expected_b1,
                    places=6,
                )
                self.assertAlmostEqual(
                    calc_LQ_B2(a_lqmh, a_lqhd, area),
                    expected_b2,
                    places=6,
                )

    def test_calc_jc_formulas(self):
        csv_path = os.path.join(self.csv_dir, 'calc_jc_formulas.csv')
        with open(csv_path, newline='', encoding='utf-8') as fp:
            for row in csv.DictReader(fp):
                area = float(row['area'])
                a_jc = float(row['a_jc'])
                material_name = row['material_name']

                if row['f_jc']:
                    f_jc = float(row['f_jc'])
                    expected_a1 = float(row['expected_a1'])
                    self.assertAlmostEqual(
                        calc_JC_A1(f_jc, a_jc, area),
                        expected_a1,
                        places=6,
                    )

                if row['a_yj_jc']:
                    a_yj_jc = float(row['a_yj_jc'])
                    expected_a2 = float(row['expected_a2'])
                    self.assertAlmostEqual(
                        calc_JC_A2(a_yj_jc, a_jc, area),
                        expected_a2,
                        places=6,
                    )

                if row['expected_b2']:
                    expected_b2 = float(row['expected_b2'])
                    self.assertAlmostEqual(
                        calc_JC_B2(material_name, a_jc, area),
                        expected_b2,
                        places=6,
                    )

    def test_calc_gnc_layers(self):
        csv_path = os.path.join(self.csv_dir, 'calc_gnc_layers.csv')
        with open(csv_path, newline='', encoding='utf-8') as fp:
            for row in csv.DictReader(fp):
                area = float(row['area'])
                f_gnc = float(row['f_gnc'])
                a_gnc = float(row['a_gnc'])
                a_yj_gnc = float(row['a_yj_gnc'])
                unit = row['unit']
                expected_a1 = float(row['expected_a1'])
                expected_a2 = float(row['expected_a2'])

                self.assertAlmostEqual(
                    calc_GNC_A1(f_gnc, a_gnc, area, unit),
                    expected_a1,
                    places=6,
                )
                self.assertAlmostEqual(
                    calc_GNC_A2(a_yj_gnc, a_gnc, area, unit),
                    expected_a2,
                    places=6,
                )

    def test_calc_end_of_life(self):
        csv_path = os.path.join(self.csv_dir, 'calc_end_of_life.csv')
        with open(csv_path, newline='', encoding='utf-8') as fp:
            for row in csv.DictReader(fp):
                a_zhd = float(row['a_zhd'])
                area = float(row['area'])
                expected_d1 = float(row['expected_d1'])
                expected_d2 = float(row['expected_d2'])

                self.assertAlmostEqual(
                    calc_D1(a_zhd, area),
                    expected_d1,
                    places=6,
                )
                self.assertAlmostEqual(
                    calc_D2(a_zhd, area),
                    expected_d2,
                    places=6,
                )


if __name__ == '__main__':
    unittest.main()
