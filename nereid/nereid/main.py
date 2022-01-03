from nereid.factory import create_app

app = create_app(dict(NEREID_FORCE_FOREGROUND=True))
