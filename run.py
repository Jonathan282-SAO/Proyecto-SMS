from app import create_app
app = create_app()


if __name__ == '__main__':
    # Arranque simple de la aplicación desde la factory.
    app.run(debug=True)