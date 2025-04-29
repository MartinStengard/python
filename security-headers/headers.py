import utils
from constants import EVAL_WARN


class SecurityHeadersException(Exception):
    pass


class SecurityHeaders:
    SECURITY_HEADERS_DICT = {
        'x-frame-options': {
            'recommended': True,
            'eval_func': utils.eval_x_frame_options,
        },
        'strict-transport-security': {
            'recommended': True,
            'eval_func': utils.eval_sts,
        },
        'content-security-policy': {
            'recommended': True,
            'eval_func': utils.eval_csp,
        },
        'x-content-type-options': {
            'recommended': True,
            'eval_func': utils.eval_content_type_options,
        },
        'x-xss-protection': {
            # X-XSS-Protection is deprecated; not supported anymore, and may be even dangerous in older browsers
            'recommended': False,
            'eval_func': utils.eval_x_xss_protection,
        },
        'referrer-policy': {
            'recommended': True,
            'eval_func': utils.eval_referrer_policy,
        },
        'permissions-policy': {
            'recommended': True,
            'eval_func': utils.eval_permissions_policy,
        }
    }

    SERVER_VERSION_HEADERS = [
        'x-powered-by',
        'server',
        'x-aspnetmvc-version',
        'x-generator',
        'x-dupral-cache'
        'x-server',
        'x-aspnet-version',
        'x-wix-renderer-server'
    ]

    def __analyze(self):
        """ Default return array """
        retval = {}

        if not self.headers:
            raise SecurityHeadersException("Headers not found")

        """ Loop through headers and evaluate the risk """
        for header in self.SECURITY_HEADERS_DICT:
            if header in self.headers:
                eval_func = self.SECURITY_HEADERS_DICT[header].get('eval_func')
                if not eval_func:
                    raise SecurityHeadersException("No evaluation function found for header: {}".format(header))
                res, notes = eval_func(self.headers[header])
                retval[header] = {
                    'defined': True,
                    'warn': res == EVAL_WARN,
                    'contents': self.headers[header],
                    'notes': notes,
                }

            else:
                warn = self.SECURITY_HEADERS_DICT[header].get('recommended')
                retval[header] = {'defined': False, 'warn': warn, 'contents': None, 'notes': []}

        for header in self.SERVER_VERSION_HEADERS:
            if header in self.headers:
                res, notes = utils.eval_version_info(self.headers[header])
                retval[header] = {
                    'defined': True,
                    'warn': res == EVAL_WARN,
                    'contents': self.headers[header],
                    'notes': notes,
                }

        return retval

    def __init__(self, headers):
        self.headers = {key.lower(): val.lower() for key, val in headers.items()}

    @staticmethod
    def analyze(headers):
        sh = SecurityHeaders(headers)
        result = sh.__analyze()

        if not result:
            print("Failed to fetch headers, exiting...")
            return

        for header, value in result.items():
            if value['warn']:
                if not value['defined']:
                    utils.print_warning("Header '{}' is missing".format(header))
                else:
                    utils.print_warning("Header '{}' contains value '{}".format(header, value['contents']))
                    for n in value['notes']:
                        print(" * {}".format(n))
            else:
                if not value['defined']:
                    utils.print_ok("Header '{}' is missing".format(header))
                else:
                    utils.print_ok("Header '{}' contains value".format(header))
