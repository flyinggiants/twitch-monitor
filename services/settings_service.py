from typing import Union, Optional

import yaml


class ConfigError(ValueError):
    def __init__(self, missing_name, key):
        ValueError.__init__(self, f'A {missing_name} (`{key}`) needs to be defined in settings.yaml!')


class Settings:
    def __init__(self):
        with open('settings.yaml') as f:
            self.data = yaml.safe_load(f)

    def _safe_get_string_setting(self, key, missing_name) -> str:
        if key not in self.data:
            raise ConfigError(missing_name, key)

        return self.data[key]

    def get_twitch_client_id(self) -> str:
        return self._safe_get_string_setting('twitch_client_id', 'Client-ID for connecting with the Twitch API')

    def get_twitch_client_secret(self) -> str:
        return self._safe_get_string_setting('twitch_client_secret', 'Client-Secret for connecting with the Twitch API')
