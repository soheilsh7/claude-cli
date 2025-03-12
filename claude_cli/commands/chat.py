import os
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from claude_cli.utils.client import EnhancedClient

console = Console()

def start_chat(config, new_chat=False, conversation_id=None, proxy=None, debug=False):
    """Start an interactive chat session with Claude."""
    cookie = config.get('cookie')
    claude = EnhancedClient(cookie, proxy=proxy, debug=debug)
    
    # Handle conversation ID
    if not conversation_id and not new_chat:
        # Check if there's a default conversation
        if 'default_conversation_id' in config and not new_chat:
            conversation_id = config.get('default_conversation_id')
            console.print(f"[cyan]Using default conversation: {conversation_id}[/]")
        else:
            # Start a new conversation
            conversation = claude.create_new_chat()
            conversation_id = conversation['uuid']
            console.print(f"[green]Created new conversation: {conversation_id}[/]")
    elif new_chat:
        # Force a new conversation
        conversation = claude.create_new_chat()
        conversation_id = conversation['uuid']
        console.print(f"[green]Created new conversation: {conversation_id}[/]")
    else:
        # Verify the conversation exists
        conversations = claude.list_all_conversations()
        ids = [conv['uuid'] for conv in conversations]
        if conversation_id not in ids:
            console.print(f"[bold red]Error:[/] Conversation ID '{conversation_id}' not found.")
            sys.exit(1)
        console.print(f"[cyan]Continuing conversation: {conversation_id}[/]")
    
    console.print("[bold]Welcome to Claude Chat![/]")
    console.print("Type 'exit' or press Ctrl+C to quit, 'help' for commands")
    
    # Load any existing conversation history
    try:
        history = claude.chat_conversation_history(conversation_id)
        if history and 'chat_messages' in history and len(history['chat_messages']) > 0:
            console.print("[cyan]--- Previous messages ---[/]")
            # Print last few messages for context
            for message in history['chat_messages'][-6:]:  # Show last 6 messages
                role = "You" if message['sender'] == 'human' else "Claude"
                content = message['message']['content'][0]['text']
                console.print(f"[bold]{role}:[/] {content[:100]}{'...' if len(content) > 100 else ''}")
            console.print("[cyan]--- New conversation ---[/]")
    except Exception as e:
        # If we can't load history, just continue
        if debug:
            console.print(f"[yellow]Warning:[/] Couldn't load history: {str(e)}")
    
    # Main chat loop
    try:
        while True:
            user_input = console.input("[bold green]You:[/] ")
            
            # Handle built-in commands
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'help':
                show_help()
                continue
            elif user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            elif user_input.lower().startswith('attach '):
                # Extract file path
                file_path = user_input[7:].strip()
                if not os.path.exists(file_path):
                    console.print(f"[bold red]Error:[/] File '{file_path}' not found.")
                    continue
                
                # Ask for a message to send with the attachment
                message = console.input("[bold green]Message with attachment:[/] ")
                
                console.print("[cyan]Sending message with attachment...[/]")
                try:
                    response = send_message_safely(claude, message, conversation_id, attachment=file_path)
                    console.print("[bold purple]Claude:[/]")
                    
                    # Check if we got the new format with meta info
                    if isinstance(response, dict) and "text" in response:
                        console.print(Markdown(response["text"]))
                        
                        # Show response time if available
                        if "meta" in response and "response_time_seconds" in response["meta"]:
                            response_time = response["meta"]["response_time_seconds"]
                            console.print(f"[dim](Response time: {response_time:.2f}s)[/dim]")
                    else:
                        # Legacy format
                        console.print(Markdown(response))
                except Exception as e:
                    console.print(f"[bold red]Error sending attachment:[/] {str(e)}")
                continue
                
            # Regular message
            console.print("[cyan]Thinking...[/]")
            try:
                response = send_message_safely(claude, user_input, conversation_id)
                console.print("[bold purple]Claude:[/]")
                
                # Check if we got the new format with meta info
                if isinstance(response, dict) and "text" in response:
                    console.print(Markdown(response["text"]))
                    
                    # Show response time if available
                    if "meta" in response and "response_time_seconds" in response["meta"]:
                        response_time = response["meta"]["response_time_seconds"]
                        model = response["meta"].get("model", "unknown")
                        
                        if debug:
                            console.print(Panel(f"Response time: {response_time:.2f}s\nModel: {model}", 
                                              title="Response Info", 
                                              expand=False))
                        else:
                            console.print(f"[dim](Response time: {response_time:.2f}s)[/dim]")
                else:
                    # Legacy format
                    console.print(Markdown(response))
            except Exception as e:
                console.print(f"[bold red]Error:[/] {str(e)}")
    
    except KeyboardInterrupt:
        console.print("\n[bold]Exiting chat. Goodbye![/]")
        sys.exit(0)

def send_message_safely(claude, prompt, conversation_id, attachment=None):
    """Send a message with error handling for JSON parsing issues."""
    try:
        return claude.send_message(prompt, conversation_id, attachment=attachment)
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        console.print(f"[yellow]Warning: JSON parsing error: {str(e)}[/]")
        console.print("[yellow]Attempting to fix the response...[/]")
        
        # Patch the claude_api's send_message method with a more robust implementation
        # This is a temporary fix during this session
        def patched_send_message(self, prompt, conversation_id, attachment=None, timeout=500):
            import re
            import json
            
            url = "https://claude.ai/api/append_message"
            
            # Upload attachment if provided
            attachments = []
            if attachment:
                attachment_response = self.upload_attachment(attachment)
                if attachment_response:
                    attachments = [attachment_response]
                else:
                    return {"Error: Invalid file format. Please try again."}
            
            # Ensure attachments is an empty list when no attachment is provided
            if not attachment:
                attachments = []
            
            payload = json.dumps({
                "completion": {
                    "prompt": f"{prompt}",
                    "timezone": "Asia/Kolkata",
                    "model": "claude-2"
                },
                "organization_uuid": f"{self.organization_id}",
                "conversation_uuid": f"{conversation_id}",
                "text": f"{prompt}",
                "attachments": attachments
            })
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
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
            
            from curl_cffi import requests
            response = requests.post(url, headers=headers, data=payload, impersonate="chrome110", timeout=timeout)
            decoded_data = response.content.decode("utf-8")
            
            # More robust parsing
            completions = []
            for line in decoded_data.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Handle the server-sent event format
                if line.startswith('data: '):
                    try:
                        json_str = line[6:].strip()
                        data = json.loads(json_str)
                        if 'completion' in data:
                            completions.append(data['completion'])
                    except json.JSONDecodeError:
                        # Skip malformed JSON
                        console.print(f"[yellow]Skipping malformed data: {line[:30]}...[/]")
                        continue
            
            answer = ''.join(completions)
            if not answer and decoded_data:
                # Fallback: try to extract text between quotes if JSON parsing failed
                import re
                matches = re.findall(r'"completion"\s*:\s*"([^"]+)"', decoded_data)
                if matches:
                    answer = ''.join(matches)
                else:
                    answer = "Sorry, I couldn't process the response. Please try again."
            
            return answer
        
        # Apply the patch
        import types
        claude.send_message = types.MethodType(patched_send_message, claude)
        
        # Try again with the patched method
        return claude.send_message(prompt, conversation_id, attachment=attachment)

def show_help():
    """Show help for chat commands"""
    console.print("""
[bold]Available Commands:[/]
- [cyan]exit[/]: Exit the chat
- [cyan]help[/]: Show this help message
- [cyan]clear[/]: Clear the screen
- [cyan]attach [file][/]: Attach a file to your next message
""")