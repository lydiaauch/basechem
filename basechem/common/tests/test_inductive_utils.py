from django.core import mail
from django.test import tag

from basechem.common.constants import IB_HLM, IB_LOGD, IB_RLM
from basechem.common.inductive_utils import get_ib_predictions, put_data_to_ib
from basechem.common.mocks.mock_inductive_utils import mock_get_ib_predictions
from basechem.common.tests.base import BasechemNoMockTestCase


@tag("local", "inductive", "external")
class InductiveBioUtilsTestCase(BasechemNoMockTestCase):
    def test_get_ib_predictions(self):
        """
        Tests `get_ib_predictions` and tests that output of `mock_get_ib_predictions`
        tracks with `get_ib_predictions`
        """
        input_file = "basechem/main/tests/testdata/test_onecomp.sdf"

        with self.subTest("Rat, image"):
            result = get_ib_predictions(input_file, [IB_RLM])
            mock_result = mock_get_ib_predictions(input_file, [IB_RLM])

            self.assertEqual(len(result), len(mock_result))
            result = result[IB_RLM][0]
            mock_result = mock_result[IB_RLM][0]

            self.assertEqual(float, type(float(result["prediction"])))
            self.assertEqual(bool, type(bool(result["out_of_domain"])))
            self.assertTrue(len(result["interp_image"]) > 50)
            self.assertTrue(len(result["probs_image"]) > 50)

            # Check that the mock result has the correct format but not the same data
            self.assertEqual(mock_result.keys(), result.keys())
            for key in mock_result.keys():
                self.assertEqual(type(mock_result[key]), type(result[key]))
            self.assertTrue(len(mock_result["interp_image"]) > 50)
            self.assertTrue(len(mock_result["probs_image"]) > 50)

        with self.subTest("Two models, no image"):
            models = [IB_RLM, IB_HLM]
            result = get_ib_predictions(input_file, models, images=False)
            mock_result = mock_get_ib_predictions(input_file, models, images=False)

            self.assertEqual(len(result), 2)
            self.assertEqual(list(result.keys()), models)
            self.assertEqual(mock_result.keys(), result.keys())
            self.assertEqual(len(result[models[0]]), len(mock_result[models[0]]))

            for model, prediction in result.items():
                self.assertTrue(model in models)
                self.assertEqual(len(prediction), 1)
                for pred in prediction:
                    self.assertEqual(float, type(float(pred["prediction"])))
                    self.assertEqual(bool, type(bool(pred["out_of_domain"])))
                    self.assertEqual(pred["interp_image"], "")
                    self.assertEqual(pred["probs_image"], "")

            for model, prediction in mock_result.items():
                self.assertTrue(model in models)
                self.assertEqual(len(prediction), 1)
                for pred in prediction:
                    self.assertEqual(float, type(float(pred["prediction"])))
                    self.assertEqual(bool, type(bool(pred["out_of_domain"])))
                    self.assertEqual(pred["interp_image"], "")
                    self.assertEqual(pred["probs_image"], "")

        with self.subTest("logd"):
            result = get_ib_predictions(input_file, [IB_LOGD], images=False)
            mock_result = mock_get_ib_predictions(input_file, [IB_LOGD], images=False)

            self.assertEqual(len(result), len(mock_result))
            self.assertEqual(len(result), 1)
            result = result[IB_LOGD][0]
            mock_result = mock_result[IB_LOGD][0]

            self.assertEqual(float, type(float(result["prediction"])))
            self.assertEqual(mock_result.keys(), result.keys())
            for key in mock_result.keys():
                self.assertEqual(type(mock_result[key]), type(result[key]))

        with self.subTest("logd, multi-compound"):
            input_file = "basechem/main/tests/testdata/test_mmps_w_data.sdf"
            result = get_ib_predictions(input_file, [IB_LOGD], images=False)
            mock_result = mock_get_ib_predictions(input_file, [IB_LOGD], images=False)

            self.assertEqual(len(result), 1)
            self.assertEqual(mock_result.keys(), result.keys())
            self.assertEqual(len(result[IB_LOGD]), 14)
            self.assertEqual(len(result[IB_LOGD]), len(mock_result[IB_LOGD]))

            for model, prediction in result.items():
                self.assertEqual(model, IB_LOGD)
                self.assertEqual(len(prediction), 14)
                for pred in prediction:
                    self.assertEqual(float, type(float(pred["prediction"])))
                    self.assertEqual(bool, type(bool(pred["out_of_domain"])))
                    self.assertEqual(pred["interp_image"], "")
                    self.assertEqual(pred["probs_image"], "")

    def test_put_data_to_ib(self):
        """
        Tests `put_data_to_ib` to make sure no email is sent with
        empty data
        """
        self.assertEqual(len(mail.outbox), 0)
        input_file = "/tmp/empty.sdf"
        with open(input_file, "w") as f:
            pass

        put_data_to_ib(input_file, "generic_logd")

        self.assertEqual(len(mail.outbox), 0)
