# Claude CLI

A command-line interface for interacting with Claude AI.

![Claude CLI Demo](https://via.placeholder.com/650x350)

## Features

- Interactive chat with Claude AI in your terminal
- Send one-off queries without entering an interactive session
- Manage your conversations (list, delete, rename)
- Support for file attachments
- Rich text formatting (markdown)
- Configuration management

## Installation

### From PyPI

```bash
pip install claudeshell
```

### From Source

```bash
git clone https://github.com/yourusername/claude-cli.git
cd claude-cli
pip install -e .
```

## Setup

Before using Claude CLI, you need to configure your Claude cookie:

```bash
claude config
```

This will prompt you to enter your Claude cookie. Alternatively, you can set the `CLAUDE_COOKIE` environment variable.

### Getting Your Claude Cookie

1. Go to [claude.ai](https://claude.ai) and log in
2. Open your browser's developer tools (F12 or right-click > Inspect)
3. Go to the Network tab
4. Refresh the page
5. Click on any request to claude.ai
6. In the Headers tab, find the Cookie header
7. Copy the entire cookie value

## Usage

### Interactive Chat

Start a new chat conversation:

```bash
claude chat --new
```

Continue an existing conversation:

```bash
claude chat --id <conversation_id>
```

### One-off Queries

Send a single query and get a response:

```bash
claude query "What is the capital of France?"
```

With attachment:

```bash
claude query "Summarize this document" --attachment path/to/file.pdf
```

### Managing Conversations

List all conversations:

```bash
claude list
```

Delete a conversation:

```bash
claude delete <conversation_id>
```

Rename a conversation:

```bash
claude rename <conversation_id> "New Title"
```

## Commands Reference

- `claude chat`: Start an interactive chat session
- `claude query`: Send a one-off query
- `claude list`: List all conversations
- `claude delete`: Delete a conversation
- `claude rename`: Rename a conversation
- `claude config`: Configure settings

## Dependencies

- [claude-api](https://github.com/KoushikNavuluri/Claude-API): Unofficial Claude API
- click: Command-line interface creation
- rich: Terminal text formatting and display
- pyyaml: Configuration file handling

## License

MIT

## Disclaimer

This project provides an unofficial client for Claude AI and is not affiliated with or endorsed by Anthropic. Use it at your own risk.