# Claude CLI

A command-line interface for interacting with Claude AI.

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
git clone https://github.com/soheilsh7/claude-cli.git
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

Visit [here](https://github.com/KoushikNavuluri/Claude-API?tab=readme-ov-file#usage) for more description on how to get your session key.

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

# Using Claude Terminal with a Proxy

Claude Terminal now includes built-in proxy support, so you don't need to use external tools like `proxychains`. Here's how to use it:

## Setting a Default Proxy

You can configure a default proxy that will be used for all commands:

```bash
claude config --proxy socks5://127.0.0.1:2080
```

This saves the proxy in your config file (~/.config/claude-terminal/config.yaml).

To remove the default proxy:

```bash
claude config --proxy ""
```

## Using a One-Time Proxy

You can also specify a proxy for a single command:

```bash
claude chat --proxy socks5://127.0.0.1:2080
claude query "Hello" --proxy socks5://127.0.0.1:2080
claude list --proxy socks5://127.0.0.1:2080
```

The `--proxy` parameter takes precedence over any default proxy configured.

## Supported Proxy Formats

- SOCKS5: `socks5://127.0.0.1:1080`
- SOCKS4: `socks4://127.0.0.1:1080`
- HTTP: `http://127.0.0.1:8080`
- HTTPS: `https://127.0.0.1:8080`

## Authentication

If your proxy requires authentication, include username and password:

```
socks5://username:password@127.0.0.1:1080
```

## Troubleshooting

If you encounter issues with the proxy:

1. Verify your proxy is running correctly
2. Check that the proxy URL format is correct
3. Ensure your proxy allows connections to claude.ai
4. Try with verbose output: `claude chat --proxy your_proxy_url --verbose`

## Security Note

Proxy settings are stored in plain text in your config file. If this is a concern, use the command-line `--proxy` parameter instead of the saved configuration.

## Dependencies

- [claude-api](https://github.com/KoushikNavuluri/Claude-API): Unofficial Claude API
- click: Command-line interface creation
- rich: Terminal text formatting and display
- pyyaml: Configuration file handling

## License

MIT

## Disclaimer

This project provides an unofficial client for Claude AI and is not affiliated with or endorsed by Anthropic. Use it at your own risk.