"""
MCP Prompts - Provides prompt templates for common coding tasks.
"""

import logging
from typing import Dict, Any, List, Optional


class MCPPrompts:
    """Implements MCP prompt templates for context engine."""

    def __init__(self, context_engine):
        """
        Initialize MCP prompts.

        Args:
            context_engine: ContextEngine instance
        """
        self.engine = context_engine
        self.logger = logging.getLogger(__name__)

    def get_prompt_definitions(self) -> List[Dict[str, Any]]:
        """Get list of available prompt templates."""
        return [
            {
                "name": "analyze_feature",
                "description": "Analyze how a feature is implemented in the codebase",
                "arguments": [
                    {
                        "name": "feature",
                        "description": "Feature to analyze (e.g., 'authentication', 'database layer')",
                        "required": True
                    }
                ]
            },
            {
                "name": "debug_error",
                "description": "Find code related to a specific error or bug",
                "arguments": [
                    {
                        "name": "error_message",
                        "description": "Error message or description",
                        "required": True
                    },
                    {
                        "name": "context",
                        "description": "Additional context about when the error occurs",
                        "required": False
                    }
                ]
            },
            {
                "name": "implement_similar",
                "description": "Implement a feature similar to an existing one",
                "arguments": [
                    {
                        "name": "new_feature",
                        "description": "Feature to implement",
                        "required": True
                    },
                    {
                        "name": "similar_to",
                        "description": "Existing feature to base implementation on",
                        "required": True
                    }
                ]
            },
            {
                "name": "refactor_code",
                "description": "Refactor code following existing patterns in the codebase",
                "arguments": [
                    {
                        "name": "target",
                        "description": "What to refactor (e.g., 'authentication system')",
                        "required": True
                    },
                    {
                        "name": "goal",
                        "description": "Refactoring goal (e.g., 'improve performance', 'add typing')",
                        "required": True
                    }
                ]
            },
            {
                "name": "add_tests",
                "description": "Add tests for a feature following existing test patterns",
                "arguments": [
                    {
                        "name": "feature",
                        "description": "Feature to test",
                        "required": True
                    }
                ]
            },
            {
                "name": "find_dependencies",
                "description": "Find dependencies and usage of a specific component",
                "arguments": [
                    {
                        "name": "component",
                        "description": "Component name (class, function, module)",
                        "required": True
                    }
                ]
            }
        ]

    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a prompt template with arguments filled in.

        Args:
            name: Prompt name
            arguments: Prompt arguments

        Returns:
            Prompt with context
        """
        try:
            if name == "analyze_feature":
                return self._analyze_feature_prompt(**arguments)
            elif name == "debug_error":
                return self._debug_error_prompt(**arguments)
            elif name == "implement_similar":
                return self._implement_similar_prompt(**arguments)
            elif name == "refactor_code":
                return self._refactor_code_prompt(**arguments)
            elif name == "add_tests":
                return self._add_tests_prompt(**arguments)
            elif name == "find_dependencies":
                return self._find_dependencies_prompt(**arguments)
            else:
                return {
                    "error": f"Unknown prompt: {name}",
                    "available_prompts": [p["name"] for p in self.get_prompt_definitions()]
                }

        except Exception as e:
            self.logger.error(f"Error getting prompt {name}: {e}")
            return {
                "error": str(e),
                "prompt": name
            }

    def _analyze_feature_prompt(self, feature: str) -> Dict[str, Any]:
        """Generate prompt for analyzing a feature."""
        # Search for the feature
        context = self.engine.query(
            query=f"{feature} implementation architecture",
            top_k=10,
            include_conversation=False
        )

        prompt = f"""Analyze how the '{feature}' feature is implemented in this codebase.

## Relevant Code Found:

{context.context_text}

## Analysis Tasks:

1. **Architecture**: Describe the overall architecture and design patterns used
2. **Key Components**: Identify the main classes, functions, and modules
3. **Data Flow**: Explain how data flows through the system
4. **Dependencies**: List important dependencies and integrations
5. **Potential Issues**: Note any potential problems or areas for improvement

Please provide a comprehensive analysis based on the code above.
"""

        return {
            "success": True,
            "prompt_name": "analyze_feature",
            "prompt": prompt,
            "context_chunks": len(context.chunks_used),
            "context_tokens": context.total_tokens
        }

    def _debug_error_prompt(
        self,
        error_message: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate prompt for debugging an error."""
        # Search for error-related code
        search_query = f"{error_message}"
        if context:
            search_query += f" {context}"

        code_context = self.engine.query(
            query=search_query,
            top_k=8,
            include_conversation=False
        )

        prompt = f"""Debug the following error in the codebase:

**Error Message**: {error_message}
{f"**Context**: {context}" if context else ""}

## Relevant Code:

{code_context.context_text}

## Debugging Steps:

1. **Locate the Issue**: Identify where in the code this error occurs
2. **Root Cause**: Determine what's causing the error
3. **Related Code**: Find related code that might be affected
4. **Fix Strategy**: Suggest how to fix the error
5. **Prevention**: Recommend how to prevent similar errors

Please provide a detailed debugging analysis.
"""

        return {
            "success": True,
            "prompt_name": "debug_error",
            "prompt": prompt,
            "context_chunks": len(code_context.chunks_used),
            "context_tokens": code_context.total_tokens
        }

    def _implement_similar_prompt(
        self,
        new_feature: str,
        similar_to: str
    ) -> Dict[str, Any]:
        """Generate prompt for implementing a feature similar to an existing one."""
        # Search for the existing feature
        existing_context = self.engine.query(
            query=f"{similar_to} implementation",
            top_k=10,
            include_conversation=False
        )

        prompt = f"""Implement '{new_feature}' based on the existing '{similar_to}' implementation.

## Existing Implementation to Follow:

{existing_context.context_text}

## Implementation Guidelines:

1. **Follow Patterns**: Use the same architectural patterns as the existing feature
2. **Code Style**: Match the coding style and conventions
3. **File Structure**: Place files in similar locations
4. **Dependencies**: Use similar dependencies and integrations
5. **Testing**: Add tests following the same patterns

**Task**: Implement '{new_feature}' following the patterns shown above.

Please provide the implementation plan and code.
"""

        return {
            "success": True,
            "prompt_name": "implement_similar",
            "prompt": prompt,
            "context_chunks": len(existing_context.chunks_used),
            "context_tokens": existing_context.total_tokens
        }

    def _refactor_code_prompt(self, target: str, goal: str) -> Dict[str, Any]:
        """Generate prompt for refactoring code."""
        # Search for the target code
        target_context = self.engine.query(
            query=f"{target} current implementation",
            top_k=10,
            include_conversation=False
        )

        # Search for similar refactored code as examples
        example_context = self.engine.query(
            query=f"{goal} best practices examples",
            top_k=5,
            include_conversation=False
        )

        prompt = f"""Refactor '{target}' with the goal: {goal}

## Current Implementation:

{target_context.context_text}

## Reference Examples:

{example_context.context_text}

## Refactoring Plan:

1. **Current State**: Analyze the current implementation
2. **Improvements**: Identify what needs to change
3. **Strategy**: Plan the refactoring approach
4. **Implementation**: Show the refactored code
5. **Testing**: Ensure functionality is preserved
6. **Migration**: Plan for migrating to new code

Please provide a detailed refactoring plan and implementation.
"""

        return {
            "success": True,
            "prompt_name": "refactor_code",
            "prompt": prompt,
            "context_chunks": len(target_context.chunks_used) + len(example_context.chunks_used),
            "context_tokens": target_context.total_tokens + example_context.total_tokens
        }

    def _add_tests_prompt(self, feature: str) -> Dict[str, Any]:
        """Generate prompt for adding tests."""
        # Search for the feature to test
        feature_context = self.engine.query(
            query=f"{feature} implementation",
            top_k=8,
            include_conversation=False
        )

        # Search for existing test patterns
        test_context = self.engine.query(
            query="test examples patterns",
            top_k=5,
            include_conversation=False
        )

        prompt = f"""Add comprehensive tests for '{feature}'.

## Code to Test:

{feature_context.context_text}

## Existing Test Patterns:

{test_context.context_text}

## Testing Requirements:

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **Edge Cases**: Test boundary conditions and errors
4. **Coverage**: Ensure good test coverage
5. **Mocking**: Mock external dependencies appropriately

**Task**: Write comprehensive tests for '{feature}' following the patterns above.

Please provide the test implementation.
"""

        return {
            "success": True,
            "prompt_name": "add_tests",
            "prompt": prompt,
            "context_chunks": len(feature_context.chunks_used) + len(test_context.chunks_used),
            "context_tokens": feature_context.total_tokens + test_context.total_tokens
        }

    def _find_dependencies_prompt(self, component: str) -> Dict[str, Any]:
        """Generate prompt for finding dependencies."""
        # Search for the component
        component_context = self.engine.query(
            query=f"{component} definition usage",
            top_k=15,
            include_conversation=False
        )

        prompt = f"""Find all dependencies and usage of '{component}'.

## Component and Usage:

{component_context.context_text}

## Analysis Required:

1. **Definition**: Where is '{component}' defined?
2. **Direct Usage**: What code directly uses this component?
3. **Indirect Dependencies**: What depends on code that uses this?
4. **Imports**: What modules import this component?
5. **Impact**: What would break if this component changed?

Please provide a complete dependency analysis.
"""

        return {
            "success": True,
            "prompt_name": "find_dependencies",
            "prompt": prompt,
            "context_chunks": len(component_context.chunks_used),
            "context_tokens": component_context.total_tokens
        }
