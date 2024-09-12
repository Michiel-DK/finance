from bert_score import BERTScorer
from rouge import Rouge
from rouge_score import rouge_scorer

import pandas as pd

def scorer(original, summary):
    
    bert_scorer = BERTScorer(model_type='bert-base-uncased')
    bert_precision, bert_recall, bert_f1 = bert_scorer.score([original], [summary])
    
    return pd.DataFrame({'Precision':bert_precision, 'Recall':bert_recall, 'F1':bert_f1}).T
    
    

    
