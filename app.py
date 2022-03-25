from api import create_app
from flask import url_for

# ========================================================
# Run App
# ========================================================
app = create_app('development')


def runserver():
    print("Server is runing")
    app.run(port=5050)


if __name__ == '__main__':
        runserver()


