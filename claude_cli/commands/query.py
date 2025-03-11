from claude_cli.utils.client import EnhancedClient
from rich.console import Console
import sys

console = Console()

def send_query(config, prompt, conversation_id=None, attachment=None, proxy=None):
    """Send a one-off query to Claude and return the response."""
    cookie = config.get('cookie')
    claude = EnhancedClient(cookie, proxy=proxy)
    
    # Create a new conversation if needed
    if not conversation_id:
        conversation = claude.create_new_chat()
        if 'error' in conversation:
            console.print(f"[bold red]Error creating conversation:[/] {conversation['error']}")
            sys.exit(1)
        conversation_id = conversation['uuid']
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
            console.print(f"[yellow]Warning: Could not verify conversation ID: {str(e)}[/]")
            console.print(f"[yellow]Attempting to use the specified conversation ID anyway.[/]")
    
    # Send the message
    try:
        console.print("[dim]Sending query to Claude...[/]")
        if attachment:
            console.print(f"[dim]With attachment: {attachment}[/]")
            response = claude.send_message(prompt, conversation_id, attachment=attachment)
        else:
            response = claude.send_message(prompt, conversation_id)
        
        return response
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)