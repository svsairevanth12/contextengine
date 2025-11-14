"""
Memory Manager - Manages short-term and long-term memory for conversation sessions.
Stores session information, conversation history, and user preferences.
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib


class MemoryManager:
    """Manages session memory and conversation history."""

    def __init__(
        self,
        session_directory: str = "./data/sessions",
        max_history_items: int = 100,
        save_interval: int = 5
    ):
        """
        Initialize the memory manager.

        Args:
            session_directory: Directory to store session files
            max_history_items: Maximum number of conversation items to keep
            save_interval: Save session every N interactions
        """
        self.logger = logging.getLogger(__name__)
        self.session_directory = Path(session_directory)
        self.max_history_items = max_history_items
        self.save_interval = save_interval

        # Create session directory if it doesn't exist
        self.session_directory.mkdir(parents=True, exist_ok=True)

        # Current session state
        self.current_session_id: Optional[str] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_metadata: Dict[str, Any] = {}
        self.interaction_count: int = 0

        self.logger.info(f"Memory manager initialized at {session_directory}")

    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session.

        Args:
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            Session ID
        """
        if session_id is None:
            # Generate session ID from timestamp
            timestamp = datetime.now().isoformat()
            session_id = hashlib.md5(timestamp.encode()).hexdigest()[:16]

        self.current_session_id = session_id
        self.conversation_history = []
        self.session_metadata = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'interaction_count': 0
        }
        self.interaction_count = 0

        self.logger.info(f"Created new session: {session_id}")
        return session_id

    def load_session(self, session_id: str) -> bool:
        """
        Load an existing session.

        Args:
            session_id: ID of the session to load

        Returns:
            True if session loaded successfully, False otherwise
        """
        session_file = self.session_directory / f"{session_id}.json"

        if not session_file.exists():
            self.logger.warning(f"Session file not found: {session_file}")
            return False

        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)

            self.current_session_id = session_id
            self.conversation_history = session_data.get('conversation_history', [])
            self.session_metadata = session_data.get('metadata', {})
            self.interaction_count = self.session_metadata.get('interaction_count', 0)

            self.logger.info(f"Loaded session: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error loading session: {e}")
            return False

    def save_session(self) -> bool:
        """
        Save the current session to disk.

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.current_session_id:
            self.logger.warning("No active session to save")
            return False

        try:
            session_file = self.session_directory / f"{self.current_session_id}.json"

            # Update metadata
            self.session_metadata['last_updated'] = datetime.now().isoformat()
            self.session_metadata['interaction_count'] = self.interaction_count

            session_data = {
                'metadata': self.session_metadata,
                'conversation_history': self.conversation_history
            }

            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            self.logger.debug(f"Saved session: {self.current_session_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            return False

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: Role of the message sender (user, assistant, system)
            content: Message content
            metadata: Optional metadata for the message
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.conversation_history.append(message)

        # Trim history if it exceeds max items
        if len(self.conversation_history) > self.max_history_items:
            self.conversation_history = self.conversation_history[-self.max_history_items:]

        self.interaction_count += 1

        # Auto-save based on interval
        if self.interaction_count % self.save_interval == 0:
            self.save_session()

    def get_conversation_history(
        self,
        last_n: Optional[int] = None,
        role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            last_n: Get only the last N messages
            role_filter: Filter by role (user, assistant, system)

        Returns:
            List of messages
        """
        history = self.conversation_history

        # Filter by role if specified
        if role_filter:
            history = [msg for msg in history if msg['role'] == role_filter]

        # Get last N messages if specified
        if last_n:
            history = history[-last_n:]

        return history

    def get_context_summary(self, last_n: int = 5) -> str:
        """
        Get a formatted summary of recent conversation.

        Args:
            last_n: Number of recent messages to include

        Returns:
            Formatted conversation summary
        """
        recent_messages = self.get_conversation_history(last_n=last_n)

        if not recent_messages:
            return "No conversation history."

        summary_parts = ["Recent Conversation:"]
        for msg in recent_messages:
            role = msg['role'].upper()
            content = msg['content'][:200]  # Truncate long messages
            summary_parts.append(f"{role}: {content}")

        return '\n'.join(summary_parts)

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        self.interaction_count = 0
        self.logger.info("Conversation history cleared")

    def delete_session(self, session_id: Optional[str] = None) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete (current session if not specified)

        Returns:
            True if deleted successfully
        """
        sid = session_id or self.current_session_id

        if not sid:
            self.logger.warning("No session to delete")
            return False

        try:
            session_file = self.session_directory / f"{sid}.json"
            if session_file.exists():
                session_file.unlink()
                self.logger.info(f"Deleted session: {sid}")

                if sid == self.current_session_id:
                    self.current_session_id = None
                    self.conversation_history = []
                    self.session_metadata = {}

                return True

        except Exception as e:
            self.logger.error(f"Error deleting session: {e}")

        return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions.

        Returns:
            List of session info dictionaries
        """
        sessions = []

        try:
            for session_file in self.session_directory.glob("*.json"):
                with open(session_file, 'r') as f:
                    session_data = json.load(f)

                metadata = session_data.get('metadata', {})
                sessions.append({
                    'session_id': metadata.get('session_id', session_file.stem),
                    'created_at': metadata.get('created_at', 'unknown'),
                    'last_updated': metadata.get('last_updated', 'unknown'),
                    'interaction_count': metadata.get('interaction_count', 0)
                })

        except Exception as e:
            self.logger.error(f"Error listing sessions: {e}")

        return sessions

    def export_session(
        self,
        output_file: str,
        session_id: Optional[str] = None,
        format: str = "json"
    ) -> bool:
        """
        Export a session to a file.

        Args:
            output_file: Output file path
            session_id: Session ID to export (current if not specified)
            format: Export format (json, txt)

        Returns:
            True if exported successfully
        """
        sid = session_id or self.current_session_id

        if not sid:
            self.logger.warning("No session to export")
            return False

        try:
            # Load session if not current
            if sid != self.current_session_id:
                session_file = self.session_directory / f"{sid}.json"
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
            else:
                session_data = {
                    'metadata': self.session_metadata,
                    'conversation_history': self.conversation_history
                }

            if format == "json":
                with open(output_file, 'w') as f:
                    json.dump(session_data, f, indent=2)

            elif format == "txt":
                with open(output_file, 'w') as f:
                    f.write(f"Session: {sid}\n")
                    f.write(f"Created: {session_data['metadata'].get('created_at', 'unknown')}\n")
                    f.write("=" * 60 + "\n\n")

                    for msg in session_data['conversation_history']:
                        f.write(f"{msg['role'].upper()} [{msg['timestamp']}]:\n")
                        f.write(f"{msg['content']}\n\n")

            self.logger.info(f"Exported session to {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting session: {e}")
            return False

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about the current session."""
        if not self.current_session_id:
            return {}

        user_messages = len([m for m in self.conversation_history if m['role'] == 'user'])
        assistant_messages = len([m for m in self.conversation_history if m['role'] == 'assistant'])

        return {
            'session_id': self.current_session_id,
            'total_messages': len(self.conversation_history),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'interaction_count': self.interaction_count,
            'created_at': self.session_metadata.get('created_at', 'unknown'),
            'last_updated': self.session_metadata.get('last_updated', 'unknown')
        }


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    # Initialize memory manager
    manager = MemoryManager(session_directory="./test_sessions")

    # Create a new session
    session_id = manager.create_session()
    print(f"Created session: {session_id}")

    # Add some messages
    manager.add_message("user", "Hello, can you help me with Python?")
    manager.add_message("assistant", "Of course! I'd be happy to help with Python.")
    manager.add_message("user", "How do I read a file?")

    # Get conversation history
    history = manager.get_conversation_history()
    print(f"\nConversation history ({len(history)} messages):")
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")

    # Save session
    manager.save_session()

    # Get stats
    stats = manager.get_session_stats()
    print(f"\nSession stats: {stats}")

    # Export session
    manager.export_session("./test_export.txt", format="txt")

    # Cleanup
    manager.delete_session()
    import shutil
    if os.path.exists("./test_sessions"):
        shutil.rmtree("./test_sessions")
    if os.path.exists("./test_export.txt"):
        os.remove("./test_export.txt")

    print("\nTest completed")
