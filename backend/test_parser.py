from parser_spacy import parse_profile

text = """
I am a 20 year old engineering student from Karnataka.
My family income is 2.5 lakh per year.
"""

profile = parse_profile(text)

print(profile)