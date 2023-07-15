from pathlib import Path
from threading import Thread
import os, zipfile
from flask import (Flask, jsonify, redirect, request, send_file,
                   send_from_directory)
from werkzeug.serving import make_server

from src.context import AppContext, Participant, Session

QUESTIONS_FOLDER = Path('questions')

class ServerAPI(Thread):

    def __init__(self, host='0.0.0.0', port=8080):
        Thread.__init__(self)
        self.app = Flask(__name__, static_folder='../../../client/build')
        @self.app.route('/api/session/<int:session_id>', methods=['GET'])
        def api_session_handle_get(session_id: int):
            session = AppContext.sessions.get(session_id, None)
            if session is None:
                return "Session not found", 404

            return jsonify(session.as_dict)

        @self.app.route('/api/session', methods=['POST'])
        def api_get_all_sessions():
            print(request.json['user'])
            if 'user' not in request.json:
                return "Invalid request", 400
            username = request.json['user']
            password = request.json['pass']
            if(username!="admin" or password!="admin"):
                return "Check if your credentials are correct please", 400
            
            return jsonify([session.as_dict for session in AppContext.sessions.values()])

        @self.app.route('/api/session/<int:session_id>', methods=['POST'])
        def api_edit_session(session_id: int):
            session = AppContext.sessions.get(session_id, None)
            if session is None:
                return "Session not found", 404

            session_data = request.json
            if any(
                key not in ['status', 'question_id', 'duration']
                for key in session_data.keys()
            ):
                return "Invalid parameter", 400

            if 'status' in session_data:
                try:
                    session.status = Session.Status(session_data['status'])
                except ValueError:
                    return "Requested status is not valid", 400

            if 'question_id' in session_data:
                question_id = session_data['question_id']
                if not isinstance(question_id, int):
                    return "Requested question_id must be an integer", 400

                if not (QUESTIONS_FOLDER / str(question_id)).is_dir():
                    return "Requested question_id doesn't exist", 404

                session.active_question = question_id

            if 'duration' in session_data:
                if not isinstance(session_data['duration'], int):
                    return "Requested duration must be an integer", 400

                session.duration = session_data['duration']

            return jsonify(session.as_dict)

        @self.app.route('/api/session/<int:session_id>/allParticipants', methods=['POST'])
        def api_session_get_all_participants(session_id: int):
            if 'user' not in request.json:
                return "Invalid request", 400
            username = request.json['user']
            password = request.json['pass']
            if(username!="admin" or password!="admin"):
                return "Check if your credentials are correct please", 400
            session = AppContext.sessions.get(session_id, None)
            if session is None:
                return "Session not found", 404
            return jsonify([participant.as_dict for participant in session.participants.values()])

        # función que escucha la petición del componente sessionLogin
        @self.app.route('/api/session/<int:session_id>/participants', methods=['POST'])
        def api_session_add_participant(session_id: int):
            if 'user' not in request.json:
                return "Invalid request", 400
            username = request.json['user']

            session = AppContext.sessions.get(session_id, None)
            if session is None:
                return "Session not found", 404
            if any(username.lower() == participant.username.lower() and participant.status!=Participant.Status.OFFLINE for participant in session.participants.values()):
                return "Participant already joined session", 400

            participant = session.add_participant(username)

            return jsonify(participant.as_dict)

        @self.app.route('/api/session/<int:session_id>/participants/<int:participant_id>', methods=['POST'])
        def api_session_remove_participant(session_id: int, participant_id: int):
            session = AppContext.sessions.get(session_id, None)
            if session is None:
                return "Session not found", 404

            if any(participant_id == participant.id for participant in session.participants.values()):
                if any(participant_id == participant.id and participant.status==Participant.Status.OFFLINE for participant in session.participants.values()):
                    return "Participant already leaved session", 400
                else:
                    session.remove_participant(participant_id)
            else:
                return "Participant not found", 404
            return "Bye"
        @self.app.route('/api/collection')
        def api_get_all_collections():
            collections = AppContext.collections
            response = []
            if collections is None:
                return "Collections not found", 404
            for key, value in collections.items():
                response.append(value.as_dict)

            return jsonify(response)
        
        @self.app.route('/api/<string:collection>/question')
        def api_get_all_questions(collection: str):
            questions = AppContext.collections.get(collection).questions
            response = []
            if questions is None:
                return "Questions not found", 404
            for clave, valor in questions.items():
                response.append(valor)
            return jsonify(response)

        @self.app.route('/api/question/<string:collection>/<int:question_id>')
        def api_question_handle(collection: str, question_id: int):
            collection_obj = AppContext.collections.get(collection)
            if collection_obj is None:
                return "Collection not found", 404

            questions = collection_obj.questions
            if questions is None:
                return "Questions not found", 404

            question = questions.get(question_id)
            if question is None:
                return "Question not found", 404

            return jsonify(question.__json__())

        @self.app.route('/api/question/<string:collection>/<int:question_id>/image')
        def api_question_image_handle(collection: str, question_id: int):
            question = AppContext.collections.get(collection).questions.get(question_id, None)
            if question is None:
                return "Question not found", 404

            return send_file(question.img_path) if question.img_is_local else redirect(question.img_path)

        # Serve client app
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def client_handler(path):
            if path == '' or not (Path(self.app.static_folder) / path).is_file():
                return send_from_directory(self.app.static_folder, 'index.html')

            return send_from_directory(self.app.static_folder, path)

        # Peticiones para el admin
        @self.app.route('/api/admin/login', methods=['POST'])
        def api_admin_login():
            if 'user' not in request.json:
                return "Invalid request", 400
            username = request.json['user']
            password = request.json['pass']
            if(username!="admin" or password!="admin"):
                return "Check if your credentials are correct please", 400
            
            return jsonify({"status":"ok"})
        
        @self.app.route('/api/createSession', methods=['POST'])
        def api_create_session():
            if 'user' not in request.json:
                return "Invalid request", 400
            username = request.json['user']
            password = request.json['pass']
            if(username!="admin" or password!="admin"):
                return "Check if your credentials are correct please", 400
            session = Session()
            AppContext.sessions[session.id] = session
            return jsonify(session.as_dict)
        @self.app.route('/api/downloadLog/<path:zip_filename>')
        def download_log(zip_filename):
            zip_filename+=".zip"
            zip_path = os.path.join("./session_log/zips", zip_filename)
            if os.path.isfile(zip_path):
                return send_from_directory(os.path.abspath(os.path.dirname(zip_path)), os.path.basename(zip_path), as_attachment=True)
            else:
                return "El archivo ZIP no existe", 404
        @self.app.route('/api/downloadAllLogs')
        def download_all_logs():
            zip_filepath = generate_all_logs_zip()

            if zip_filepath and os.path.isfile(zip_filepath):
                return send_from_directory(os.path.abspath(os.path.dirname(zip_filepath)), os.path.basename(zip_filepath), as_attachment=True)
            else:
                return "Error al generar el archivo ZIP", 500

        def generate_all_logs_zip():
            try:
                zip_filename = "AllLogs.zip"
                folder_path = "./session_log/zips"
                zip_path = os.path.join("./session_log", zip_filename)  # Ruta completa del archivo ZIP
                if os.path.isfile(zip_path):
                    os.remove(zip_path)
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, folder_path))

                return zip_path
            except Exception as e:
                print(f"Error al generar el archivo ZIP: {str(e)}")
                return None

            
        @self.app.route('/api/listLogs')
        def list_logs():
            folder_path = './session_log'
            logs = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]

            return jsonify(logs=logs)
        
        self.server = make_server(host, port, self.app, threaded=True)
        self.ctx = self.app.app_context()
        self.ctx.push()
        
    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
