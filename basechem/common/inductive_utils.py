import requests
from django.conf import settings
from django.core.mail import mail_admins
from rdkit import Chem

from basechem.common.constants import ADMIN_FAILURE, ALL_IB_MODELS

###########################
### Request Predictions ###
###########################


def get_ib_predictions(
    input_file, models, images=True, version=settings.INDUCTIVE_VERSION
):
    """
    Send the given SDF file to the InductiveBio predict endpoint to generate predictions
    from the given models
    :param input_file: sdf file containing compounds of which to predict LM stability
    :param models: list of models to predict values from
    :param images: boolean for if images should be requested from the API
    :param version: either "latest" or "dev"
    :return: returns a list of dicts of the form
        {
        "name": str,
        "prediction": str(number),
        "measured": str(number) or "",
        "out_of_domain": str(bool),
        "latest_data_date": "YYYY-MM-DD",
        "model_version": str,
        "interp_image": str,
        "probs_image": str,
        "probs_list": list,
    }
    """
    url = "https://api.inductive.bio/0.1/properties/predict_multi_model"
    headers = {
        "X-API-KEY": settings.INDUCTIVE_API_KEY,
        "X-CUSTOMER-ID": settings.INDUCTIVE_CUSTOMER_ID,
    }

    if any(model not in ALL_IB_MODELS for model in models):
        admin_email_message = (
            f"One of {models} is not recognized by the InductiveBio API"
        )
        mail_admins(ADMIN_FAILURE, admin_email_message)
        return {}

    models_arr = [{"model_id": model, "model_version": version} for model in models]

    with open(input_file) as f:
        sdf_text = f.read()

        suppl = Chem.SDMolSupplier(input_file)
        ids = [m.GetProp("_Name") for m in suppl]

        body = {
            "model_requests": models_arr,
            "input_type": "SDF",
            "input": sdf_text,
            "molecule_ids": ids,
            "include_interpretations": images,
        }

        response = requests.post(url, json=body, headers=headers)
        response_dict = response.json()

        if not isinstance(response_dict, dict):
            response_dict = {}

        predictions = {}
        for response in response_dict.get("data", []):
            predictions[response.get("model_id")] = _parse_inductive_response(response)
        return predictions


def _parse_inductive_response(response_dict):
    """
    Parse the InductiveBio predict response into Basechem preferred format
    :param response_dict: json response from Inductive predict
    :return: parsed response dict of the form
        {
        "name": "",
        "model_version": "",
        "prediction": "InductiveBio API Error - LMs",
        "measured": "",
        "out_of_domain": "",
        "latest_data_date": "",
        "interp_image": "",
        "probs_image": "",
        "probs_list": [],
    }
    """
    response_preds = response_dict.get("predictions", {})
    if not response_preds:
        admin_email_message = f"InductiveBio API failed to generate predictions for {response_dict.get('molecule_id')} with a response of: \n {response_dict}"
        mail_admins(ADMIN_FAILURE, admin_email_message)
        return [
            {
                "name": "",
                "prediction": "InductiveBio API Error",
                "measured": "",
                "out_of_domain": "",
                "latest_data_date": "",
                "model_version": "",
                "interp_image": "",
                "probs_image": "",
                "probs_list": [],
            }
        ]

    predictions = []
    for cpd_data in response_preds:
        cpd_pred = {}
        cpd_pred["name"] = cpd_data["molecule_id"]
        cpd_pred["prediction"] = str(round(cpd_data["continuous_prediction"], 2))
        measured = cpd_data.get("measured_value", {}).get("continuous_value", "")
        if measured != "":
            measured = str(round(measured, 2))
        cpd_pred["measured"] = measured
        cpd_pred["out_of_domain"] = str(cpd_data["out_of_domain_flag"])

        # Get base64 images if they exist
        interp_image = ""
        probs_image = ""
        if cpd_data.get("interpretation_images"):
            interp_image = cpd_data.get("interpretation_images")[0]["image"]
            probs_image = cpd_data.get("interpretation_images")[1]["image"]
        cpd_pred["interp_image"] = interp_image
        cpd_pred["probs_image"] = probs_image
        cpd_pred["probs_list"] = cpd_data.get("predicted_probabilities", [])

        cpd_pred["latest_data_date"] = response_dict.get("latest_data_date", "")
        cpd_pred["model_version"] = response_dict.get("model_version", "")

        predictions.append(cpd_pred)

    return predictions


#######################
### POST Data to IB ###
#######################


def put_data_to_ib(new_data_filepath, model):
    """
    PUT given file with measured data to Inductive endpoint
    :param new_data_filepath: path to file containing new data
    """
    url = "https://api.inductive.bio/0.1/data/sdf_upload"
    headers = {
        "X-API-KEY": settings.INDUCTIVE_API_KEY,
        "X-CUSTOMER-ID": settings.INDUCTIVE_CUSTOMER_ID,
    }

    if model not in ALL_IB_MODELS:
        admin_email_message = f"{model} is not recognized by the InductiveBio API"
        mail_admins(ADMIN_FAILURE, admin_email_message)
        return {}

    with open(new_data_filepath) as f:
        sdf_text = f.read()

        if sdf_text:
            data_body = {
                "data": sdf_text,
                "project_column": "project_code",
                "molecule_id_column": "molecule_id",
                "properties_dict": {
                    "measured_value": {
                        "date_column": "most_recent_date",
                        "model_ids": [f"{model}"],
                    }
                },
            }

            response = requests.put(url, json=data_body, headers=headers)
            r = response.json()
            if r.get("status") != "SUCCESS":
                admin_email_message = f"InductiveBio API failed to PUT new LogD data for the file: {new_data_filepath} with the response {r}"
                mail_admins(ADMIN_FAILURE, admin_email_message)
            elif r.get("status") == "SUCCESS":
                return "SUCCESS"
