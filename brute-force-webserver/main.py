from brute_force_webserver import BruteForce


def brute(url):
    brute_result = []
    brute_result += BruteForce.start(url, 2, "common_dir.lst")
    brute_result += BruteForce.start(url, 2, "common_php.lst")
    return brute_result


if __name__ == '__main__':
    result = brute("http://testphp.vulnweb.com")
    print(result)
