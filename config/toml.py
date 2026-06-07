from django.conf import settings
import tomllib

def toml_config_processor(request):
    path = settings.BASE_DIR / "site_config.toml"
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return {"TOML": data}