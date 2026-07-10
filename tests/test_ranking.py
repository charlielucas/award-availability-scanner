import unittest

from award_availability.ranking import normalize_search_payload, rank_options


class RankingTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "data": [
                {
                    "id": "sample-1",
                    "route_id": "route-1",
                    "date": "2030-04-12",
                    "program": "Example Rewards",
                    "currency": "USD",
                    "cabins": {
                        "business": {"available": True, "miles": 62000, "direct": True, "seats": 2, "taxes": 212.5},
                        "economy": {"available": True, "miles": 26000, "direct": True, "seats": 4, "taxes": 75},
                    },
                },
                {
                    "id": "sample-2",
                    "route_id": "route-2",
                    "date": "2030-04-13",
                    "program": "Sample Miles",
                    "currency": "USD",
                    "cabins": {
                        "business": {"available": True, "miles": 58000, "direct": False, "seats": 1, "taxes": 163},
                        "first": {"available": False, "miles": 90000, "direct": False},
                    },
                },
            ]
        }

    def test_normalizes_available_cabins(self):
        options = normalize_search_payload(self.payload, "aaa", "bbb")
        self.assertEqual(3, len(options))
        self.assertEqual("AAA", options[0].origin)
        self.assertEqual("business", options[0].cabin)

    def test_ranks_by_miles_and_filters_nonstop(self):
        options = normalize_search_payload(self.payload, "AAA", "BBB")
        ranked = rank_options(options, max_miles=70000, direct_only=True)
        self.assertEqual([26000, 62000], [option.miles for option in ranked])
        self.assertTrue(all(option.direct for option in ranked))

    def test_skips_invalid_mileage(self):
        self.payload["data"][0]["cabins"]["business"]["miles"] = 0
        options = normalize_search_payload(self.payload, "AAA", "BBB")
        self.assertEqual(2, len(options))
