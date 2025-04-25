import json
from typing import Any

json_file: dict[str, Any] = json.loads(open("knock_json_file.json").read())
all_domains = []

for domain, domain_item in json_file.items():
    if domain == "_meta":
        continue

    extras = []
    if domain_item.get('server') != "":
        extras.append("server: " + domain_item.get('server'))
    if str(domain_item.get('code')) != "":
        extras.append("code: " + str(domain_item.get('code')))

    extras_join = ", ".join(extras)
    extras_join = " - " + extras_join if extras_join != "" else ""
    all_domains.append(domain + extras_join)

all_domains.sort()

for domain in all_domains:
    print(domain)
