from website import create_app

from config import settings

app = create_app()

if __name__ == '__main__':
	app.run(debug=True, port=int(settings.PORT))