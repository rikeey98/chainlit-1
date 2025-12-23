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
├── mcp_tools.py        # MCP 도구 구현 (파일 읽기, 목록 조회)
├── app.py              # Chainlit 메인 애플리케이션
├── mcp_server.py       # (선택) FastMCP 서버 예제
└── mcp_client.py       # (선택) SSE 클라이언트 예제
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

### 3. Chainlit 앱 실행

```bash
uv run chainlit run app.py
```

브라우저에서 자동으로 열리는 주소(보통 `http://localhost:8000`)로 접속합니다.

**이제 별도의 MCP 서버 실행이 필요 없습니다!** 모든 도구가 Chainlit 앱 내에서 직접 실행됩니다.

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

### MCP 도구 (mcp_tools.py)

파일 시스템 작업을 위한 도구 구현:

- **read_file**: 파일 내용 읽기
- **list_files**: 디렉토리 파일 목록 조회

OpenAI 함수 호출 형식으로 도구 정의를 제공합니다.

### Chainlit 앱 (app.py)

사용자와 상호작용하는 메인 애플리케이션:

- 채팅 인터페이스 제공
- LLM에게 사용 가능한 도구 전달
- 도구 호출 및 결과를 LLM에 전달하여 응답 생성
- 실시간 스트리밍 응답

### (선택) MCP 서버/클라이언트 예제

별도 프로세스로 MCP 서버를 실행하고 싶은 경우:

- **mcp_server.py**: FastMCP SSE 서버 예제
- **mcp_client.py**: SSE 클라이언트 예제

> 기본 구현에서는 사용하지 않지만, 분리된 아키텍처가 필요한 경우 참고할 수 있습니다.

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
MCP 도구 (mcp_tools.py)
    ↓
파일 시스템 작업
    ↓
결과 반환
    ↓
LLM이 결과 해석
    ↓
사용자에게 응답 (스트리밍)
```

## 🔑 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | (필수) |
| `OPENAI_BASE_URL` | API 엔드포인트 URL | `https://api.openai.com/v1` |
| `MODEL_NAME` | 사용할 모델 이름 | `gpt-4` |
| `MAX_TOKENS` | 최대 토큰 수 | `2000` |
| `TEMPERATURE` | 응답 다양성 (0-1) | `0.7` |

## 🧪 테스트

MCP 도구 직접 테스트:
```bash
uv run python -c "from mcp_tools import read_file, list_files; print(list_files('.'))"
```

(선택) MCP 서버/클라이언트 테스트:
```bash
# 터미널 1: MCP 서버 실행
uv run python mcp_server.py

# 터미널 2: 클라이언트 테스트
uv run python mcp_client.py
```

## 📝 개발 노트

### 새로운 도구 추가

`mcp_tools.py`의 TOOLS 딕셔너리에 새로운 도구 추가:

```python
def your_new_tool(param: str) -> str:
    """도구 설명"""
    # 구현
    return result

# TOOLS 딕셔너리에 추가
TOOLS["your_new_tool"] = {
    "function": your_new_tool,
    "description": "도구 설명",
    "parameters": {
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "파라미터 설명"
            }
        },
        "required": ["param"]
    }
}
```

### 다른 LLM 사용

Ollama 등 OpenAI 호환 API를 사용하는 경우 `.env` 파일에서 설정:

```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama  # Ollama는 API 키가 필요없지만 형식상 필요
MODEL_NAME=llama2
```

## 🐛 문제 해결

### LLM 응답 없음
- API 키가 올바르게 설정되었는지 확인 (.env 파일)
- OPENAI_API_KEY 환경 변수 확인
- 네트워크 연결 확인
- 모델 이름이 올바른지 확인 (기본값: gpt-4)

### 파일 읽기 권한 오류
- 읽으려는 파일의 권한 확인
- 상대 경로 대신 절대 경로 사용 고려
- 파일이 존재하는지 확인

### 도구가 호출되지 않음
- LLM이 도구를 사용해야 하는지 명확하게 요청
- 예: "README.md 파일을 읽어줘" (명확함) vs "README에 뭐가 있어?" (불명확)

## 📚 참고 자료

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Chainlit Documentation](https://docs.chainlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 📄 라이선스

MIT License