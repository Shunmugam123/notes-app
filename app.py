from flask import Flask, render_template, request, redirect, url_for
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
APP_VERSION = "1.0.0"

# Initialize Firestore
# It's recommended to set the GOOGLE_APPLICATION_CREDENTIALS environment variable
# to the path of your service account key file for production.
# For local development, you might load it directly if the file is accessible.
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    cred = credentials.ApplicationDefault()
else:
    # This path is for local testing if GOOGLE_APPLICATION_CREDENTIALS is not set
    # In a real app, you'd handle credentials more securely
    print("WARNING: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
    print("Attempting to initialize Firebase with default credentials (e.g., when running on GCP).")
    try:
        cred = credentials.ApplicationDefault()
    except Exception as e:
        print(f"ERROR: Could not initialize Firebase with ApplicationDefault: {e}")
        print("To fix this:")
        print("1. Ensure your Google Cloud project has a Firestore database enabled.")
        print("2. If running locally, set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account key file.")
        print(f"   Visit https://console.cloud.google.com/datastore/setup?project={os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')} to enable Firestore.")
        cred = None # Set cred to None if initialization fails

if cred:
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    notes_collection = db.collection('notes')
else:
    db = None
    notes_collection = None
    print("CRITICAL: Firestore not initialized. Notes functionality will be disabled.")
    print("Please ensure you have set up Firestore for your project.")


@app.route('/')
def index():
    notes = []
    if notes_collection:
        try:
            for doc in notes_collection.stream():
                note = doc.to_dict()
                note['id'] = doc.id
                notes.append(note)
        except Exception as e:
            print(f"Error fetching notes: {e}")
            notes = [{"id": "error", "title": "Error", "content": "Could not fetch notes."}]
    return render_template('index.html', notes=notes, app_version=APP_VERSION, firestore_ready=(db is not None))

@app.route('/add', methods=['POST'])
def add_note():
    if notes_collection:
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            notes_collection.add({'title': title, 'content': content})
    return redirect(url_for('index'))

@app.route('/delete/<note_id>')
def delete_note(note_id):
    if notes_collection and note_id:
        notes_collection.document(note_id).delete()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
