# SmartHire Composer

SmartHire Composer là ứng dụng hỗ trợ HR tạo và quản lý Job Description (JD), sinh câu hỏi phỏng vấn và tìm kiếm ngữ nghĩa trên thư viện JD thật.

## Tính năng

- Đăng nhập JWT và phân quyền `admin`, `recruiter`, `manager`, `viewer`.
- Tạo, chỉnh sửa, cải thiện và gợi ý JD bằng Gemini.
- Lưu lịch sử phiên bản trong PostgreSQL.
- Sinh câu hỏi technical, behavioral và situational; tự fallback offline khi LLM tạm lỗi.
- RAG: chunk JD, tạo embedding, lưu Milvus và tìm kiếm COSINE.
- Thu thập JD thật từ API công khai Greenhouse/Lever hoặc JSON-LD `JobPosting`.
- Lưu provenance: nguồn, công ty, external ID, URL, thời điểm lấy và SHA-256.
- Xuất PDF và DOCX.

## Kiến trúc

```text
React/Vite (:5173)
        |
        | HTTP + JWT
        v
FastAPI (:8000)
   |---- PostgreSQL (:5432): user, JD, version, taxonomy, provenance
   |---- Gemini: content generation + embedding
   |---- Milvus (:19530): vector search
   `---- data/chunks/: nội dung chunk local

Milvus dùng etcd và MinIO nội bộ. Ứng dụng không dùng MinIO để lưu file JD.
```

## Yêu cầu

- Python 3.12+
- Node.js 20+
- Docker Desktop
- Gemini API key nếu dùng AI/embedding Gemini

## Khởi động nhanh trên Windows

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm ci
cd ..

# Dựng PostgreSQL, Milvus, etcd, MinIO và chạy migration/seed
.\scripts\bootstrap.ps1

# Terminal 1: backend
$env:PYTHONUTF8="1"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: frontend
cd frontend
npm run dev -- --host 0.0.0.0
```

Địa chỉ:

- Frontend: http://localhost:5173
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/ping

Tài khoản development được seed:

```text
username: hr_admin
password: changeme
```

Hãy đổi mật khẩu và JWT secret trước khi triển khai thật.

## Cấu hình

Sao chép `.env.example` thành `.env`, sau đó điền secret:

```powershell
Copy-Item .env.example .env
```

Các biến quan trọng:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jd_library
DB_USER=jd_user
DB_PASS=jd_pass
DB_SCHEMA=smarthire

JWT_SECRET_KEY=change-me
GEMINI_API_KEY=replace-me
GEMINI_CHAT_MODEL=gemini-2.5-flash-lite
GEMINI_EMBED_MODEL=gemini-embedding-001

LLM_PROVIDER=gemini
LLM_BYPASS=false
EMBEDDING_PROVIDER=gemini
VECTOR_DIM=768
```

`EMBEDDING_PROVIDER=local` bật lexical hashing thuần Python khi cần chạy hoàn toàn offline. Không trộn vector Gemini và local trong cùng collection; phải re-index toàn bộ khi đổi provider/model.

## Database

Development database:

```text
postgresql://jd_user:jd_pass@localhost:5432/jd_library
schema: smarthire
container: pg_jd_demo
```

Truy cập bằng terminal:

```powershell
docker exec -it pg_jd_demo psql -U jd_user -d jd_library
```

```sql
SET search_path TO smarthire, public;
\dt
SELECT jd_id, title, source_company, source_url FROM job_descriptions LIMIT 10;
```

## Thu thập dữ liệu JD thật

Pipeline chỉ bật mặc định cho nguồn công khai phù hợp:

1. Greenhouse Job Board API.
2. Lever Postings API.
3. Trang nghề nghiệp cụ thể có JSON-LD chuẩn `JobPosting`.

Không crawl LinkedIn hoặc job board cấm bot. `robots.txt` chỉ là tín hiệu kỹ thuật, không thay thế Terms of Service hay giấy phép sử dụng dữ liệu.

Tài liệu nguồn:

- [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html)
- [Lever Postings API](https://github.com/lever/postings-api)
- [Schema.org JobPosting](https://schema.org/JobPosting)
- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)

### Greenhouse

```powershell
.\.venv\Scripts\python.exe scripts\crawl_jobs.py `
  --source greenhouse `
  --site cloudflare `
  --company Cloudflare `
  --limit 25
```

### Lever

```powershell
.\.venv\Scripts\python.exe scripts\crawl_jobs.py `
  --source lever `
  --site company-site-token `
  --company "Company name" `
  --limit 25
```

### JSON-LD

Chỉ truyền URL trang JD cụ thể mà bạn được phép thu thập:

```powershell
.\.venv\Scripts\python.exe scripts\crawl_jobs.py `
  --source jsonld `
  --company "Company name" `
  --url "https://company.example/careers/job/123"
```

Kết quả được lưu tại `data/real_jd/`. Mỗi file chứa front matter provenance và nội dung JD gốc đã chuyển về plain Markdown.

## ETL PostgreSQL

Import JD thật:

```powershell
$env:PYTHONUTF8="1"
.\.venv\Scripts\python.exe etl\jd_etl.py `
  --dir data\real_jd `
  --author public-api-ingestion `
  --summary "Imported from public ATS API with provenance"
```

ETL upsert theo `(source_name, source_external_id)`, do đó chạy lại sẽ cập nhật thay vì tạo bản ghi trùng. Mỗi thay đổi được ghi vào `jd_versions`.

Thư mục `etl/jd_markdown/` là dữ liệu synthetic cũ, chỉ dùng test/demo; không nên trộn với corpus production.

## RAG và indexing

```powershell
$env:PYTHONUTF8="1"
.\.venv\Scripts\python.exe embeddings\jd_chunk_embed.py
```

Pipeline:

1. Đọc `job_descriptions.content_md`.
2. Chia theo heading/đoạn, hard-split block dài, có overlap.
3. Lưu chunk tại `data/chunks/jd-<id>/chunk-<n>.md`.
4. Tạo vector 768 chiều.
5. Upsert vào collection Milvus `jdchunks`.

Gemini free tier giới hạn số embedding/phút. Script batch theo `EMBEDDING_BATCH_SIZE` và nghỉ theo `EMBEDDING_BATCH_DELAY_SECONDS`. Dữ liệu Milvus cũ chỉ bị thay sau khi toàn bộ embedding mới được tạo thành công.

Thử tìm kiếm tại http://localhost:5173/retrieve hoặc:

```http
POST /v1/retrieve/similar
Authorization: Bearer <token>
Content-Type: application/json

{"query":"senior cloud security engineer", "top_k":5}
```

## API chính

| Method | Endpoint | Vai trò |
|---|---|---|
| POST | `/auth/token` | public |
| GET | `/auth/me` | authenticated |
| POST | `/v1/jd/generate` | recruiter, admin |
| PUT | `/v1/jd/update` | recruiter, admin |
| GET | `/v1/jd/version-history/{jd_id}` | recruiter, manager, admin |
| GET | `/v1/jd/export/{jd_id}` | recruiter, admin |
| POST | `/v1/jd/improve` | recruiter, admin |
| POST | `/v1/jd/suggest` | recruiter, admin |
| POST | `/v1/interview/generate` | recruiter, admin |
| POST | `/v1/retrieve/similar` | recruiter, manager, admin |
| GET | `/v1/roles/list` | recruiter, manager, admin |

## Kiểm thử

```powershell
$env:PYTHONUTF8="1"
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run build
npm audit
```

## Production checklist

- Rotate Gemini key/JWT secret và không commit `.env`.
- Thay tài khoản/mật khẩu PostgreSQL development.
- Giới hạn `CORS_ORIGINS` theo domain thật.
- Thêm HTTPS/reverse proxy và rate limiting.
- Chạy crawler theo lịch, lưu log lần fetch và xử lý tin đã đóng.
- Xác nhận Terms/API license của từng nguồn trước khi bật.
- Không thu thập CV, email ứng viên hoặc dữ liệu cá nhân nếu chưa có cơ sở pháp lý.
