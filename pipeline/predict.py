#!/usr/bin/python
 # -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import pickle


def clean_json(df):
    """ Summary: Take in a pandas DataFrame from json and prepare it for mod        el prediction.
        INPUT: Pandas DataFrame: DataFrame of imported json.
        OUTPUT: Pandas DataFrame: DataFrame after it has been prepared for t                he model.
    """

    df.drop('description', inplace=True, axis=1)

    # Fraud defined as anything that isn't premium
    #df['fraud'] = np.where(df.acct_type == "premium", False, True)

    # Strip out the value after the final period
    df['email_domain_ending'] = df['email_domain'].apply(lambda x: x.split('.')[-1].lower().strip() )

    # Required step: clean domain ending for future data
    #temp = pd.crosstab(df['email_domain_ending'], df['fraud'])

    #temp.rename(columns={False:"FALSE", True:"TRUE"}, inplace=True)
    temp = df.copy(deep=True)
    if "TRUE" not in temp.columns:
        temp["TRUE"] = 0
    if "FALSE" not in temp.columns:
        temp["FALSE"] = 0
    temp.reset_index(inplace=True)
    temp['email_domain_ending'] = np.where(temp["FALSE"] + temp["TRUE"] <= 10, 'other', temp.email_domain_ending)
    acceptable_domain_endings = set(temp['email_domain_ending'])

    df['email_domain_ending'] = df['email_domain_ending'].apply(lambda x: x if x in acceptable_domain_endings else "other")

    # Whether or not the user input a venue_name
    df['has_venue'] = np.where(pd.isnull(df.venue_name), False, True)

    # Remove unused columns
    df = df[['body_length', 'email_domain_ending', 'user_age', 'has_venue']]

    # Create dummies for email_domain_ending
    df_domain = pd.get_dummies(df['email_domain_ending'])
    frames = [df, df_domain]
    df = pd.concat(frames, axis=1)
    df = df.drop('email_domain_ending', axis=1)

    # Ensure the columns match those the model expects.
    #   This is primarily for dummies not being present. 
    cols = pickle.load(open("models/model_columns.pkl"))
    for col in cols[cols != 'fraud']:
        if col not in df.columns:
            df[col] = 0

    return df


def get_json(json_path = "test_script_examples.json"):
    """ Summary: Read in json file with test examples to predict."
        INPUT: string: Path to json file to read in.
        OUTPUT: Pandas DataFrame: DataFrame of the raw json.
    """

    return pd.read_json(json_path)


def get_model(model_path = "models/model.pkl"):
    """ Summary: Load a pickled sklearn model.
        INPUT: string: Path to pickled model.
        OUTPUT: Sklearn Model: Model we will use for prediction.
    """
    return pickle.load(open(model_path))


def get_predictions(df, model):
    """ Summary: Produce predictions with probabilties of each label.
        INPUT: Pandas DataFrame: DataFrame of prepared test examples to evaluate.
               Sklearn model: Model to perform predictions.
        OUTPUT: Predicted probabilties of each class for each example read. 
    """
    return model.predict_proba(df)



if __name__ == "__main__":
    test_df = get_json()
    test_df = clean_json(test_df)
    #model = get_model()
    #predictions = get_predictions(test_df, model)
    #print predictions

