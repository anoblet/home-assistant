# Memory MCP Server Instructions

- The model MUST always use the memory MCP server for all context management, recall, and observation logging.
- Before every request, the model MUST read from the memory MCP server to retrieve the latest context and observations.
- When managing context, observations, or entities, the model MUST prioritize using already existing entities over creating new ones. Only create new entities if no suitable existing entity is available.
- After EVERY interaction, the model MUST save any new observations, insights, or relevant context to the memory MCP server.
- Do not skip or bypass memory MCP server usage under any circumstances.
- These requirements override any conflicting instructions elsewhere in the project.
