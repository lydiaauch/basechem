import datetime
from functools import reduce

import pandas as pd
from django.conf import settings
from django_q.tasks import fetch_group

from basechem.common.constants import *
from basechem.common.inductive_utils import get_ib_predictions
from basechem.main.constants import (
    ALL_PROPS,
    ALOGD,
    APKA,
    BPKA,
    EFFLUX,
    HLM,
    KSOL,
    PERMEABILITY,
    RLM,
    ROTATABLEBONDS,
)


def get_dtx_prop_name(prop):
    """
    Given a basechem property name, return the property name that Dotmatics expects
    :param prop: a string, the name of a property
    """
    if prop == ROTATABLEBONDS:
        return "RotBonds"
    elif prop == ALOGD:
        return "AlogD"
    elif prop == "dn_id":
        return "Compound ID"
    elif prop == "latest_logd_data_date":
        return "TrainingDataCutoff"
    elif prop == "logd_version":
        return "ModelVersion"
    else:
        return prop


def generate_dtx_lm_stability_csv(collection, lm_filepath):
    """
    Generates a csv file of lm stability predictions for the compounds in the collection
    that matches what the DTX "Activity Predictions Upload" script expects
    :param collection: the collection to generate properties for
    :param lm_filepath: path to the csv file to populate
    """
    sdf_filepath, _ = collection.get_sdf_file()
    ib_output = get_ib_predictions(sdf_filepath, ALL_IB_MODELS, False)

    df_list = []
    for model in ALL_IB_MODELS:
        model_df = pd.DataFrame.from_dict(ib_output[model])
        model_df["prob"] = model_df["probs_list"].apply(
            lambda x: max([float(i) for i in x], default="")
        )
        model_df = model_df.add_suffix(f"_{model}")
        model_df.rename(columns={f"name_{model}": "name"}, inplace=True)
        df_list.append(model_df)

    joint_df = reduce(lambda x, y: pd.merge(x, y, on="name", how="outer"), df_list)

    # Add constant columns
    joint_df["assay"] = "Inductive Bio GCNN"
    joint_df["prediction_date"] = datetime.datetime.today().strftime("%m/%d/%Y")
    # model_version and latest_data_date will be the same for all entries so can just take the first
    model_version = list(set(df_list[1][f"model_version_{IB_HLM}"]))[0]
    lm_data_date = list(set(df_list[1][f"latest_data_date_{IB_HLM}"]))[0]
    joint_df["model_version"] = f"{model_version}: {lm_data_date}"
    # blank column so the CSV matches the Dotmatics processing script
    joint_df["skip"] = ""

    # Add calculated columns
    joint_df["out_of_domain_flag"] = joint_df[f"out_of_domain_{IB_RLM}"].apply(
        lambda x: "out-of-domain" if x == "True" else ""
    )
    joint_df["pStable"] = joint_df[f"probs_list_{IB_HLM}"].apply(
        lambda x: f"{x[0]:.3f}"
    )

    rename = {
        f"prediction_{IB_APKA}": "C_aPKA",
        f"prediction_{IB_BPKA}": "C_bPKA",
        f"prediction_{IB_EFFLUX}": "C_EFFLUX",
        f"prob_{IB_EFFLUX}": "C_EFFLUX_PROB",
        f"prediction_{IB_PERM}": "C_PERMEABILITY",
        f"prob_{IB_PERM}": "C_PERMEABILITY_PROB",
        f"prediction_{IB_KSOL}": "C_KSOLUBILITY",
        f"prob_{IB_KSOL}": "C_KSOLUBILITY_PROB",
        f"prediction_{IB_RLM}": "prediction_rlm",
        f"prediction_{IB_HLM}": "prediction_hlm",
    }
    joint_df.rename(columns=rename, inplace=True)

    joint_df.to_csv(
        lm_filepath,
        columns=[
            "name",
            "assay",
            "skip",
            "skip",
            "skip",
            "out_of_domain_flag",
            "skip",
            "pStable",
            "skip",
            "skip",
            "prediction_date",
            "model_version",
            "prediction_hlm",
            "skip",
            "prediction_rlm",
            "skip",
            "C_aPKA",
            "C_bPKA",
            "C_EFFLUX",
            "C_EFFLUX_PROB",
            "C_PERMEABILITY",
            "C_PERMEABILITY_PROB",
            "C_KSOLUBILITY",
            "C_KSOLUBILITY_PROB",
        ],
        index=False,
    )


def generate_dtx_propcalc_csv(collection, props_filepath):
    """
    Generates a csv file of property values for the compounds in the collection
    :param collection: the collection to generate properties for
    :param props_filepath: path to the csv file to populate
    """
    props = ["dn_id"]
    props.extend(ALL_PROPS)
    props = [
        x for x in props if x not in [HLM, RLM, EFFLUX, PERMEABILITY, KSOL, APKA, BPKA]
    ]

    if not settings.INDUCTIVE_BIO_ENABLED:
        props.remove(ALOGD)
    collection.metadata["props_to_show"] = props
    collection.save()
    collection.propcalc_analysis()
    group_name = collection.get_propcalc_group_name()

    # Wait indefinitely until group returns
    tasks = fetch_group(group_name, failures=True, count=collection.compounds().count())
    prop_dict = collect_propcalc_results(tasks)

    df = pd.DataFrame.from_dict(prop_dict, orient="index")
    # Drop columns that aren't in the properties list
    cleaned_props = [prop.lower().replace(" ", "_") for prop in props]

    if settings.INDUCTIVE_BIO_ENABLED:
        df[ALOGD.lower()] = df["logd_prediction"]
        cleaned_props.extend(["logd_version", "latest_logd_data_date"])
        props.extend(["logd_version", "latest_logd_data_date"])
        # Convert date to expected DTX format dd/mm/yyyy
        df["latest_logd_data_date"] = pd.to_datetime(df["latest_logd_data_date"])
        df["latest_logd_data_date"] = df["latest_logd_data_date"].dt.strftime(
            "%m/%d/%Y"
        )

    drop_cols = [col for col in df.columns if col not in cleaned_props]
    df = df.drop(columns=drop_cols)

    # Rename the columns to match Dotmatics names and put them in the correct order
    new_col_names = {}
    new_col_order = []
    for prop in props:
        dtx_prop_name = get_dtx_prop_name(prop)
        new_col_names[prop.lower().replace(" ", "_")] = dtx_prop_name
        new_col_order.append(dtx_prop_name)

    df.rename(columns=new_col_names, inplace=True)
    df = df.reindex(columns=new_col_order)
    df.sort_values(by=["Compound ID"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.to_csv(props_filepath, index=False)


def collect_propcalc_results(tasks):
    """
    Helper for constructing propcalc results dictionary
    :return: dictionary of properties {compound_id: dict-of-properties}
    """
    results = {}
    for task in tasks:
        co_id = int(task.name.split("_")[1])
        results[co_id] = task.result

    return results
