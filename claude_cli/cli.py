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
@click.option("--proxy", help="Proxy URL (e.g., socks5://127.0.0.1:1080)")
@click.option("--debug", is_flag=True, help="Show debug information")
def chat(new, id, proxy, debug):
    """Start an interactive chat session with Claude"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    # Use proxy from config if not provided in command
    if not proxy and 'proxy' in config:
        proxy = config.get('proxy')
        
    start_chat(config, new_chat=new, conversation_id=id, proxy=proxy, debug=debug)

@cli.command()
@click.argument("prompt")
@click.option("--id", help="Use a specific conversation ID")
@click.option("--attachment", "-a", help="Path to a file to attach")
@click.option("--markdown/--no-markdown", default=True, help="Render output as markdown")
@click.option("--proxy", help="Proxy URL (e.g., socks5://127.0.0.1:1080)")
@click.option("--debug", is_flag=True, help="Show debug information")
def query(prompt, id, attachment, markdown, proxy, debug):
    """Send a one-off query to Claude"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    # Use proxy from config if not provided in command
    if not proxy and 'proxy' in config:
        proxy = config.get('proxy')
        
    response = send_query(config, prompt, conversation_id=id, attachment=attachment, proxy=proxy, debug=debug)
    
    if markdown:
        console.print(Markdown(response))
    else:
        console.print(response)

@cli.command()
@click.option("--proxy", help="Proxy URL (e.g., socks5://127.0.0.1:1080)")
@click.option("--debug", is_flag=True, help="Show debug information")
def list(proxy, debug):
    """List all your Claude conversations"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    # Use proxy from config if not provided in command
    if not proxy and 'proxy' in config:
        proxy = config.get('proxy')
        
    list_conversations(config, proxy=proxy, debug=debug)

@cli.command()
@click.argument("conversation_id")
@click.option("--proxy", help="Proxy URL (e.g., socks5://127.0.0.1:1080)")
@click.option("--debug", is_flag=True, help="Show debug information")
def delete(conversation_id, proxy, debug):
    """Delete a conversation by ID"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    # Use proxy from config if not provided in command
    if not proxy and 'proxy' in config:
        proxy = config.get('proxy')
        
    delete_conversation(config, conversation_id, proxy=proxy, debug=debug)

@cli.command()
@click.argument("conversation_id")
@click.argument("new_title")
@click.option("--proxy", help="Proxy URL (e.g., socks5://127.0.0.1:1080)")
@click.option("--debug", is_flag=True, help="Show debug information")
def rename(conversation_id, new_title, proxy, debug):
    """Rename a conversation"""
    config = load_config()
    if not config.get('cookie'):
        console.print("[bold red]Error:[/] Claude cookie not found. Please run 'claude config' to set it up.")
        sys.exit(1)
        
    # Use proxy from config if not provided in command
    if not proxy and 'proxy' in config:
        proxy = config.get('proxy')
        
    rename_conversation(config, conversation_id, new_title, proxy=proxy, debug=debug)

@cli.command()
@click.option("--cookie", help="Claude AI cookie")
@click.option("--proxy", help="Default proxy URL (e.g., socks5://127.0.0.1:1080)")
def config(cookie, proxy):
    """Configure Claude CLI settings"""
    config = load_config()
    
    if cookie:
        config['cookie'] = cookie
    elif not config.get('cookie'):
        cookie_input = click.prompt("Enter your Claude cookie", default=config.get('cookie', ''), hide_input=True)
        if cookie_input:
            config['cookie'] = cookie_input
    
    if proxy:
        config['proxy'] = proxy
        console.print(f"[green]Default proxy set to: {proxy}[/]")
    elif proxy == "":
        # Empty string means remove proxy
        if 'proxy' in config:
            del config['proxy']
            console.print("[green]Default proxy removed[/]")
    elif 'proxy' not in config:
        use_proxy = click.confirm("Do you want to set up a default proxy?", default=False)
        if use_proxy:
            proxy_input = click.prompt("Enter proxy URL (e.g., socks5://127.0.0.1:1080)")
            if proxy_input:
                config['proxy'] = proxy_input
                console.print(f"[green]Default proxy set to: {proxy_input}[/]")
    
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