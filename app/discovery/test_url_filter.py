from url_filter import URLFilter

f = URLFilter()

test_urls = [

    "http://www.tn.gov.in",

    "https://www.tn.gov.in/",

    "https://www.tn.gov.in#main",

    "mailto:test@test.com",

    "javascript:void(0)",

    "https://www.facebook.com",

    "https://www.tn.gov.in/login",

    "https://www.tn.gov.in/about_tn.php"

]

for url in test_urls:

    print("=" * 50)
    print(url)

    print("Normalized :", f.normalize(url))
    print("Valid :", f.is_valid(url))