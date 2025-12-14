"""
Gmail OAuth Server
Tiny local HTTP server to complete OAuth flow.
"""
import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from email_agent.credentials import create_flow, exchange_code_for_tokens, save_tokens

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 8080


class OAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth flow."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/oauth/start':
            self.handle_start()
        elif path == '/oauth/callback':
            self.handle_callback(parsed_path.query)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def handle_start(self):
        """Start OAuth flow - redirect to Google consent."""
        try:
            redirect_uri = f'http://localhost:{PORT}/oauth/callback'
            flow = create_flow(redirect_uri=redirect_uri)
            
            if not flow:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Failed to create OAuth flow. Check client_secret.json')
                return
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            # Redirect to Google
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()
            
            logger.info(f"Redirecting to: {auth_url}")
            
        except Exception as e:
            logger.error(f"Error starting OAuth flow: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
    
    def handle_callback(self, query_string: str):
        """Handle OAuth callback - exchange code for tokens."""
        try:
            params = parse_qs(query_string)
            code = params.get('code', [None])[0]
            error = params.get('error', [None])[0]
            
            if error:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'OAuth error: {error}'.encode())
                logger.error(f"OAuth error: {error}")
                return
            
            if not code:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Missing authorization code')
                return
            
            # Exchange code for tokens
            redirect_uri = f'http://localhost:{PORT}/oauth/callback'
            credentials = exchange_code_for_tokens(code, redirect_uri)
            
            if credentials:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('''
                    <html>
                    <head><title>Gmail OAuth Complete</title></head>
                    <body>
                        <h1>✅ Gmail OAuth completed successfully!</h1>
                        <p>Tokens have been saved to ~/.l9/gmail/tokens.json</p>
                        <p>You can close this window.</p>
                    </body>
                    </html>
                '''.encode('utf-8'))
                from email_agent.config import GMAIL_ACCOUNT
                logger.info(f"OAuth completed for {GMAIL_ACCOUNT}")
                print(f"\n✅ OAuth completed for {GMAIL_ACCOUNT}")
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Failed to exchange code for tokens')
                
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Run OAuth server."""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, OAuthHandler)
    
    print(f"\n🌐 Gmail OAuth Server starting on http://localhost:{PORT}")
    print(f"📋 Open http://localhost:{PORT}/oauth/start in your browser")
    print("Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.shutdown()


if __name__ == '__main__':
    main()
