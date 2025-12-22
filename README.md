# Chainlit MCP File Agent

Chainlit 기반 MCP 에이전트 - 파일 읽기 기능을 제공하는 대화형 AI 에이전트

## 🎯 목표

FastMCP를 사용하여 파일 읽기 기능을 제공하는 MCP 서버와, 이를 활용하는 Chainlit 기반 대화형 에이전트 구현

## 🛠️ 기술 스택

- **환경**: Linux, uv
- **UI**: Chainlit
- **LLM**: OpenAI Compatible API
- **MCP**: FastMCP SSE (Server-Sent Events)

## 📁 프로젝트 구조

```
chainlit-1/
├── pyproject.toml      # 프로젝트 의존성 설정
├── .env.example        # 환경 변수 템플릿
├── .env                # 환경 변수 (생성 필요)
├── mcp_server.py       # FastMCP 파일 읽기 서버
├── mcp_client.py       # SSE 클라이언트
└── app.py              # Chainlit 메인 애플리케이션
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 API 키 설정
# OPENAI_API_KEY=your-api-key-here
```

### 3. MCP 서버 실행

터미널 1에서:
```bash
uv run python mcp_server.py
```

서버가 `http://localhost:8000/sse` 에서 실행됩니다.

### 4. Chainlit 앱 실행

터미널 2에서:
```bash
uv run chainlit run app.py
```

브라우저에서 `http://localhost:8000` (또는 Chainlit이 지정한 포트)로 접속합니다.

## 💡 사용 예시

### 파일 읽기
```
사용자: README.md 파일의 내용을 읽어줘
에이전트: [read_file 도구 호출] → 파일 내용 표시
```

### 디렉토리 목록
```
사용자: 현재 디렉토리의 파일 목록을 보여줘
에이전트: [list_files 도구 호출] → 파일 목록 표시
```

### 파일 분석
```
사용자: pyproject.toml에 어떤 의존성이 있어?
에이전트: [read_file 도구 호출] → 파일 읽기 → 의존성 분석 및 설명
```

## 🔧 구성 요소

### MCP 서버 (mcp_server.py)

FastMCP를 사용하여 다음 도구를 제공:

- **read_file**: 파일 내용 읽기
- **list_files**: 디렉토리 파일 목록 조회

SSE (Server-Sent Events) 방식으로 통신합니다.

### MCP 클라이언트 (mcp_client.py)

MCP 서버와 SSE로 통신하는 클라이언트:

- 도구 목록 조회
- 도구 호출 및 결과 반환
- OpenAI 함수 호출 형식으로 변환

### Chainlit 앱 (app.py)

사용자와 상호작용하는 메인 애플리케이션:

- 채팅 인터페이스 제공
- LLM에게 사용 가능한 도구 전달
- 도구 호출 결과를 LLM에 전달하여 응답 생성

## 🔄 실행 흐름

```
사용자 질문
    ↓
Chainlit 앱 (app.py)
    ↓
LLM (OpenAI API)
    ↓
도구 호출 필요 판단
    ↓
MCP 클라이언트 (mcp_client.py)
    ↓
MCP 서버 (mcp_server.py)
    ↓
파일 시스템 작업
    ↓
결과 반환
    ↓
LLM이 결과 해석
    ↓
사용자에게 응답
```

## 🔑 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | (필수) |
| `OPENAI_BASE_URL` | API 엔드포인트 URL | `https://api.openai.com/v1` |
| `MODEL_NAME` | 사용할 모델 이름 | `gpt-4` |
| `MAX_TOKENS` | 최대 토큰 수 | `2000` |
| `TEMPERATURE` | 응답 다양성 (0-1) | `0.7` |
| `MCP_SERVER_URL` | MCP 서버 URL | `http://localhost:8000` |

## 🧪 테스트

MCP 클라이언트 테스트:
```bash
uv run python mcp_client.py
```

## 📝 개발 노트

### MCP 서버 커스터마이징

`mcp_server.py`에 새로운 도구 추가:

```python
@mcp.tool()
def your_new_tool(param: str) -> str:
    """도구 설명"""
    # 구현
    return result
```

### 다른 LLM 사용

Ollama 등 OpenAI 호환 API를 사용하는 경우 `.env` 파일에서 설정:

```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama  # Ollama는 API 키가 필요없지만 형식상 필요
MODEL_NAME=llama2
```

## 🐛 문제 해결

### MCP 서버 연결 오류
- MCP 서버가 실행 중인지 확인
- 포트 8000이 사용 가능한지 확인

### LLM 응답 없음
- API 키가 올바르게 설정되었는지 확인
- 네트워크 연결 확인

### 파일 읽기 권한 오류
- 읽으려는 파일의 권한 확인
- 상대 경로 대신 절대 경로 사용 고려

## 📚 참고 자료

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Chainlit Documentation](https://docs.chainlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 📄 라이선스

MIT License