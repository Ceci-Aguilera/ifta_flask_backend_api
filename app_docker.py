from api import create_app

# ========================================================
# Run App
# ========================================================
app = create_app('testing')


def runserver():
    print("Server is runing")
    app.run(port=5050, host='0.0.0.0')


if __name__ == '__main__':
        runserver()