import os
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer

class TextSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        # Load pretrained BART model for summarization
        self.model_name = model_name
        self.summarizer = pipeline("summarization", model=model_name)
        
        # For direct access to model and tokenizer (useful for handling longer texts)
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)
    
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
    
    def generate_summary_from_file(self, input_path, output_dir="output_summary"):
        """
        Generate a summary of a text file using BART model.
        
        Args:
            input_path (str): Path to input text file (from output_speech folder)
            output_dir (str): Directory to save the summary output
            
        Returns:
            tuple: (summary text, path to summary file)
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract filename without extension
        filename = os.path.basename(input_path).split('.')[0]
        output_path = os.path.join(output_dir, f"{filename}.txt")
        
        # Read the transcription file from output_speech
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Handle long texts by checking if it exceeds model's maximum length
        max_model_length = self.tokenizer.model_max_length
        
        if len(text.split()) > max_model_length:
            # Use direct model access to handle long text
            inputs = self.tokenizer(text, max_length=max_model_length, truncation=True, return_tensors="pt")
            
            summary_ids = self.model.generate(
                inputs["input_ids"],
                num_beams=4,
                min_length=30,
                max_length=150,
                early_stopping=True
            )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        else:
            # Use pipeline for normal length text
            summary = self.generate_summary(text)
        
        # Save summary to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return summary, output_path

# Create an instance to use
summarizer = TextSummarizer()

# For backward compatibility
generate_summary = summarizer.generate_summary

# New file-based function
generate_summary_from_file = summarizer.generate_summary_from_file