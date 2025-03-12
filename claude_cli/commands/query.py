from claude_cli.utils.client import EnhancedClient
from rich.console import Console
from rich.panel import Panel
import sys

console = Console()

def send_query(config, prompt, conversation_id=None, attachment=None, proxy=None, debug=False):
    """Send a one-off query to Claude and return the response."""
    cookie = config.get('cookie')
    claude = EnhancedClient(cookie, proxy=proxy, debug=debug)
    
    # Create a new conversation if needed
    if not conversation_id:
        conversation = claude.create_new_chat()
        if 'error' in conversation:
            console.print(f"[bold red]Error creating conversation:[/] {conversation['error']}")
            sys.exit(1)
        conversation_id = conversation['uuid']
        if debug:
            console.print(f"[dim]Created new conversation: {conversation_id}[/]")
    else:
        # Verify the conversation exists
        try:
            conversations = claude.list_all_conversations()
            ids = [conv['uuid'] for conv in conversations]
            if conversation_id not in ids:
                console.print(f"[bold red]Error:[/] Conversation ID '{conversation_id}' not found.")
                sys.exit(1)
        except Exception as e:
            if debug:
                console.print(f"[yellow]Warning: Could not verify conversation ID: {str(e)}[/]")
                console.print(f"[yellow]Attempting to use the specified conversation ID anyway.[/]")
    
    # Send the message
    try:
        if debug:
            console.print("[dim]Sending query to Claude...[/]")
        else:
            console.print("Working...", end="\r")
        
        if attachment:
            if debug:
                console.print(f"[dim]With attachment: {attachment}[/]")
            response = claude.send_message(prompt, conversation_id, attachment=attachment)
        else:
            response = claude.send_message(prompt, conversation_id)
        
        # Clear the "Working..." line
        if not debug:
            console.print(" " * 20, end="\r")
        
        # Check if we got the new format with meta info
        if isinstance(response, dict) and "text" in response:
            text_response = response["text"]
            
            # Show response time if available
            if debug and "meta" in response and "response_time_seconds" in response["meta"]:
                response_time = response["meta"]["response_time_seconds"]
                model = response["meta"].get("model", "unknown")
                endpoint = response["meta"].get("endpoint", "unknown")
                chars = response["meta"].get("characters", 0)
                
                console.print(Panel(
                    f"Response time: {response_time:.2f}s\n"
                    f"Model: {model}\n"
                    f"Endpoint: {endpoint}\n"
                    f"Characters: {chars}",
                    title="Response Info", 
                    expand=False
                ))
            
            return text_response
        else:
            # Legacy format
            return response
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)