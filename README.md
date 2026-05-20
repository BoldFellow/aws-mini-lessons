# AWS Mini Lessons

Short, focused hands-on lessons for AWS Cloud Architect class. Each lesson fits in one lab session and teaches one core concept.

## Lessons

| Folder | Topic | Key concept |
|---|---|---|
| [`ebs/`](ebs/) | Elastic Block Store | Block volumes: attach to one instance, detach, reattach to another — data persists |
| [`efs/`](efs/) | Elastic File System | Shared NFS filesystem: multiple EC2 instances mount and serve from the same files simultaneously |
| [`filtering-lambda/`](filtering-lambda/) | S3 Event-Driven Filtering | S3 PUT triggers Lambda; Lambda inspects the file and routes it to one of two target buckets |
| [`sns-sqs-lambda-s3/`](sns-sqs-lambda-s3/) | SNS + SQS Fan-out Filtering | SNS filter policies route messages by attribute prefix to separate SQS queues |

## How to use

Each folder has:
- `architecture.png` — diagram
- `architecture.drawio` — editable source
- `lesson.md` — step-by-step lab instructions

Open `lesson.md` in any folder to start the lab.

## Recommended order

These lessons are self-contained and can be done in any order. Suggested sequencing within a course:

1. **EBS** — after introducing EC2 (block storage is the first storage concept)
2. **EFS** — immediately after EBS (contrast: single-attach vs. multi-attach)
3. **Filtering Lambda** — after introducing Lambda and S3 events
4. **SNS/SQS** — after introducing serverless and messaging patterns

## License

MIT — see [LICENSE](LICENSE).
