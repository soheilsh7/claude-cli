"""
Enhanced Claude Client with proxy support and improved error handling
"""
import json
import os
import uuid
import re
from curl_cffi import requests
import requests as req


class EnhancedClient:
    """
    An enhanced version of the Claude API client with proxy support
    and more robust error handling.
    """

    def __init__(self, cookie, proxy=None):
        """
        Initialize the client with cookie and optional proxy.
        
        Args:
            cookie (str): Claude AI cookie
            proxy (str, optional): Proxy URL (e.g., "socks5://127.0.0.1:1080")
        """
        self.cookie = cookie
        self.proxy = proxy
        self.organization_id = self.get_organization_id()

    def get_organization_id(self):
        """Get the organization ID using the provided cookie."""
        url = "https://claude.ai/api/organizations"

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Content-Type': 'application/json',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Cookie': f'{self.cookie}'
        }

        response = self._make_request("GET", url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to get organization ID: {response.status_code}")
            
        try:
            res = json.loads(response.text)
            if not res or len(res) == 0:
                raise Exception("No organizations found")
            uuid = res[0]['uuid']
            return uuid
        except Exception as e:
            raise Exception(f"Failed to parse organization response: {str(e)}")

    def get_content_type(self, file_path):
        """Determine content type based on file extension."""
        extension = os.path.splitext(file_path)[-1].lower()
        if extension == '.pdf':
            return 'application/pdf'
        elif extension == '.txt':
            return 'text/plain'
        elif extension == '.csv':
            return 'text/csv'
        # Add more content types as needed for other file types
        else:
            return 'application/octet-stream'

    def list_all_conversations(self):
        """List all conversations from Claude AI."""
        url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations"

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Content-Type': 'application/json',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Cookie': f'{self.cookie}'
        }

        response = self._make_request("GET", url, headers=headers)
        
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse conversations: {str(e)}")
                return []
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    def send_message(self, prompt, conversation_id, attachment=None, timeout=500):
        """Send a message to Claude with robust error handling."""
        url = "https://claude.ai/api/append_message"

        # Upload attachment if provided
        attachments = []
        if attachment:
            attachment_response = self.upload_attachment(attachment)
            if attachment_response:
                attachments = [attachment_response]
            else:
                return "Error: Invalid file format. Please try again."

        # Ensure attachments is an empty list when no attachment is provided
        if not attachment:
            attachments = []

        payload = json.dumps({
            "completion": {
                "prompt": f"{prompt}",
                "timezone": "UTC",
                "model": "claude-2"
            },
            "organization_uuid": f"{self.organization_id}",
            "conversation_uuid": f"{conversation_id}",
            "text": f"{prompt}",
            "attachments": attachments
        })

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/event-stream, text/event-stream',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Content-Type': 'application/json',
            'Origin': 'https://claude.ai',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Cookie': f'{self.cookie}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        }

        try:
            response = self._make_request("POST", url, headers=headers, data=payload)
            decoded_data = response.content.decode("utf-8", errors="ignore")
            
            # More robust parsing of server-sent events
            completions = []
            for line in decoded_data.split('\n'):
                line = line.strip()
                if not line or not line.startswith('data:'):
                    continue
                    
                try:
                    json_str = line[5:].strip()
                    data = json.loads(json_str)
                    if 'completion' in data:
                        completions.append(data['completion'])
                except json.JSONDecodeError:
                    # Try to extract with regex if JSON parsing fails
                    completion_match = re.search(r'"completion"\s*:\s*"([^"]*)"', line)
                    if completion_match:
                        completions.append(completion_match.group(1))
            
            answer = ''.join(completions)
            
            # If we still couldn't extract anything, try a more aggressive approach
            if not answer and decoded_data:
                # Look for anything that seems like a response
                all_completions = re.findall(r'"completion"\s*:\s*"([^"]*)"', decoded_data)
                answer = ''.join(all_completions)
                
                # If still nothing, return a portion of the raw response for debugging
                if not answer:
                    answer = "Failed to parse Claude's response. Raw data snippet:\n\n"
                    answer += decoded_data[:500] + "..." if len(decoded_data) > 500 else decoded_data
            
            return answer
            
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"

    def delete_conversation(self, conversation_id):
        """Delete a conversation."""
        url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}"

        payload = json.dumps(f"{conversation_id}")
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Content-Length': '38',
            'Referer': 'https://claude.ai/chats',
            'Origin': 'https://claude.ai',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Cookie': f'{self.cookie}',
            'TE': 'trailers'
        }

        response = self._make_request("DELETE", url, headers=headers, data=payload)

        if response.status_code == 204:
            return True
        else:
            return False

    def chat_conversation_history(self, conversation_id):
        """Get conversation history."""
        url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}"

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Content-Type': 'application/json',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Cookie': f'{self.cookie}'
        }

        response = self._make_request("GET", url, headers=headers)
        
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {"error": "Failed to parse conversation history"}
        else:
            return {"error": f"Failed to get conversation history: {response.status_code}"}

    def generate_uuid(self):
        """Generate a UUID for a new conversation."""
        random_uuid = uuid.uuid4()
        random_uuid_str = str(random_uuid)
        formatted_uuid = f"{random_uuid_str[0:8]}-{random_uuid_str[9:13]}-{random_uuid_str[14:18]}-{random_uuid_str[19:23]}-{random_uuid_str[24:]}"
        return formatted_uuid

    def create_new_chat(self):
        """Create a new chat conversation."""
        url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations"
        new_uuid = self.generate_uuid()

        payload = json.dumps({"uuid": new_uuid, "name": ""})
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Content-Type': 'application/json',
            'Origin': 'https://claude.ai',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        }

        response = self._make_request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {"uuid": new_uuid, "error": "Failed to parse response but conversation likely created"}
        else:
            return {"error": f"Failed to create conversation: {response.status_code}"}

    def reset_all(self):
        """Reset all conversations."""
        conversations = self.list_all_conversations()

        for conversation in conversations:
            conversation_id = conversation['uuid']
            self.delete_conversation(conversation_id)

        return True

    def upload_attachment(self, file_path):
        """Upload an attachment to Claude."""
        if file_path.endswith('.txt'):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_type = "text/plain"
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
            except UnicodeDecodeError:
                # If UTF-8 fails, try with latin-1 which can read any file
                with open(file_path, 'r', encoding='latin-1') as file:
                    file_content = file.read()

            return {
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "extracted_content": file_content
            }
            
        url = 'https://claude.ai/api/convert_document'
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Origin': 'https://claude.ai',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Cookie': f'{self.cookie}',
            'TE': 'trailers'
        }

        file_name = os.path.basename(file_path)
        content_type = self.get_content_type(file_path)

        files = {
            'file': (file_name, open(file_path, 'rb'), content_type),
            'orgUuid': (None, self.organization_id)
        }

        # For file uploads, we need to use the regular requests library
        # as curl_cffi doesn't handle multipart form data well
        proxies = {}
        if self.proxy:
            proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
            
        response = req.post(url, headers=headers, files=files, proxies=proxies)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def rename_chat(self, title, conversation_id):
        """Rename a chat conversation."""
        url = "https://claude.ai/api/rename_chat"

        payload = json.dumps({
            "organization_uuid": f"{self.organization_id}",
            "conversation_uuid": f"{conversation_id}",
            "title": f"{title}"
        })
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Referer': 'https://claude.ai/chats',
            'Origin': 'https://claude.ai',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Cookie': f'{self.cookie}',
            'TE': 'trailers'
        }

        response = self._make_request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            return True
        else:
            return False
            
    def _make_request(self, method, url, headers=None, data=None):
        """Make a request with proxy support if configured."""
        proxy_dict = {}
        if self.proxy:
            proxy_dict = {"proxies": {"https": self.proxy, "http": self.proxy}}
            
        if method == "GET":
            return requests.get(url, headers=headers, impersonate="chrome110", **proxy_dict)
        elif method == "POST":
            return requests.post(url, headers=headers, data=data, impersonate="chrome110", **proxy_dict)
        elif method == "DELETE":
            return requests.delete(url, headers=headers, data=data, impersonate="chrome110", **proxy_dict)
        else:
            raise ValueError(f"Unsupported method: {method}")