import os
import sys
from claude_api import Client
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def start_chat(config, new_chat=False, conversation_id=None):
    """Start an interactive chat session with Claude."""
    cookie = config.get('cookie')
    claude = Client(cookie)
    
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
        pass
    
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
                    response = claude.send_message(message, conversation_id, attachment=file_path)
                    console.print("[bold purple]Claude:[/]")
                    console.print(Markdown(response))
                except Exception as e:
                    console.print(f"[bold red]Error sending attachment:[/] {str(e)}")
                continue
                
            # Regular message
            console.print("[cyan]Thinking...[/]")
            try:
                response = claude.send_message(user_input, conversation_id)
                console.print("[bold purple]Claude:[/]")
                console.print(Markdown(response))
            except Exception as e:
                console.print(f"[bold red]Error:[/] {str(e)}")
    
    except KeyboardInterrupt:
        console.print("\n[bold]Exiting chat. Goodbye![/]")
        sys.exit(0)

def show_help():
    """Show help for chat commands"""
    console.print("""
[bold]Available Commands:[/]
- [cyan]exit[/]: Exit the chat
- [cyan]help[/]: Show this help message
- [cyan]clear[/]: Clear the screen
- [cyan]attach [file][/]: Attach a file to your next message
""")