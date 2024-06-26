"""
Generate metrics given cleaned team data.

Usage:
    get_metrics (-i <input> | --input=<input>)
        [-o <output> | --output=<output>]
    get_metrics (-h | --help)

Options:
    -i <input> --input=<input>
        The cleaned team data in tsv format
    -o <output> --output=<output>
        The output directory to store metrics.tsv file
    -h --help
        Show this screen.
"""

import pandas as pd
from sklearn.metrics import cohen_kappa_score as ck
from sklearn.metrics import f1_score as f1
import itertools as it
from docopt import docopt

arguments = docopt(__doc__)

BIAS_VALUES = [
    'Biased against Palestine', 
    'Biased against Israel',
    'Biased against both Palestine and Israel',
    'Biased against others',
    'Unbiased',
    'Unclear',
    'Not Applicable',
]

def get_slice_by(df, s_type, batch, team, task, annotator = None):
    # ignore annotator filter if no annotator is given
    annotator_filter = (df.sheet_type == annotator) if annotator else True

    return df[(df.type == s_type) & (df.batch == batch) & (df.team_name == team) & (df.task == task) & (annotator_filter)].reset_index(drop=True)

def get_annotator_details(pair):
    if 'sheet_type' in pair[0]:
        return pair[0]['sheet_type'], pair[1]['sheet_type']
    else:
        return None, None

def replace_labels(series, from_labels, to_label):
    for f_label in from_labels:
        series.replace(f_label, to_label, inplace=True)
    return series

def to_bias_grp_else_series(series):
    x = replace_labels(series.copy(), ['Unclear', 'Not Applicable'], 'Un/NA')
    return replace_labels(x.copy(), BIAS_VALUES[:4], 'Biased')

def get_cohens_kappa(series_1, series_2):
    return ck(series_1, series_2)

def get_accuracy(series_1, series_2):
    return series_1.eq(series_2).sum() / series_1.shape[0]

def get_accuracy_else(series_1, series_2):
    x = replace_labels(series_1.copy(), ['Unclear', 'Not Applicable'], 'Un/NA')
    y = replace_labels(series_2.copy(), ['Unclear', 'Not Applicable'], 'Un/NA')

    return get_accuracy(x, y)

def get_accuracy_bias_grp(series_1, series_2):
    x = to_bias_grp_else_series(series_1)
    y = to_bias_grp_else_series(series_2)

    return get_accuracy(x, y)

def get_fscore(series_1, series_2):
    return f1(series_1, series_2, average='macro')

def get_fscore_bias(series_1, series_2):
    x = to_bias_grp_else_series(series_1)
    y = to_bias_grp_else_series(series_2)
    return f1(x, y, average='micro', labels=['Biased'])

def get_fscore_prop(series_1, series_2):
    x = replace_labels(series_1.copy(), ['Unclear', 'Not Applicable'], 'Un/NA')
    y = replace_labels(series_2.copy(), ['Unclear', 'Not Applicable'], 'Un/NA')

    return f1(x, y, average='micro', labels=['Propaganda'])

def get_pair_bias_score(df, s_type, pair):
    annot_1, annot_2 = get_annotator_details(pair)
    team_1_data = get_slice_by(df, s_type, pair[0]['batch'], pair[0]['team_name'], 'Bias', annot_1)
    team_2_data = get_slice_by(df, s_type, pair[1]['batch'], pair[1]['team_name'], 'Bias', annot_2)

    if team_1_data.shape[0] == 0 or team_2_data.shape[0] == 0:
        return {}
    
    # get cohens kappa
    b_co_ka = get_cohens_kappa(team_1_data.label, team_2_data.label)
    # get bias accuracy - 1) exact 2) else 3) bias_grp + else
    b_accuracy = get_accuracy(team_1_data.label, team_2_data.label)
    # b_accuracy_else = get_accuracy_else(team_1_data.label, team_2_data.label)
    # b_accuracy_bias_grp_else = get_accuracy_bias_grp(team_1_data.label, team_2_data.label)
    # fscores
    b_fscore = get_fscore(team_1_data.label, team_2_data.label)
    b_only_fscore = get_fscore_bias(team_1_data.label, team_2_data.label)
    
    return {
        'bias_cohen_kappa': b_co_ka,
        'bias_accuracy': b_accuracy,
        'bias_macro_f1': b_fscore,
        'bias*_f1': b_only_fscore
    }

def get_pair_prop_score(df, s_type, pair):
    annot_1, annot_2 = get_annotator_details(pair)
    team_1_data = get_slice_by(df, s_type, pair[0]['batch'], pair[0]['team_name'], 'Propaganda', annot_1)
    team_2_data = get_slice_by(df, s_type, pair[1]['batch'], pair[1]['team_name'], 'Propaganda', annot_2)
    
    if team_1_data.shape[0] == 0 or team_2_data.shape[0] == 0:
        return {}
    
    # get cohens kappa
    p_co_ka = get_cohens_kappa(team_1_data.label, team_2_data.label)
    # get bias accuracy - 1) exact 2) else 3) bias_grp + else
    p_accuracy = get_accuracy(team_1_data.label, team_2_data.label)
    # fscores
    p_fscore = get_fscore(team_1_data.label, team_2_data.label)
    p_only_fscore = get_fscore_prop(team_1_data.label, team_2_data.label)
    
    return {
        'propaganda_cohen_kappa': p_co_ka,
        'propaganda_accuracy': p_accuracy,
        'propaganda_macro_f1': p_fscore,
        'propaganda_f1': p_only_fscore
    }

def get_team_main_metrics(df):
    # get unique team-batch pairs from MAIN
    unique_team_batch = df[df.type == 'MAIN'][['team_name', 'batch']].drop_duplicates()
    # unique pairs across teams
    pairs = it.permutations(unique_team_batch.to_dict('records'), 2)

    pair_scores = []
    for pair in pairs:
        if pair[0]['batch'] != pair[1]['batch']:
            continue
        print(pair)

        s_type = 'MAIN'
        
        pair_details = {
            's_type': s_type, 
            'batch': pair[0]['batch'], 
            'team_1': pair[0]['team_name'], 
            'team_2': pair[1]['team_name']
        }
        
        bias_scores = get_pair_bias_score(df, s_type, pair)

        prop_scores = get_pair_prop_score(df, s_type, pair)
        
        pair_scores.append({**pair_details, **bias_scores, **prop_scores})
        
    pair_df = pd.DataFrame(pair_scores)
    pair_df['metrics'] = 'across_team'
    
    team_avgs = pair_df.groupby(['s_type', 'team_1']).mean(numeric_only=True).reset_index()
    team_avgs['metrics'] = 'across_team_avg'
    
    return pd.concat([pair_df, team_avgs])

def get_team_iaa_metrics(df):
    unique_team_batch = df[df['type'] == 'IAA'][['team_name', 'batch', 'sheet_type']].drop_duplicates()
    # unique pairs across teams
    pairs = it.permutations(unique_team_batch.to_dict('records'), 2)
    pair_scores = []
    for pair in pairs:
        if pair[0]['batch'] != pair[1]['batch']:
            continue
        print(pair)
        
        if pair[0]['team_name'] != pair[1]['team_name']:
            metric = 'across_team'
        else:
            metric = 'within_team'

        s_type = 'IAA'
        
        pair_details = {
            's_type': s_type, 
            'metrics': metric,
            'batch': pair[0]['batch'], 
            'team_1': pair[0]['team_name'], 
            'annot_1': pair[0]['sheet_type'], 
            'team_2': pair[1]['team_name'],
            'annot_2': pair[1]['sheet_type']
        }
        bias_scores = get_pair_bias_score(df, s_type, pair)

        prop_scores = get_pair_prop_score(df, s_type, pair)
        
        pair_scores.append({**pair_details, **bias_scores, **prop_scores})

    
    return pd.DataFrame(pair_scores)

def get_within_team_avgs(iaa_pair_df):
    in_team_df = iaa_pair_df[iaa_pair_df.team_2 == iaa_pair_df.team_1]
    in_team_avgs = in_team_df.groupby(['s_type', 'team_1']).mean(numeric_only=True).reset_index()
    in_team_avgs['metrics'] = 'within_team_avg'
    return in_team_avgs

def get_across_team_avgs(iaa_pair_df):
    across_team_df = iaa_pair_df[iaa_pair_df.team_2 != iaa_pair_df.team_1]
    across_team_avgs = across_team_df.groupby(['s_type', 'team_1']).mean(numeric_only=True).reset_index()
    across_team_avgs['metrics'] = 'across_team_avg'
    
    return across_team_avgs

if __name__ == '__main__':
    df = pd.read_csv(arguments['--input'], sep='\t')
    
    # team metrics, MAIN
    team_df = get_team_main_metrics(df)
    
    # annotator metricS, IAA
    iaa_pair_df = get_team_iaa_metrics(df)
    
    # team averages
    in_team_avgs = get_within_team_avgs(iaa_pair_df)
    across_team_avgs = get_across_team_avgs(iaa_pair_df)
    
    # combining above metrics
    annotator_df = pd.concat([iaa_pair_df, in_team_avgs, across_team_avgs])
    annotator_df = pd.concat([team_df, annotator_df]).reset_index(drop=True)
    
    annotator_df.to_csv(f"{arguments['--output']}/metrics.tsv", sep='\t', index=False)