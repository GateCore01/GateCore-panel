from flask import Flask, request, jsonify
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES

app = Flask(__name__)

# LDAP-Konfiguration (anpassen!)
LDAP_SERVER = "ldap://your-ldap-server.com"
LDAP_BASE_DN = "dc=example,dc=com"
LDAP_USERNAME = "cn=admin,dc=example,dc=com"
LDAP_PASSWORD = "your-password"

def authenticate_user(username, password):
    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=LDAP_USERNAME, password=LDAP_PASSWORD, auto_bind=True)
        
        # Suche nach Benutzer
        search_filter = f"(uid={username})"
        conn.search(LDAP_BASE_DN, search_filter, ALL_ATTRIBUTES)
        
        if conn.entries:
            # Prüfe das Passwort (wird hier nicht direkt getestet – muss mit bind getestet werden)
            # Hier: binden mit dem eingegebenen Passwort
            conn.bind(username, password)
            return True
        return False
    except Exception as e:
        return False

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if authenticate_user(username, password):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Fehler beim Login."})

if __name__  == '__main__':
    app.run(port=5000)