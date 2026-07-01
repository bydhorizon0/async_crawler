## 핵심 구조 및 동작 방식
1. 생산자-소비자(Producer-Consumer) 패턴

- `asyncio.Queue` 기반 구동: 수집 대상 큐(queue)와 브라우저 페이지 큐(page_queue)를 사용하여 워커 태스크가 독립적으로 작업을 처리합니다.
- 페이지 인스턴스 재사용: 매번 브라우저 탭을 새로 켜지 않고, 사용이 끝난 Page 객체를 page_queue에 다시 반납(put)하여 재사용합니다. 
- 리소스 및 세션 초기화: 하나의 수집 작업이 끝나면 실패 여부와 상관없이 about:blank로 이동하고 쿠키를 삭제(clear_cookies)하여 상태를 격리합니다. 
- 안전한 종료 보장: 예외 발생 시에도 finally 블록에서 queue.task_done()을 무조건 실행하여 프로그램이 멈추지 않고 정상 종료되도록 합니다.

2. 페이지네이션 및 동시성 제어

- 동적 페이지네이션 (클릭형): 자바스크립트 클릭 이벤트로 페이지를 이동합니다. 무분별한 요청을 막기 위해 asyncio.Semaphore(3)로 최대 동시 요청 수를 3개로 제한합니다. 
- 정적 페이지네이션 (URL형): URL 파라미터(예: page={})를 변경하여 바로 이동하며, 성능 향상을 위해 DOM 트리만 로드되면 즉시 다음 처리를 시작합니다(wait_until="domcontentloaded").

3. 데이터 파싱 및 가변 URL 생성

- 요소 대기: 리스트의 첫 번째 아이템이 보일 때까지 최대 30초 대기 처리(wait_for)가 적용되어 있습니다. 
- 정규표현식 식별자 추출: 요소의 속성에서 ID 문자열을 추출한 뒤 정규식(re.search) 결과에 따라 가변 인자 타플(format_args)을 생성합니다. 그룹 지정이 없는 정규식도 매칭된 전체 문자열을 쓰도록 방어 코드가 작성되어 있습니다. 
- 상세 URL 매핑: 추출한 인자들을 패턴 문자열에 언패킹(format(*format_args))하여 최종 상세 URL을 완성하며, 인자 개수 불일치 에러(IndexError)를 처리합니다.

## 사용한 라이브러리

- `playwright`
- `fake-useragent`
- `aiosqlite`
- `httpx`


## 실행 방법

#### 의존성 설치 및 환경 구성
uv 패키지 관리자를 사용하여 정의된 가상환경을 동기화하고 패키지를 설치한 뒤, playwright 구동에 필요한 내부 브라우저 바이너리를 내려받습니다.

```bash
uv sync
source .venv/bin/activate
playwright install
```

#### 프로그램 구동
비동기 수집 프로세스가 포함된 메인 스크립트를 실행합니다.

```bash
python main_async.py
```