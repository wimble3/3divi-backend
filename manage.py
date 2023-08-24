from app import app
from app.management.run.face_recognition_consumer import bp as fr_consumer_bp
from app.management.run.server import bp as server_bp
from app.management.run.video_upload_consumer import bp as vu_consumer_bp


app.register_blueprint(fr_consumer_bp)
app.register_blueprint(server_bp)
app.register_blueprint(vu_consumer_bp)

if __name__ == "__main__":
    app.cli()
