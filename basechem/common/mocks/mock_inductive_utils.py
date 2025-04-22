from rdkit import Chem

from basechem.common.constants import (
    IB_EFFLUX,
    IB_HLM,
    IB_KSOL,
    IB_LOGD,
    IB_PERM,
    IB_RLM,
)


def mock_get_ib_predictions(input_file, models, images=True):
    """
    Mock for `get_ib_predictions` to use in all test cases except those in `test_inductive_utils.py`
    """
    interp_image = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=="
    probs_image = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=="

    suppl = Chem.SDMolSupplier(input_file)
    return_data = {}
    for model in models:
        return_data[model] = []
        for mol in suppl:
            if model == IB_RLM:
                compound_data = {
                    "name": mol.GetProp("_Name"),
                    "prediction": "54.04",
                    "measured": "",
                    "out_of_domain": "True",
                    "latest_data_date": "2022-11-25",
                    "model_version": "2.0.0",
                    "interp_image": "",
                    "probs_image": "",
                    "probs_list": [0.049, 0.051, 0.9],
                }
                if images:
                    compound_data["interp_image"] = interp_image
                    compound_data["probs_image"] = probs_image
                return_data[model].append(compound_data)
            if model == IB_HLM:
                compound_data = {
                    "name": mol.GetProp("_Name"),
                    "prediction": "20.53",
                    "measured": "",
                    "out_of_domain": "True",
                    "latest_data_date": "2022-11-25",
                    "model_version": "2.0.0",
                    "interp_image": "",
                    "probs_image": "",
                    "probs_list": [0.2, 0.4, 0.4],
                }
                if images:
                    compound_data["interp_image"] = interp_image
                    compound_data["probs_image"] = probs_image
                return_data[model].append(compound_data)

            if model == IB_LOGD:
                compound_data = {
                    "name": mol.GetProp("_Name"),
                    "prediction": "2.30",
                    "measured": "2.22",
                    "out_of_domain": "",
                    "latest_data_date": "2022-11-25",
                    "model_version": "2.0.0",
                    "interp_image": "",
                    "probs_image": "",
                    "probs_list": [],
                }
                return_data[model].append(compound_data)

            if model == IB_EFFLUX:
                compound_data = {
                    "name": mol.GetProp("_Name"),
                    "prediction": "0.5",
                    "measured": "",
                    "out_of_domain": "False",
                    "latest_data_date": "2024-01-01",
                    "model_version": "1.1.0",
                    "interp_image": "",
                    "probs_image": "",
                    "probs_list": [0.99, 0.003, 0.0008],
                }
                if images:
                    compound_data["interp_image"] = interp_image
                    compound_data["probs_image"] = probs_image
                return_data[model].append(compound_data)

            if model == IB_PERM:
                compound_data = {
                    "name": mol.GetProp("_Name"),
                    "prediction": "0.12",
                    "measured": "",
                    "out_of_domain": "False",
                    "latest_data_date": "2024-01-01",
                    "model_version": "1.0.0",
                    "interp_image": "",
                    "probs_image": "",
                    "probs_list": [0.680, 0.086, 0.233],
                }
                if images:
                    compound_data["interp_image"] = interp_image
                    compound_data["probs_image"] = probs_image
                return_data[model].append(compound_data)

            if model == IB_KSOL:
                compound_data = {
                    "name": mol.GetProp("_Name"),
                    "prediction": "6.5",
                    "measured": "",
                    "out_of_domain": "True",
                    "latest_data_date": "2024-10-29",
                    "model_version": "1.0.0",
                    "interp_image": "",
                    "probs_image": "",
                    "probs_list": [0.586, 0.311, 0.101],
                }
                if images:
                    compound_data["interp_image"] = interp_image
                    compound_data["probs_image"] = probs_image
                return_data[model].append(compound_data)

    return return_data


def mock_put_data_to_ib(input_file, model):
    """
    Mock for `put_data_to_ib` to use in all test cases
    Does nothing since we don't want to PUT any data
    """
    return
