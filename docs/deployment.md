# 배포 가이드

jay-asset은 두 부분으로 나뉘어 배포됩니다.

| 구분 | 방식 | 배포 방법 |
|---|---|---|
| 프론트엔드 (React) | AWS Amplify Hosting, GitHub `main` 연결 | `main`에 push하면 자동 배포 |
| 백엔드 (Flask on Lambda) | AWS SAM 스택 `jay-asset` | `.\scripts\deploy-backend.ps1` |

## 전체 구조

```
asset.jehyeonlee.net (Amplify 앱: jay-asset)
   │  REACT_APP_API_BASE_URL
   ▼
Lambda Function URL ── Lambda (SAM 스택 jay-asset, 논리 이름 ApiFunction)
                          │  lambda_handler.handler
                          ├─ API 요청 (/api/*)        → Flask app.py
                          ├─ {"job": "market_data_ingest"}  ← 평일 21:00 (뉴욕) 스케줄
                          └─ {"job": "performance_refresh"} ← 매월 1일 08:00 (뉴욕) 스케줄
                          ▼
DynamoDB: jay-asset-daily-prices / jay-asset-performance / jay-asset-cache
```

- AWS 리소스는 모두 [template.yaml](../template.yaml)에 정의되어 있습니다.
- **DynamoDB 테이블 3개는 SAM이 관리하지 않습니다.** 데이터가 들어 있는 기존 테이블을 이름으로만 참조하므로, 스택을 지우거나 다시 만들어도 테이블은 그대로 남습니다.
- 리전은 `us-east-1`입니다.

## 처음 한 번만: 준비

1. **AWS CLI 로그인**: `aws sts get-caller-identity`가 계정 `366346557198`을 보여 줘야 합니다. 사용자에게 CloudFormation, Lambda, IAM, S3, Scheduler 권한이 필요합니다. 지금은 `AdministratorAccess`를 붙여 두었습니다.
2. **SAM CLI 설치**: `winget install Amazon.SAM-CLI`를 실행한 뒤 **VS Code를 완전히 재시작**합니다.
3. **Docker Desktop 설치**: 빌드는 Docker 안에서 Linux용으로 진행됩니다(numpy, pandas 때문에 필요).
4. **PowerShell 스크립트 실행 허용**:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```
5. **비밀값 파일 만들기**: [backend/.env.aws.example](../backend/.env.aws.example)을 `backend/.env.aws.local`로 복사하고 `TIINGO_API_KEY`를 채웁니다. 이 파일은 git에 올라가지 않습니다.

## 백엔드 배포

1. Docker Desktop을 켭니다.
2. 프로젝트 루트에서 실행합니다.
   ```powershell
   .\scripts\deploy-backend.ps1
   ```
3. 변경 목록(changeset)이 나오면 확인하고 `y`를 누릅니다.
   - 코드만 바꾼 경우: `* Modify  ApiFunction` 정도만 나와야 정상입니다.
   - `- Delete`가 보이거나, 예상하지 못한 `Replacement: True`가 보이면 `N`을 누르고 원인을 먼저 확인합니다.

스크립트가 하는 일은 다음과 같습니다.
- `backend/.env.aws.local`에서 Tiingo 키를 읽습니다.
- `sam build`: Docker 안에서 `backend/requirements.txt`를 설치하고 코드를 묶습니다.
- `sam deploy`: 변경된 부분만 AWS에 반영합니다.

**API 주소는 배포할 때마다 바뀌지 않습니다.** 스택을 지우고 다시 만들거나 `template.yaml`에서 `ApiFunction` 이름을 바꿀 때만 바뀝니다. 현재 주소는 아래 명령으로 확인합니다.

```powershell
aws cloudformation describe-stacks --stack-name jay-asset --query "Stacks[0].Outputs" --output table
```

### 스케줄 잠시 멈추기

```powershell
.\scripts\deploy-backend.ps1 -SchedulesState DISABLED
```

다시 켤 때는 옵션 없이 평소처럼 실행하면 됩니다. 기본값이 `ENABLED`입니다.

### 의존성 관리

- [backend/requirements.txt](../backend/requirements.txt): **Lambda에 들어가는 패키지만** 적습니다. boto3는 Lambda 런타임에 이미 들어 있어서 넣지 않습니다.
- [backend/requirements-dev.txt](../backend/requirements-dev.txt): 로컬 개발용입니다(boto3, yfinance, pandas_datareader 포함). 로컬에서는 `pip install -r requirements-dev.txt`로 설치합니다.
- `backend/` 안에 `lambda_build/`, `lambda_pkg/`, `deployment*.zip` 같은 예전 빌드 결과물이 있으면 패키지 크기 제한(250MB)을 넘기 때문에, 스크립트가 배포 전에 멈춥니다. 지우고 다시 실행합니다.

## 프론트엔드 배포

- `main`에 push하면 Amplify가 `npm run build` 후 자동으로 배포합니다.
- 백엔드 API 주소는 Amplify 콘솔의 **Hosting → Environment variables → `REACT_APP_API_BASE_URL`**에 들어 있습니다. 값 끝에 `/api`가 붙습니다.
- `REACT_APP_*` 값은 **빌드할 때** 코드에 박혀 들어갑니다. 그래서 값을 바꾼 뒤에는 반드시 다시 빌드해야 합니다.
  ```powershell
  aws amplify start-job --app-id d32iz68055zr4k --branch-name main --job-type RELEASE
  ```
  콘솔에서 **Redeploy this version**을 눌러도 됩니다.
- 로컬 개발에서는 루트의 `.env.local`에 있는 `REACT_APP_API_BASE_URL`을 사용합니다.

## 새 전략이나 티커를 추가할 때

전략 코드 자체는 [backend/NEW_STRATEGY_CHECKLIST.md](../backend/NEW_STRATEGY_CHECKLIST.md)를 따릅니다. 배포와 관련해 추가로 할 일은 다음과 같습니다.

1. **새 티커를 매일 수집 목록에 추가합니다.** [template.yaml](../template.yaml)의 `MARKET_INGEST_TICKERS` 값에 티커를 넣습니다.
2. 백엔드를 배포합니다(`.\scripts\deploy-backend.ps1`).
3. **과거 데이터를 한 번 채웁니다(backfill).** 매일 수집은 최근 14일만 가져오기 때문입니다. 기존 데이터는 2023-12-11부터 있으므로 약 1,030일을 받습니다.
   ```powershell
   $fn = aws cloudformation describe-stacks --stack-name jay-asset --query "Stacks[0].Outputs[?OutputKey=='FunctionName'].OutputValue" --output text
   '{"job":"market_data_ingest","tickers":["VWO","BND"],"lookback_days":1030}' | Set-Content -Encoding ascii payload.json
   aws lambda invoke --function-name $fn --payload fileb://payload.json --cli-read-timeout 310 out.json
   Get-Content out.json   # "ok": true, "rows_written" 확인
   Remove-Item payload.json, out.json
   ```
4. 확인: `<API 주소>/api/calculate`로 새 전략을 계산하고, `<API 주소>/api/performance?strategy_id=<id>`로 성과를 조회해 봅니다.
5. 프론트엔드 변경(설명 문구 등)을 push합니다.

## 운영 작업

**작업 수동 실행** (위 backfill과 같은 방식으로 payload만 바꿉니다)
- 성과 다시 계산: `{"job":"performance_refresh"}`
- 최근 시세 수집: `{"job":"market_data_ingest","lookback_days":14}`

**로그 보기**
```powershell
sam logs --stack-name jay-asset -n ApiFunction --tail
```
로그는 30일 동안 보관됩니다.

**되돌리기**
- 코드 문제라면 이전 커밋으로 돌아가서(`git checkout <commit>`) 다시 배포하는 게 가장 간단합니다.
- `sam delete --stack-name jay-asset`를 실행하면 Lambda, 스케줄, 역할이 전부 삭제되고 **API 주소도 사라집니다.** 테이블은 남지만, 다시 배포하면 주소가 새로 생기므로 Amplify 환경변수도 바꿔야 합니다. 꼭 필요할 때만 사용합니다.

### 계산 결과 캐시

`/api/calculate` 결과는 `jay-asset-cache` 테이블에 2시간 동안 캐시됩니다. 캐시 키에는 **전략 코드 파일(전략 클래스와 `BaseStrategy`)의 지문(hash)**이 들어갑니다. 그래서 전략 코드를 고쳐서 배포하면 예전 캐시는 자동으로 무시됩니다.

단, `market/` 같은 공용 코드만 고쳤다면 지문이 바뀌지 않아서 최대 2시간 동안 예전 결과가 나올 수 있습니다. 바로 반영하고 싶으면 AWS 콘솔에서 `jay-asset-cache` 테이블의 항목을 지웁니다. 캐시라서 지워도 안전합니다.

### 주의: 템플릿 파라미터

`sam deploy`는 이미 있는 스택을 다시 배포할 때, 직접 넘겨주지 않은 파라미터는 **지난번 값을 그대로 씁니다.** `template.yaml`의 `Parameters` 아래 `Default`를 바꿔도 반영되지 않습니다. 그래서 자주 바뀌는 값(수집 티커, CORS 도메인)은 파라미터가 아니라 리소스에 직접 적어 두었습니다. 새 설정값을 추가할 때도 같은 방식을 따릅니다.

## 문제 해결

| 증상 | 해결 |
|---|---|
| `running scripts is disabled on this system` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `sam : The term 'sam' is not recognized` | VS Code 완전 재시작 (스크립트가 PATH를 다시 읽으려고 시도함) |
| `requires a container runtime ... Docker` | Docker Desktop 켜기 |
| `Remove old build artifacts before deploying` | 메시지에 나온 `backend/` 안의 예전 빌드 폴더와 zip 삭제 |
| `TIINGO_API_KEY is missing` | `backend/.env.aws.local` 확인 |
| `No changes to deploy` | 바뀐 게 없다는 뜻이라 정상 |
| 브라우저 CORS 에러 | 새 도메인이라면 `template.yaml`의 `AllowOrigins` 목록에 추가하고 배포 |
| 전략 계산 시 `No ... data available` | 해당 티커의 시세가 테이블에 없음 → 위 "새 티커 추가" 3단계(backfill) 실행 |

## 남은 정리 작업 (2026-10 SAM 전환)

수동 배포에서 SAM으로 옮기면서 생긴 정리 작업입니다. 끝나면 이 섹션은 지웁니다.

- [x] 예전 스케줄 2개 삭제: `jay-asset-daily-market-ingest`, `jay-asset-performance-refresh`
- [x] 새 스케줄 켜기
- [x] VWO, BND를 수집 목록에 추가
- [ ] 며칠 지켜본 뒤 예전 Lambda `jay-asset-api`와 역할 `jay-asset-lambda-role` 삭제
- [ ] (선택) GitHub Actions로 백엔드도 push 시 자동 배포
