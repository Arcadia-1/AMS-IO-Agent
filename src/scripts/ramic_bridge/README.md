# RAMIC Bridge

RAMIC (Remote Access to Microelectronics IC) bridge for communicating with Cadence Virtuoso.

## Components

- `ramic_bridge.py` - Python bridge client
- `ramic_bridge.il` - SKILL server implementation
- `ramic_bridge_daemon_27.py` - Daemon for Virtuoso 6.1.7

## Usage

Enables Python agents to execute SKILL code remotely in Virtuoso via socket communication.

## Configuration

Set `RB_HOST` and `RB_PORT` environment variables or in `.env` file.

