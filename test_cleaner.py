from app.utils.text_cleaner import clean_text

sample = """
      Welcome

        to

   Anna University!!!!



AI     Lab.
"""

print(clean_text(sample))