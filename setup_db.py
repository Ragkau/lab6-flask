from app import app, db

with app.app_context():
    db.drop_all()  # Clean slate
    db.create_all()
    print("Created tables:", db.metadata.tables.keys())
