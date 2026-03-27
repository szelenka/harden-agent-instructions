SECRET_KEY = "fixture-only-not-real"
DEBUG = True
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "src.todos",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "src.urls"
