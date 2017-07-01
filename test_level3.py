# -*- coding: utf-8 -*-
import unittest
import level3
from datetime import datetime as dt


class MyTest(unittest.TestCase):
    cases = [{

        "input":
            {
                "reviewee_id": "a",
                "lang": "ruby",
                "run_date": "2017-04-26",
                "deadline": "2017-04-28",
                "json_path": "data/level3.json"

            },
        "output":
            {
                "teammate_candidates": ["d", "e", "f", "g"],
                "otherteam_candidates": ["j", "q", "s"],
                "last_candidates": ["d", "e", "f", "g", "j", "q", "s"],
            }

    },
        {
            "input":
                {
                    "reviewee_id": "a",
                    "lang": "javascript",
                    "run_date": "2017-04-26",
                    "deadline": "2017-04-28",
                    "json_path": "data/level3.json"

                },
            "output":
                {
                    "teammate_candidates": ["d"],
                    "otherteam_candidates": ["j", "n", "o", "p"],
                    "last_candidates": ["d", "j", "n", "o", "p"]
                }
        },
        {
            "input":
                {
                    "reviewee_id": "a",
                    "lang": "go",
                    "run_date": "2017-04-26",
                    "deadline": "2017-04-28",
                    "json_path": "data/level3.json"

                },
            "output":
                {
                    "teammate_candidates": ["N/A"],
                    "otherteam_candidates": ["h", "j", "k", "l", "m"],
                    "last_candidates": ["h", "j", "k", "l", "m"],
                }
        },
        {
            "input":
                {
                    "reviewee_id": "a",
                    "lang": "go",
                    "run_date": "2017-05-02",
                    "deadline": "2017-05-04",
                    "json_path": "data/level3.json"

                },
            "output": "SystemExit"
        }

    ]
    data = level3.get_data_from_jsonpath("data/level3.json")

    def test_get_xth_next_business_day_of_date_str(self):
        data = level3.get_data_from_jsonpath("data/level3.json")
        next_date = level3.get_xth_next_business_day_of_date_str("2017-05-02", 2, data)
        expected_date_str = dt.strptime("2017-05-09", "%Y-%m-%d")
        self.assertEqual(next_date, expected_date_str)

        next_date = level3.get_xth_next_business_day_of_date_str("2017-05-02", -2, data)
        expected_date_str = dt.strptime("2017-04-28", "%Y-%m-%d")
        self.assertEqual(next_date, expected_date_str)

    def test_get_deadline_validity(self):
        earliest_datetime = dt.strptime("2017-05-09", "%Y-%m-%d")
        self.assertEqual(level3.get_deadline_validity(earliest_datetime, "2017-05-08", self.data), False)
        self.assertEqual(level3.get_deadline_validity(earliest_datetime, "2017-05-10", self.data), True)

        earliest_datetime = dt.strptime("2017-04-28", "%Y-%m-%d")
        self.assertEqual(level3.get_deadline_validity(earliest_datetime, "2017-04-26", self.data), False)
        self.assertEqual(level3.get_deadline_validity(earliest_datetime, "2017-04-29", self.data), False)

    def test_get_vacation_filtered_candidates(self):
        candidate_engineers = self.data["engineers"]
        candidate_engineers_ids = map(lambda x: x["id"], candidate_engineers)
        filtered_candidates = level3.get_vacation_filtered_candidates(self.data, candidate_engineers, "2017-04-28")
        filtered_candidates_ids = map(lambda x: x["id"], filtered_candidates)

        removed_ids = set(candidate_engineers_ids) - set(filtered_candidates_ids)
        self.assertEqual(set(['b', 'i']), removed_ids)

    def test_main_exit(self):
        inputs = self.cases[3]["input"]
        with self.assertRaises(SystemExit) as cm:
            level3.main([self, inputs["reviewee_id"], inputs["json_path"], \
                         inputs["lang"], inputs["deadline"]], "2017-04-26")
        self.assertEqual(cm.exception.code, 1)

    def test_main(self):
        for case in self.cases[:3]:
            inputs = case["input"]
            output = level3.main([self, inputs["reviewee_id"], inputs["json_path"], \
                                  inputs["lang"], inputs["deadline"]], "2017-04-26")
            output_list = output.split(',')

            # check duplicates of reviewer
            s = set()
            duplicates = len(list(set([x for x in output_list if (x in s and x != "N/A") or s.add(x)])))
            self.assertEqual(duplicates, 0)

            # check output is in "x,x,x"
            self.assertEqual(type(output), unicode)
            self.assertEqual(len(output_list), 3)

            # test whether reviewer is in expected output.
            output_dict = dict(zip(["teammate_reviewer", "otherteam_recviewer", "last_reviewer"], output_list))
            self.assertIn(output_dict["teammate_reviewer"], case["output"]["teammate_candidates"])
            self.assertIn(output_dict["otherteam_recviewer"], case["output"]["otherteam_candidates"])
            self.assertIn(output_dict["last_reviewer"], case["output"]["last_candidates"])


if __name__ == "__main__":
    unittest.main()