import yaml


class ConfigError(ValueError):
    def __init__(self, key, description):
        ValueError.__init__(self, f'A {description} (`{key}`) needs to be defined in settings.yaml!')


class Settings:
    def __init__(self):
        with open('settings.yaml') as f:
            self.data = yaml.safe_load(f)

    def _safe_get_string_setting(self, key, description) -> str:
        if key not in self.data:
            raise ConfigError(key, description)

        return self.data[key]

    def get_twitch_client_id(self) -> str:
        return self._safe_get_string_setting('twitch_client_id', 'Client-ID for connecting with the Twitch API')

    def get_twitch_client_secret(self) -> str:
        return self._safe_get_string_setting('twitch_client_secret', 'Client-Secret for connecting with the Twitch API')
