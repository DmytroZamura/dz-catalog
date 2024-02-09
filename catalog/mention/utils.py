from django.template.defaultfilters import slugify
import re


def parse_hashtags(text):
    tags = re.findall(r"#(\w+)", text)
    return tags
    # return [i for i in text.split() if i.startswith("#")]

def parse_mentions(text):
    return [slugify(i) for i in text.split() if i.startswith("@")]