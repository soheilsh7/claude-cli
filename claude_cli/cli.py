#!/usr/bin/env python3
import os
import click
import sys
from rich.console import Console
from rich.markdown import Markdown

from claude_cli.config import load_config, save_config
from claude_cli.commands.chat import start_chat
from claude_cli.commands.query import send_query
from claude_cli.commands.manage import list_conversations, delete_conversation, rename_conversation

console = Console()

@click.group()
@click.version_option()
def cli():
    """Command-line interface for Claude AI"""
    pass

@cli.command()
@click.option("--new", is_flag=True, help="Start a new conversation")
@click.option("--id", help="Continue an existing conversation by ID")
def chat(new, id):
    """Start an interactive chat session with Claude"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    start_chat(config, new_chat=new, conversation_id=id)

@cli.command()
@click.argument("prompt")
@click.option("--id", help="Use a specific conversation ID")
@click.option("--attachment", "-a", help="Path to a file to attach")
@click.option("--markdown/--no-markdown", default=True, help="Render output as markdown")
def query(prompt, id, attachment, markdown):
    """Send a one-off query to Claude"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    response = send_query(config, prompt, conversation_id=id, attachment=attachment)
    
    if markdown:
        console.print(Markdown(response))
    else:
        console.print(response)

@cli.command()
def list():
    """List all your Claude conversations"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    list_conversations(config)

@cli.command()
@click.argument("conversation_id")
def delete(conversation_id):
    """Delete a conversation by ID"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    delete_conversation(config, conversation_id)

@cli.command()
@click.argument("conversation_id")
@click.argument("new_title")
def rename(conversation_id, new_title):
    """Rename a conversation"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    rename_conversation(config, conversation_id, new_title)

@cli.command()
@click.option("--cookie", help="Claude AI cookie")
def config(cookie):
    """Configure Claude CLI settings"""
    config = load_config()
    
    if cookie:
        config['cookie'] = cookie
    else:
        cookie_input = click.prompt("Enter your Claude cookie", default=config.get('cookie', ''), hide_input=True)
        if cookie_input:
            config['cookie'] = cookie_input
    
    save_config(config)
    console.print("[green]Configuration saved successfully![/]")

def main():
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()