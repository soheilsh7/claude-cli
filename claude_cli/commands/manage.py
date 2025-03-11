from claude_api import Client
from rich.console import Console
from rich.table import Table
from rich import box
import datetime
import sys

console = Console()

def list_conversations(config):
    """List all available conversations."""
    cookie = config.get('cookie')
    claude = Client(cookie)
    
    try:
        conversations = claude.list_all_conversations()
        
        if not conversations:
            console.print("[yellow]You don't have any conversations yet.[/]")
            return
        
        table = Table(title="Claude Conversations", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Created", style="magenta")
        table.add_column("Messages", style="blue", justify="right")
        
        for conv in sorted(conversations, key=lambda x: x.get('created_at', ''), reverse=True):
            conv_id = conv.get('uuid', 'Unknown')
            name = conv.get('name', 'Untitled') or 'Untitled'
            
            # Format the creation date
            created_at = conv.get('created_at', '')
            if created_at:
                try:
                    # Parse the timestamp and format it
                    dt = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    created_str = created_at
            else:
                created_str = 'Unknown'
            
            # Get message count
            message_count = len(conv.get('chat_messages', []))
            
            table.add_row(conv_id, name, created_str, str(message_count))
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)

def delete_conversation(config, conversation_id):
    """Delete a specific conversation."""
    cookie = config.get('cookie')
    claude = Client(cookie)
    
    try:
        # Confirm before deleting
        confirmed = console.input(f"[yellow]Are you sure you want to delete conversation {conversation_id}? (y/N): [/]").lower()
        if confirmed != 'y':
            console.print("[cyan]Deletion cancelled.[/]")
            return
        
        success = claude.delete_conversation(conversation_id)
        if success:
            console.print(f"[green]Successfully deleted conversation: {conversation_id}[/]")
        else:
            console.print(f"[bold red]Failed to delete conversation: {conversation_id}[/]")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)

def rename_conversation(config, conversation_id, new_title):
    """Rename a specific conversation."""
    cookie = config.get('cookie')
    claude = Client(cookie)
    
    try:
        success = claude.rename_chat(new_title, conversation_id)
        if success:
            console.print(f"[green]Successfully renamed conversation to: {new_title}[/]")
        else:
            console.print(f"[bold red]Failed to rename conversation: {conversation_id}[/]")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)

def view_conversation_history(config, conversation_id):
    """View the message history of a specific conversation."""
    cookie = config.get('cookie')
    claude = Client(cookie)
    
    try:
        history = claude.chat_conversation_history(conversation_id)
        
        if not history or 'chat_messages' not in history or not history['chat_messages']:
            console.print("[yellow]This conversation doesn't have any messages.[/]")
            return
        
        name = history.get('name', 'Untitled') or 'Untitled'
        console.print(f"[bold]Conversation:[/] {name} ({conversation_id})")
        
        for i, message in enumerate(history['chat_messages']):
            role = "You" if message['sender'] == 'human' else "Claude"
            content = message['message']['content'][0]['text']
            
            if i > 0:  # Add separator between messages
                console.print("─" * 50)
            
            console.print(f"[bold {'green' if role == 'You' else 'purple'}]{role}:[/]")
            console.print(content)
    
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)