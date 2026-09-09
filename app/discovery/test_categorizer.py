from pprint import pprint

from categorizer import Categorizer

urls = [

    "https://pmkisan.gov.in",

    "https://uidai.gov.in",

    "https://pmjay.gov.in",

    "https://www.epfindia.gov.in",

    "https://cbse.gov.in",

    "https://transport.tn.gov.in",

    "https://www.india.gov.in/my-government/schemes"
]

cat = Categorizer()

result = cat.categorize(urls)

pprint(result)