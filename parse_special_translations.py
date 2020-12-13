"""Extract translation strings from bsiconbox and table_ord_helper tags."""
import re
import sys

print('"""Auto-generated file with translations for bsiconbox and table_ord_helper tags."""')

bsiconbox_regex = re.compile("{% ?bsiconbox .*? \d+ (.*?) ?%}")
table_ord_helper_regex = re.compile('{% ?table_ord_helper (".*?") .*? ?%}')
items = []
for line in sys.stdin:
    items += bsiconbox_regex.findall(line)
    items += table_ord_helper_regex.findall(line)

for term in sorted(set(items)):
    print("_({})".format(term))
