"""Prompt management with role-based templates"""

from typing import Dict, Optional
from src.config import SYSTEM_ROLES


class PromptManager:
    """Manages prompts with different roles and contexts"""

    def __init__(self):
        self.system_roles = SYSTEM_ROLES
        self.conversation_history = []

    def create_prompt(
        self,
        question: str,
        role: str = "qa",
        context: Optional[str] = None
    ) -> str:
        """
        Create a formatted prompt with role-based system message
        
        Args:
            question: User question
            role: Role type (qa, tutor, creative, assistant)
            context: Optional context/background information
            
        Returns:
            Formatted prompt string
        """
        if role not in self.system_roles:
            role = "qa"
        
        system_message = self.system_roles[role]
        
        # Build prompt with system role
        prompt_parts = [system_message]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        prompt_parts.append(f"\nQuestion: {question}")
        prompt_parts.append("\nAnswer:")
        
        prompt = "\n".join(prompt_parts)
        return prompt

    def create_conversational_prompt(
        self,
        question: str,
        role: str = "qa"
    ) -> str:
        """
        Create a prompt using conversation history
        
        Args:
            question: Current question
            role: Role type
            
        Returns:
            Formatted prompt with history
        """
        system_message = self.system_roles.get(role, self.system_roles["qa"])
        
        prompt_parts = [system_message]
        
        # Add conversation history (last 3 exchanges)
        if self.conversation_history:
            prompt_parts.append("\nConversation History:")
            for q, a in self.conversation_history[-3:]:
                prompt_parts.append(f"Q: {q}")
                prompt_parts.append(f"A: {a}")
        
        prompt_parts.append(f"\nQ: {question}")
        prompt_parts.append("A:")
        
        return "\n".join(prompt_parts)

    def add_to_history(self, question: str, answer: str):
        """Add Q&A pair to conversation history"""
        self.conversation_history.append((question, answer))

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()

    def get_available_roles(self) -> Dict[str, str]:
        """Get all available roles and their descriptions"""
        return self.system_roles
