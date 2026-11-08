import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .config import ROOT

async def invoke(name, args):
    params=StdioServerParameters(command=sys.executable,args=['-m','backend.mcp_server'],cwd=str(ROOT),env=dict(os.environ))
    tool_error=None
    result=None
    names=[]
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            listing=await session.list_tools()
            names=[tool.name for tool in listing.tools]
            if name not in names:
                raise ValueError('MCP tool was not discovered.')
            response=await session.call_tool(name,args)
            content='\n'.join(item.text for item in response.content if item.type=='text')
            if response.isError:
                tool_error='MCP tool failed: '+content[:300]
            else:
                try:
                    result=json.loads(content)
                except ValueError:
                    result={'text':content}
    if tool_error:
        raise ValueError(tool_error)
    return {'transport':'stdio','discovered_tools':names,'tool':name,'result':result}
