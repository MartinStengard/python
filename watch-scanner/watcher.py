import json
from typing import Any

from netaddr import IPNetwork, AddrFormatError


def is_valid_ip(address):
    try:
        IPNetwork(address)
        return True
    except (ValueError, AddrFormatError):
        return False


def get_value_if_key_exists(data_object, key):
    if key in data_object:
        return data_object.get(key)
    return ""


def add_item(key: str, prop: str, val: Any, container: dict[str, dict]):
    item = {}
    if key in container:
        item = container.get(key)

    item.update({prop: val})
    container.update({key: item})


def watch():
    # Load watch config file
    # Loop all hosts from nmap result
    #   For each hostname (multiple of the same) check against expected
    #   ports and flags in watch config
    # Loop all vulnerability flags
    #   For each flag (unique per "hostname" and "port") continue to
    #   loop the vulnerabilities that are stored in the property "items" as a list
    #     For each vulnerability check if it is expected as stated in watch config.
    # Return result

    watch_config: dict[str, dict] = json.loads(open("watch_config.json").read())
    nmap_object: dict[str, dict | list] = json.loads(open("nmap_result.json").read())
    nmap_flags: list[dict] = nmap_object.get("flags")

    difference = {}

    # Check current scan against watch configuration
    for current_nmap_ip, current_nmap_values in nmap_object.items():
        if not is_valid_ip(current_nmap_ip):
            continue

        # HOSTNAME AND PORT SECTION *****************
        current_nmap_item_hostnames: list = current_nmap_values.get("hostname")

        # Check expected hostname
        if not any(item in watch_config for item in current_nmap_item_hostnames):
            print(f"1 - {current_nmap_item_hostnames}"
                  f" - new hostname {current_nmap_item_hostnames} found")
            add_item("new_hostname", "hostnames_values", current_nmap_values, difference)
            # expected_new_items.append({"hostname": current_nmap_item_hostnames, "item": current_nmap_values})
            continue

        for current_nmap_port_object in current_nmap_values.get("ports", []):
            current_nmap_port = current_nmap_port_object.get("portid")
            current_nmap_service_name = get_value_if_key_exists(current_nmap_port_object.get("service"), "name")

            current_nmap_hostname = None
            for hostname in current_nmap_item_hostnames:
                if hostname in watch_config:
                    current_nmap_hostname = hostname
                    break

            # hostname:port
            key_current_host_port = str(current_nmap_hostname) + ":" + str(current_nmap_port)

            # Check expected port
            watch_hostname: dict[str, dict] = watch_config.get(current_nmap_hostname)
            if current_nmap_port not in watch_hostname:
                print(f"2 - {current_nmap_hostname} - new port {current_nmap_port} found")
                add_item(key_current_host_port, f"new_port_{current_nmap_port}", current_nmap_port_object, difference)
                # expected_new_items.append({"port": current_nmap_port_object})
                continue

            # Check expected service name
            watch_port: dict[str, dict | list] = watch_hostname.get(current_nmap_port)
            if current_nmap_service_name != watch_port.get("service_name"):
                print(f"3 - {current_nmap_hostname}:{current_nmap_port}"
                      f" - expected service name {watch_port.get('service_name')} "
                      f"changed to {current_nmap_service_name}")
                add_item(key_current_host_port, "changed_service_name", f"{watch_port.get('service_name')} -> "
                                                              f"{current_nmap_port_object}", difference)
                # expected_changed_items.append({"expected": watch_port.get('service_name'),
                #                                "changed": current_nmap_service_name})
                continue

            # FLAG SECTION ******************************
            # Check expected hostname flags
            watch_port_expected_flags: dict[str, dict | list] = watch_port.get("expected_flags")
            current_nmap_item_flags: dict = {}
            for item in nmap_flags:
                if item.get("ip") == current_nmap_ip and item.get("port") == current_nmap_port:
                    current_nmap_item_flags = item.get("items")
                    break

            # All expected flags missing in current scan (current scan have no flags)
            if len(watch_port_expected_flags) > 0 and len(current_nmap_item_flags) == 0:
                print(f"4 - {current_nmap_hostname}:{current_nmap_port} - expected flag object missing")
                # print(json.dumps(watch_port_expected_flags))
                add_item(key_current_host_port, "missing_flags", watch_port_expected_flags, difference)
                # expected_missing_items.append(watch_port_expected_flags)
                continue

            # No expected flags exist but current scan have flags
            if len(watch_port_expected_flags) == 0 and len(current_nmap_item_flags) > 0:
                print(f"5 - {current_nmap_hostname}:{current_nmap_port} - new flag object found")
                # print(json.dumps(current_nmap_item_flags))
                add_item(key_current_host_port, "new_flags", current_nmap_item_flags, difference)
                # expected_new_items.append(current_nmap_item_flags)
                continue

            # Expected flags exist AND current scan have flags, continue
            for current_flag_key, current_flag_value in current_nmap_item_flags.items():
                # Current flag key section is missing in expected flag keys sections
                # current_flag_key: nmap_vulners, security_headers, cookie_flags, cors
                if str(current_flag_key) not in watch_port_expected_flags:
                    print(f"6 - {current_nmap_hostname}:{current_nmap_port} {current_flag_key} - new flag found")
                    # print(json.dumps(current_flag_value))
                    add_item(key_current_host_port, f"new_flag_{current_flag_key}", current_flag_value, difference)
                    # expected_new_items.append({current_flag_key: current_flag_value})
                    continue

                #  www.example.se:80 nmap_vulners
                #  www.example.se:80 security_headers
                current_host_port_flag = current_nmap_hostname + ":" + current_nmap_port + " " + current_flag_key

                # nmap_vulners
                # security_headers
                key = current_flag_key.lower()

                watch_item = watch_port_expected_flags.get(key)

                # Check current scan flag key against expected flag keys
                match key:
                    case "nmap_vulners":
                        for current_item in current_flag_value:
                            current_item_name = current_item.get("name")
                            if current_item_name not in watch_item:
                                print(f"8 - {current_host_port_flag}: new nmap_vulner flag found => '{current_item_name}'")
                            else:
                                # Can I check for changed value? Looking for name value as key so probably not.
                                pass

                    case "security_headers":
                        for current_item in current_flag_value:
                            current_item_name = current_item.get("name")
                            if current_item_name not in watch_item:
                                # Current flag is missing in expected => new flag
                                current_found = []
                                if "message" in current_item:
                                    current_found.append("message: " + current_item.get("message"))
                                if "notes" in current_item:
                                    current_found.append("notes: " + ", ".join(current_item.get("notes")))
                                found = ", ".join(current_found)
                                print(f"9 - {current_host_port_flag}: new security header flag '{current_item_name}' found => '{found}'")
                            else:
                                # Current flag exists in expected, check value(s)
                                if "notes" in current_item:
                                    # watch_notes - list of expected notes found for the security header key
                                    watch_notes: [list] = watch_item.get(current_item_name)
                                    for note in current_item.get("notes"):
                                        if note not in watch_notes:
                                            print(f"10 - {current_host_port_flag}: new value for '{current_item_name}' => '{note}'")

                    case "cookie_flags":
                        for current_item in current_flag_value:
                            current_cookie_name = list(current_item.keys())[0]
                            current_cookie_value = current_item.get(current_cookie_name)

                            if current_cookie_name not in watch_item:
                                # Current flag is missing in expected => new cookie
                                print(f"11 - {current_host_port_flag}: new cookie '{current_cookie_name}' found => '{current_cookie_value}'")
                            else:
                                # Current flag exists in expected, check value(s)
                                if current_cookie_value != watch_item.get(current_cookie_name):
                                    print(f"12 - {current_host_port_flag}: cookie '{current_cookie_name}' changed => '{current_cookie_value}'")

                    case "cors":
                        for current_item in current_flag_value:
                            current_cors_name = list(current_item.keys())[0]
                            current_cors_value = current_item.get(current_cors_name)

                            if current_cors_name not in watch_item:
                                # Current flag is missing in expected => new cookie
                                print(
                                    f"11 - {current_host_port_flag}: new cors flag '{current_cors_name}' found => '{current_cors_value}'")
                            else:
                                # Current flag exists in expected, check value(s)
                                if current_cors_value != watch_item.get(current_cors_name):
                                    print(
                                        f"12 - {current_host_port_flag}: cors flag '{current_cors_name}' changed => '{current_cors_value}'")

    nmap_object.items()

    # Check expected flags against current flags
    # TODO: Check expected flag keys against flag keys in current scan
    for key_expected_host, expected_host in watch_config.items():
        # print(f"key_expected_host: {key_expected_host}")
        # print(f"expected_host: {expected_host}")
        # key_expected_host:
        #     www.example.com | www.tes.com
        for key_expected_host_port, expected_host_port in expected_host.items():
            # print(f"key_expected_host_port: {key_expected_host_port}")
            # print(f"expected_host_port: {expected_host_port}")
            # key_expected_host_port:
            #     80 | 443

            # Matching flag items from current nmap scan (hostname + port).
            # It's important to leave out IPs since the cloud environment switches IP regular.
            # print(f"************\n{key_expected_host}:{key_expected_host_port}")
            all_current_nmap_hostname_port_flag_matches = get_all_hostname_and_port_flags(key_expected_host,
                                                                                          key_expected_host_port,
                                                                                          nmap_flags)

            # Get the two properties:
            #     service_name | expected_flags
            expected_service_name = expected_host_port.get("service_name")
            expected_flags = expected_host_port.get("expected_flags")
            # print(f"expected_service_name: {expected_service_name}")
            # print(f"expected_flags: {expected_flags}")

            for key_expected_flag, expected_flag_item in expected_flags.items():
                # print(f"key_expected_flag: {key_expected_flag}")
                # print(f"expected_flag_item: {expected_flag_item}")
                # key_expected_host_port_item:
                #     nmap_vulners | security_headers | cookie_flags | cors

                yyy:list[dict] = []
                for xxx in all_current_nmap_hostname_port_flag_matches:
                    if xxx.get(key_expected_flag):
                        print(xxx)

                for expected_item_flag_name, expected_item_flag_value in expected_flag_item.items():
                    # print(f"{expected_item_flag_name}: {expected_item_flag_value}")
                    # name and value:
                    #     (nmap_vulners)     {"https-redirect": "https-redirect", ...}
                    #     (security_headers) {"content-security-policy": ["prev found flag1", "prev found flag2"], ...}
                    #     (cookie_flags)     {"https-cookie_1": "Missing Secure", ...}
                    #     (cors)             {"misconfiguration_1": "descriptive text", ...}
                    expected_and_current_matches = False
                    match key_expected_flag:
                        case "nmap_vulners":
                            # print(f"{expected_item_flag_name}: {expected_item_flag_value}")
                            pass
                        case "security_headers":
                            # print(f"{expected_item_flag_name}: {expected_item_flag_value}")
                            pass
                        case "cookie_flags":
                            # print(f"{expected_item_flag_name}: {expected_item_flag_value}")
                            pass
                        case "cors":
                            # print(f"{expected_item_flag_name}: {expected_item_flag_value}")
                            for xxx in all_current_nmap_hostname_port_flag_matches:
                                print(xxx)
                            pass

        # watch_item = watch_port_expected_flags.get(key)
        # for current_nmap_ip, current_nmap_values in nmap_object.items():
        #    print(f"current_nmap_ip: {current_nmap_ip}")
        #    print(f"current_nmap_values: {current_nmap_values}")
            # current_item_name = current_item.get("name")
            # if current_item_name not in watch_item:
            #    print(f"8 - {current_host_port_flag}: new flag found => {current_item_name}")


def get_all_hostname_and_port_flags(expected_hostname: str,
                                    expected_hostname_port: str,
                                    nmap_flags: list[dict]) -> list[list[dict]]:
    hostname_port_flags: list[list[dict]] = []

    for item in nmap_flags:
        current_hostnames: list = item.get("hostname")
        current_port = item.get("port")
        if expected_hostname in current_hostnames and expected_hostname_port == current_port:
            if item.get("items"):
                hostname_port_flags.append(item.get("items"))

    return hostname_port_flags


watch()
