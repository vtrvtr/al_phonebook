# Copy this file to $HOME/.al_phonebook/plugins to be able to print contacts in json format.

import json

class JsonFormatter:

    def format(d):
        return json.dumps(d, indent=4)