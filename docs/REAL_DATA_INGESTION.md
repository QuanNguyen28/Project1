# Phương án thu thập dữ liệu JD thật

## Mục tiêu

Xây corpus JD có thể truy nguyên, cập nhật định kỳ và sử dụng được cho RAG mà không phụ thuộc vào dữ liệu Faker. Mỗi bản ghi phải trả lời được:

- Tin đến từ đâu?
- Ai là công ty đăng tuyển?
- ID và URL gốc là gì?
- Nội dung được lấy lúc nào?
- Nội dung có thay đổi không?
- Có được phép tự động lấy và sử dụng hay không?

## Thứ tự ưu tiên nguồn

| Ưu tiên | Nguồn | Cách lấy | Đánh giá |
|---|---|---|---|
| 1 | ATS API công khai | Greenhouse Job Board API, Lever Postings API | Ổn định, có ID, cấu trúc rõ |
| 2 | Career site của doanh nghiệp | JSON-LD `JobPosting` trên URL được duyệt | Tốt, cần kiểm tra ToS/robots từng site |
| 3 | Feed/API theo hợp đồng | API partner từ job board | Tốt nhất nếu cần quy mô thương mại |
| Không mặc định | LinkedIn/job board cấm bot | Không scrape | Rủi ro pháp lý và khóa tài khoản |

Tài liệu chính thức:

- Greenhouse: https://developers.greenhouse.io/job-board.html
- Lever: https://github.com/lever/postings-api
- Schema.org: https://schema.org/JobPosting
- LinkedIn User Agreement: https://www.linkedin.com/legal/user-agreement

## Pipeline đề xuất

```text
Source registry
   -> policy/allow-list check
   -> fetch with rate limit + User-Agent
   -> raw response snapshot (optional)
   -> normalize to JobPosting
   -> content hash + deduplicate
   -> Markdown with provenance
   -> PostgreSQL upsert + version history
   -> chunk full content
   -> embed one consistent model
   -> atomic Milvus rebuild/upsert
   -> quality and freshness report
```

## Schema provenance đã triển khai

`job_descriptions` có thêm:

- `source_name`
- `source_external_id`
- `source_url`
- `source_company`
- `source_published_at`
- `source_fetched_at`
- `source_hash`

Unique index `(source_name, source_external_id)` ngăn trùng tin. Nếu hash không đổi, ETL chỉ cập nhật `source_fetched_at` và không tạo version rác.

## Chính sách vận hành

1. Chỉ thêm nguồn qua allow-list đã review Terms/API documentation.
2. Dùng endpoint JSON chính thức trước HTML crawling.
3. Rate limit mặc định tối thiểu 500 ms/request; tôn trọng `Retry-After`.
4. Không đăng nhập, vượt CAPTCHA, né rate limit hoặc gọi private API.
5. Không thu thập form ứng tuyển, CV, email, số điện thoại hay dữ liệu ứng viên.
6. Luôn giữ URL gốc và hiển thị attribution khi dùng nội dung.
7. Có cơ chế xóa dữ liệu theo yêu cầu của chủ nguồn.
8. Không dùng corpus để tái xuất bản nguyên văn như một job board cạnh tranh nếu chưa có giấy phép.

## Làm sạch và đánh giá chất lượng

- Loại boilerplate bình đẳng tuyển dụng/quyền riêng tư khỏi embedding nhưng giữ trong raw content nếu cần audit.
- Phát hiện ngôn ngữ, country, remote/hybrid/on-site.
- Chuẩn hóa department, seniority, employment type và skill taxonomy.
- Loại tin quá ngắn, description rỗng hoặc URL không hợp lệ.
- Deduplicate gần đúng giữa nhiều nguồn bằng hash chuẩn hóa + similarity title/company/location.
- Theo dõi tỷ lệ thiếu title/location/description và phân phối độ dài.

## Đồng bộ tin đóng

Giai đoạn tiếp theo nên thêm `source_active`, `first_seen_at`, `last_seen_at`:

1. Mỗi lần crawl đánh dấu toàn bộ external ID nhìn thấy.
2. Tin không còn xuất hiện qua 2–3 lần crawl liên tiếp được chuyển `source_active=false`.
3. Không xóa lịch sử ngay; loại tin inactive khỏi retrieval mặc định.
4. Có TTL lưu trữ theo thỏa thuận với nguồn.

## Lịch chạy khuyến nghị

- API ATS: 2–4 lần/ngày.
- Career page JSON-LD: 1 lần/ngày.
- Re-index chỉ JD có hash thay đổi.
- Full index validation: hàng tuần.
- Báo cáo freshness/failed sources: hàng ngày.

Trong production nên dùng scheduler như GitHub Actions, Airflow, Prefect hoặc cron, kèm retry có exponential backoff và alert khi schema nguồn thay đổi.

## Dữ liệu hiện có trong project

- `etl/jd_markdown/`: 109 JD synthetic cũ; chỉ dùng demo/test.
- `data/real_jd/`: JD thật lấy từ các public Greenhouse feeds.
- PostgreSQL: corpus đã import với provenance và version history.
- Milvus: corpus được chunk và embedding cho semantic retrieval.

Không nên gộp synthetic corpus vào production index. Nếu cần benchmark, dùng collection hoặc schema riêng và gắn nhãn `data_origin=synthetic`.
