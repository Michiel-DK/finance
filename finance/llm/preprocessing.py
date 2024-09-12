from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

class LexRankPreproc():
    def __init__(self, n_sentences:int = 50, language:str = "english"):
        self.n_sentences = n_sentences
        self.language = language

    def preprocess(self, text:str) -> list:
        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        summarizer = LexRankSummarizer()
        most_important_sents = summarizer(parser.document, sentences_count=self.n_sentences)
        return [str(sent) for sent in most_important_sents if str(sent)]