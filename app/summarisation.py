from transformers import pipeline, BartForConditionalGeneration, BartTokenizer

class TextSummarizer:
    def __init__(self):
        # Load pretrained BART model for summarization
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
    def generate_summary(self, text, max_length=150, min_length=30):
        """
        Generate a summary of the input text
        
        Args:
            text (str): Input text to summarize
            max_length (int): Maximum length of the summary
            min_length (int): Minimum length of the summary
            
        Returns:
            str: Generated summary
        """
        summary = self.summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        return summary[0]['summary_text']