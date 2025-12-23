import chainlit as cl
from contextlib import AsyncExitStack
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tool import load_mcp_tools
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp import ClientSession

# ============================================
# 1. 채팅 시작 시 - 초기화 단계
# ============================================
@cl.on_chat_start
async def on_chat_start():
    """
    사용자가 채팅을 시작할 때 한 번만 실행
    역할: 여러 MCP 서버 연결 + Agent 생성 + 세션에 저장
    """
    
    # 1-1. AsyncExitStack 생성
    stack = AsyncExitStack()
    
    # 1-2. 여러 MCP 서버 파라미터 설정
    # 역할: 여러 MCP 서버를 리스트로 정의
    servers = [
        StdioServerParameters(
            command="uvx",
            args=["mcp-server-fetch"],
            env=None
        ),
        StdioServerParameters(
            command="uvx",
            args=["mcp-server-filesystem"],
            env=None
        ),
        # 필요한 만큼 추가 가능
        # StdioServerParameters(
        #     command="uvx",
        #     args=["mcp-server-sqlite"],
        #     env=None
        # ),
    ]
    
    # 1-3. 모든 서버에서 tools 수집
    # 역할: 각 서버에 연결하고 모든 tools를 하나의 리스트로 통합
    all_tools = []
    
    for server_params in servers:
        # 1-3-1. stdio_client로 서버 프로세스 실행 및 파이프 연결
        read, write = await stack.enter_async_context(
            stdio_client(server_params)
        )
        
        # 1-3-2. ClientSession 생성 및 초기화
        session = await stack.enter_async_context(
            ClientSession(read, write)
        )
        await session.initialize()
        
        # 1-3-3. 이 서버의 tools를 LangChain Tools로 변환
        tools = await load_mcp_tools(session)
        
        # 1-3-4. 전체 tools 리스트에 추가
        all_tools.extend(tools)
    
    # 1-4. LLM 생성
    llm = ChatOpenAI(model="gpt-4")
    
    # 1-5. 시스템 프롬프트 설정
    system_prompt = SystemMessage(
        content="당신은 친절한 AI 어시스턴트입니다. 한국어로 답변해주세요."
    )
    
    # 1-6. ReAct Agent 생성 (모든 서버의 tools 사용)
    # 역할: 여러 MCP 서버의 모든 tools를 하나의 Agent에 통합
    agent = create_react_agent(
        llm,
        all_tools,  # 모든 서버의 tools
        prompt=system_prompt
    )
    
    # 1-7. 세션에 저장
    cl.user_session.set("agent", agent)
    cl.user_session.set("stack", stack)


# ============================================
# 2. 메시지 수신 시 - 실행 단계
# ============================================
@cl.on_message
async def on_message(message: cl.Message):
    """
    사용자가 메시지를 보낼 때마다 실행
    역할: Agent 실행 + 응답 전송
    """
    
    agent = cl.user_session.get("agent")
    
    config = RunnableConfig(
        callbacks=[cl.LangchainCallbackHandler()],
        recursion_limit=100
    )
    
    response = await agent.ainvoke(
        {"messages": [("user", message.content)]},
        config=config
    )
    
    await cl.Message(content=response["messages"][-1].content).send()


# ============================================
# 3. 채팅 종료 시 - 정리 단계
# ============================================
@cl.on_chat_end
async def on_chat_end():
    """
    사용자가 채팅을 종료할 때 실행
    역할: 모든 MCP 서버 연결 정리
    """
    
    stack = cl.user_session.get("stack")
    
    # 역할: 모든 서버의 연결을 역순으로 종료
    if stack:
        await stack.aclose()
