from dataclasses import dataclass

import helpers.config_helper as config_helper

@dataclass
class McServer():
    name: str
    path: str
    wrapper = None

    def get(self, key):
        return config_helper.get_setting(self.path, key)

    def set(self, key, value):
        config_helper.save_setting(self.path, key, value)

    def keys(self):
        return config_helper.get_settings(self.path).keys()

    def get_start_command(self):
        config = config_helper.get_settings(self.path)
        params = ["java", "jar", "ram", "port", "maxp", "whitelist"]
        cmd = ""
        for param in params:
            try:
                cmd += f" -{param} " + config[param] if config[param] != "" else ""
            except KeyError:
                pass
        return cmd.strip(" ")
