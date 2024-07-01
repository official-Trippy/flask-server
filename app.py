from api import create_app
from response_dto import ReasonDTO, ErrorReasonDTO

app = create_app()
app.config['JSON_AS_ASCII'] = False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')