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

    def __init__(self, cookie, proxy=None, debug=False):
        """
        Initialize the client with cookie and optional proxy.
        
        Args:
            cookie (str): Claude AI cookie
            proxy (str, optional): Proxy URL (e.g., "socks5://127.0.0.1:1080")
            debug (bool, optional): Whether to output debug information
        """
        self.cookie = cookie
        self.proxy = proxy
        self.debug = debug
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

        try:
            if self.debug:
                print(f"Fetching organization ID from: {url}")
                
            response = self._make_request("GET", url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"Failed to get organization ID: HTTP {response.status_code}"
                try:
                    error_data = json.loads(response.content)
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                except:
                    pass
                raise Exception(error_msg)
                
            res = json.loads(response.text)
            if not res or len(res) == 0:
                raise Exception("No organizations found. Your cookie may be invalid or expired.")
            uuid = res[0]['uuid']
            
            if self.debug:
                print(f"Successfully retrieved organization ID: {uuid}")
                
            return uuid
        except json.JSONDecodeError:
            raise Exception("Failed to parse organization response. The API may have changed or your cookie is invalid.")
        except Exception as e:
            if "Proxy connection error" in str(e) or "Connection error" in str(e):
                raise  # Re-raise connection errors directly
            raise Exception(f"Failed to get organization ID: {str(e)}")

    def get_content_type(self, file_path):
        """Determine content type based on file extension."""
        extension = os.path.splitext(file_path)[-1].lower()
        if extension == '.pdf':
            return 'application/pdf'
        elif extension == '.txt':
            return 'text/plain'
        elif extension == '.csv':
            return 'text/csv'
        elif extension == '.doc' or extension == '.docx':
            return 'application/msword'
        elif extension == '.ppt' or extension == '.pptx':
            return 'application/vnd.ms-powerpoint'
        elif extension == '.xls' or extension == '.xlsx':
            return 'application/vnd.ms-excel'
        elif extension == '.png':
            return 'image/png'
        elif extension == '.jpg' or extension == '.jpeg':
            return 'image/jpeg'
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

        try:
            response = self._make_request("GET", url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"Failed to list conversations: HTTP {response.status_code}"
                try:
                    error_data = json.loads(response.content)
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                except:
                    pass
                raise Exception(error_msg)
            
            return json.loads(response.text)
        except json.JSONDecodeError:
            return []
        except Exception as e:
            if "Proxy connection error" in str(e) or "Connection error" in str(e):
                raise  # Re-raise connection errors directly
            raise Exception(f"Failed to list conversations: {str(e)}")

    def send_message(self, prompt, conversation_id, attachment=None, timeout=500):
        """Send a message to Claude with robust error handling."""
        # Try different API endpoints - Claude periodically changes these
        api_endpoints = [
            f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}/completion"
        ]
        
        # Verify conversation exists before trying to send message
        try:
            conversations = self.list_all_conversations()
            conv_ids = [conv['uuid'] for conv in conversations]
            if conversation_id not in conv_ids:
                return f"Error: Conversation ID '{conversation_id}' does not exist in your account. Please check the ID or create a new conversation."
        except Exception as e:
            if self.debug:
                print(f"Warning: Could not verify conversation ID: {str(e)}")
            # Continue anyway as the ID might still be valid

        # Upload attachment if provided
        attachments = []
        if attachment:
            attachment_response = self.upload_attachment(attachment)
            if attachment_response:
                attachments = [attachment_response]
            else:
                return "Error: Invalid file format or upload failed. Please try again."

        # Ensure attachments is an empty list when no attachment is provided
        if not attachment:
            attachments = []

        # Try different models if one fails - newer model names first
        models_to_try = ["claude"]
        
        # Start the timer for response time tracking
        import time
        start_time = time.time()
        
        for endpoint in api_endpoints:
            if self.debug:
                print(f"Trying endpoint: {endpoint}")
            for model in models_to_try:
                # Try different payload formats
                payloads = [
                    # Simplified format
                    json.dumps({
                        "prompt": f"{prompt}",
                        "attachments": attachments
                    })
                ]
                
                for payload_idx, payload in enumerate(payloads):

                    # Freshen headers with each attempt
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
                        if self.debug:
                            print(f"Trying model: {model}, payload format: {payload_idx+1}")
                        response = self._make_request("POST", endpoint, headers=headers, data=payload, timeout=timeout)
                        
                        # Check for error responses first
                        if response.status_code != 200:
                            error_msg = f"Error from Claude API: HTTP {response.status_code}"
                            try:
                                error_data = json.loads(response.content)
                                if isinstance(error_data, dict) and 'error' in error_data:
                                    error_msg += f" - {error_data['error'].get('message', 'Unknown error')}"
                                    
                                    # Specific error handling
                                    if error_data['error'].get('type') == 'not_found_error':
                                        error_msg += "\n\nThis could mean:\n- The conversation ID doesn't exist\n- Your cookie has expired\n- The API endpoints have changed"
                                    
                            except Exception:
                                pass
                            
                            # Continue to next payload format or model or endpoint
                            continue
                    
                        # Process successful response
                        if self.debug:
                            print(f"Success! Got 200 response from endpoint: {endpoint}, model: {model}")
                        decoded_data = response.content.decode("utf-8", errors="ignore")
                        
                        # Look for patterns in the response to detect format
                        # First, check if it's a streaming response
                        if 'data:' in decoded_data:
                            if self.debug:
                                print("Detected streaming response format")
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
                                    elif 'text' in data:  # Alternative format
                                        completions.append(data['text'])
                                    elif 'delta' in data and 'text' in data['delta']:  # Claude 3 format
                                        completions.append(data['delta']['text'])
                                except json.JSONDecodeError:
                                    # Try to extract with regex if JSON parsing fails
                                    completion_match = re.search(r'"completion"\s*:\s*"([^"]*)"', line)
                                    if completion_match:
                                        completions.append(completion_match.group(1))
                            
                            answer = ''.join(completions)
                        else:
                            # Might be a regular JSON response
                            if self.debug:
                                print("Detected non-streaming response format")
                            try:
                                data = json.loads(decoded_data)
                                # Various possible response formats
                                if 'completion' in data:
                                    answer = data['completion']
                                elif 'text' in data:
                                    answer = data['text']
                                elif 'content' in data:
                                    answer = data['content']
                                else:
                                    # Return the whole response for debugging
                                    answer = f"Got a 200 response but couldn't extract text. Raw data:\n\n{decoded_data[:1000]}"
                            except json.JSONDecodeError:
                                answer = f"Got a 200 response but couldn't parse JSON. Raw data:\n\n{decoded_data[:1000]}"
                        
                        # If we still couldn't extract anything, try a more aggressive approach
                        if not answer and decoded_data:
                            if self.debug:
                                print("Trying aggressive pattern matching")
                            # Look for anything that seems like a response
                            patterns = [
                                r'"completion"\s*:\s*"([^"]*)"',
                                r'"text"\s*:\s*"([^"]*)"',
                                r'"content"\s*:\s*"([^"]*)"',
                                r'"delta"\s*:\s*{\s*"text"\s*:\s*"([^"]*)"'
                            ]
                            
                            for pattern in patterns:
                                all_matches = re.findall(pattern, decoded_data)
                                if all_matches:
                                    answer = ''.join(all_matches)
                                    break
                            
                        # If we got a valid response, return it!
                        if answer and len(answer.strip()) > 0:
                            # Calculate response time
                            end_time = time.time()
                            response_time = end_time - start_time
                            
                            if self.debug:
                                print(f"Successfully extracted answer ({len(answer)} chars)")
                                print(f"Response time: {response_time:.2f} seconds")
                                
                            # Add a meta field with response information
                            result = {
                                "text": answer,
                                "meta": {
                                    "response_time_seconds": round(response_time, 2),
                                    "model": model,
                                    "endpoint": endpoint,
                                    "characters": len(answer)
                                }
                            }
                            return result
                        
                        # If we get here, we got a 200 response but couldn't extract the answer
                        if self.debug:
                            print("Got 200 response but couldn't extract answer")
                        if payload_idx == len(payloads) - 1 and model == models_to_try[-1] and endpoint == api_endpoints[-1]:
                            end_time = time.time()
                            response_time = end_time - start_time
                            error_msg = f"Got response from Claude but couldn't extract the answer. Raw data:\n\n{decoded_data[:1000]}"
                            return {
                                "text": error_msg,
                                "meta": {
                                    "response_time_seconds": round(response_time, 2),
                                    "error": True
                                }
                            }
                    
                    except Exception as e:
                        if self.debug:
                            print(f"Exception with endpoint {endpoint}, model {model}, payload {payload_idx+1}: {str(e)}")
                        # Continue to next payload format
                        continue
        
        # This should only be reached if all endpoints, models, and payload formats failed
        end_time = time.time()
        response_time = end_time - start_time
        error_msg = "All communication attempts with Claude failed. The Claude.ai API may have changed significantly. Please check for updates to the client library or try refreshing your cookie."
        return {
            "text": error_msg,
            "meta": {
                "response_time_seconds": round(response_time, 2),
                "error": True
            }
        }

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

        try:
            response = self._make_request("DELETE", url, headers=headers, data=payload)
            
            if response.status_code == 204:
                return True
            else:
                return False
        except Exception:
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

        try:
            if self.debug:
                print(f"Fetching conversation history from: {url}")
                
            response = self._make_request("GET", url, headers=headers)
            
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                error_msg = f"Failed to get conversation history: HTTP {response.status_code}"
                try:
                    error_data = json.loads(response.content)
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                except:
                    pass
                    
                if self.debug:
                    print(error_msg)
                    
                return {"error": error_msg}
        except json.JSONDecodeError:
            if self.debug:
                print("Failed to parse conversation history JSON")
            return {"error": "Failed to parse conversation history"}
        except Exception as e:
            if self.debug:
                print(f"Exception fetching history: {str(e)}")
            return {"error": f"Failed to get conversation history: {str(e)}"}

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

        try:
            response = self._make_request("POST", url, headers=headers, data=payload)
            
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                error_msg = f"Failed to create conversation: HTTP {response.status_code}"
                try:
                    error_data = json.loads(response.content)
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                except:
                    pass
                return {"error": error_msg, "uuid": new_uuid}
        except json.JSONDecodeError:
            return {"uuid": new_uuid, "error": "Failed to parse response but conversation likely created"}
        except Exception as e:
            return {"error": f"Failed to create conversation: {str(e)}", "uuid": new_uuid}

    def reset_all(self):
        """Reset all conversations."""
        conversations = self.list_all_conversations()
        
        if isinstance(conversations, dict) and "error" in conversations:
            return False

        for conversation in conversations:
            conversation_id = conversation['uuid']
            self.delete_conversation(conversation_id)

        return True

    def upload_attachment(self, file_path):
        """Upload an attachment to Claude."""
        if not os.path.exists(file_path):
            return False
            
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

        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            files = {
                'file': (file_name, file_data, content_type),
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
                
            response = req.post(url, headers=headers, files=files, proxies=proxies, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Failed to upload attachment: HTTP {response.status_code}"
                try:
                    error_data = json.loads(response.content)
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                except:
                    pass
                print(f"Upload error: {error_msg}")
                return False
        except Exception as e:
            print(f"Upload exception: {str(e)}")
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

        try:
            response = self._make_request("POST", url, headers=headers, data=payload)

            if response.status_code == 200:
                return True
            else:
                return False
        except Exception:
            return False
            
    def _make_request(self, method, url, headers=None, data=None, timeout=30):
        """Make a request with proxy support if configured and better error handling."""
        proxy_dict = {}
        if self.proxy:
            proxy_dict = {"proxies": {"https": self.proxy, "http": self.proxy}}
            
        try:
            if method == "GET":
                return requests.get(url, headers=headers, impersonate="chrome110", timeout=timeout, **proxy_dict)
            elif method == "POST":
                return requests.post(url, headers=headers, data=data, impersonate="chrome110", timeout=timeout, **proxy_dict)
            elif method == "DELETE":
                return requests.delete(url, headers=headers, data=data, impersonate="chrome110", timeout=timeout, **proxy_dict)
            else:
                raise ValueError(f"Unsupported method: {method}")
        except requests.exceptions.ProxyError:
            raise Exception(f"Proxy connection error. Please check your proxy configuration: {self.proxy}")
        except requests.exceptions.ConnectTimeout:
            raise Exception(f"Connection timeout. The request took too long to complete (>{timeout}s).")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error. Please check your internet connection and proxy settings.")