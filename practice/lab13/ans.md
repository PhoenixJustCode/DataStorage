# Шпаргалка — Lab 13: AWS S3 (Cloud Storage Basics)

---

## Что за задание вообще?

Практика по облачному хранилищу AWS S3. Нужно:
1. Создать bucket с версионированием и шифрованием
2. Загружать/скачивать файлы через AWS CLI
3. Написать Python-скрипт на boto3 (upload, download, list, presigned URL, delete)
4. Настроить Lifecycle-политику (архивация → Glacier → удаление)

**Важно:** bucket-имена глобально уникальны по всему AWS. В конце удалить всё, чтобы не платить.

---

## Что нужно сделать ДО начала (setup)

```bash
# 1. Установить AWS CLI
pip install awscli

# 2. Установить boto3
pip install boto3

# 3. Настроить credentials (Access Key + Secret Key из AWS Console → IAM)
aws configure
# AWS Access Key ID: ...
# AWS Secret Access Key: ...
# Default region name: eu-north-1
# Default output format: json
```

**Где взять ключи:** AWS Console → IAM → Users → ваш user → Security credentials → Create access key.

**Никогда** не коммитить `~/.aws/credentials` в git.

---

## Task 1 — Создать Bucket с версионированием

**Через AWS Console (проще):**
1. S3 → Create bucket
2. Имя: `alexanderd-data-lake-lab-2026` (глобально уникальное — добавь инициалы + дату)
3. Region: **eu-north-1** (Стокгольм)
4. **Block all public access** — оставить включённым (по умолчанию)
5. **Bucket Versioning** → Enable
6. **Default encryption** → SSE-S3 (Amazon S3 managed keys)
7. Create bucket

**Через CLI (альтернатива):**
```bash
aws s3api create-bucket \
  --bucket alexanderd-data-lake-lab-2026 \
  --region eu-north-1 \
  --create-bucket-configuration LocationConstraint=eu-north-1

aws s3api put-bucket-versioning \
  --bucket alexanderd-data-lake-lab-2026 \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket alexanderd-data-lake-lab-2026 \
  --server-side-encryption-configuration '{
    "Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]
  }'
```

**Deliverable:** скриншот bucket Properties — вкладка с Versioning = Enabled.

---

## Task 2 — AWS CLI upload/download

```bash
# 1. Создать локальный файл
echo "Hello Cloud Storage!" > test.txt

# 2. Загрузить под ключом data/test.txt
aws s3 cp test.txt s3://alexanderd-data-lake-lab-2026/data/test.txt

# 3. Второй файл (CSV или картинка)
echo "id,name,value" > sample.csv
echo "1,alpha,100" >> sample.csv
aws s3 cp sample.csv s3://alexanderd-data-lake-lab-2026/data/sample.csv

# 4. Список объектов в префиксе data/
aws s3 ls s3://alexanderd-data-lake-lab-2026/data/

# 5. Скачать всё в папку downloaded/
mkdir downloaded
aws s3 cp s3://alexanderd-data-lake-lab-2026/data/ downloaded/ --recursive
```

**Разница между `s3` и `s3api`:**
- `s3` — high-level, удобно для cp/ls/sync
- `s3api` — low-level, 1-в-1 к REST API (для versioning, encryption, policies)

**Deliverable:** скриншот терминала со всеми командами и выводом.

---

## Task 3 — Python boto3 скрипт

Файл `s3_operations.py` должен делать 7 шагов. Готовый шаблон:

```python
import boto3
from botocore.exceptions import ClientError
import csv

BUCKET = 'alexanderd-data-lake-lab-2026'
KEY = 'uploads/report.csv'

# 1. Клиент
s3 = boto3.client('s3', region_name='eu-north-1')

# 2. Создать report.csv
with open('report.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'department', 'revenue'])
    w.writerow([1, 'analytics', 15000])
    w.writerow([2, 'sales', 23000])

# 3. Upload с metadata
s3.upload_file(
    'report.csv', BUCKET, KEY,
    ExtraArgs={'Metadata': {'department': 'analytics', 'owner': 'alexanderd'}}
)
print(f'Uploaded s3://{BUCKET}/{KEY}')

# 4. Download
s3.download_file(BUCKET, KEY, 'downloaded_report.csv')
print('Downloaded to downloaded_report.csv')

# 5. List с пагинацией
paginator = s3.get_paginator('list_objects_v2')
print('\nObjects in uploads/:')
for page in paginator.paginate(Bucket=BUCKET, Prefix='uploads/'):
    for obj in page.get('Contents', []):
        print(f"  {obj['Key']}  {obj['Size']}B  {obj['LastModified']}")

# 6. Presigned URL на 2 часа
url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': BUCKET, 'Key': KEY},
    ExpiresIn=7200
)
print(f'\nPresigned URL (valid 2h):\n{url}')

# 7. Проверить существование и удалить
try:
    s3.head_object(Bucket=BUCKET, Key=KEY)
    s3.delete_object(Bucket=BUCKET, Key=KEY)
    print(f'\nDeleted {KEY}')
except ClientError as e:
    print(f'Object not found: {e}')
```

**Ключевые моменты, которые могут спросить:**
- **Почему paginator?** `list_objects_v2` возвращает максимум 1000 ключей за раз. Paginator автоматически делает дополнительные запросы через `NextContinuationToken`.
- **Presigned URL** — временная ссылка для доступа без credentials. Подпись содержит Access Key, срок, операцию. Кто угодно с URL может скачать файл до истечения срока.
- **head_object** — HEAD-запрос, проверяет существование без скачивания тела.
- **Metadata** — пользовательские key-value пары, хранятся в заголовках объекта (`x-amz-meta-*`), видны через `head_object`.

**Deliverable:** файл `s3_operations.py` + скриншот вывода.

---

## Task 4 — Lifecycle Policy

**Что это:** автоматические правила перемещения/удаления объектов по возрасту. Экономит деньги — холодные данные в дешёвый Glacier.

**Классы хранилища (от горячего к холодному):**
| Класс | Цена | Доступ | Когда |
|---|---|---|---|
| S3 Standard | $$$ | мгновенно | свежие, часто используемые |
| S3 Standard-IA | $$ | мгновенно | редко (раз в месяц), но быстро нужно |
| S3 Glacier Flexible Retrieval | $ | минуты-часы | архив, иногда достаём |
| S3 Glacier Deep Archive | ¢ | 12 часов | compliance-архивы |

**Задание:**
- Префикс `archive/` → Standard-IA через 30 дней
- → Glacier Flexible Retrieval через 90 дней
- → Полностью удалить через 365 дней

**Через Console (проще):**
1. Bucket → Management → Lifecycle rules → Create lifecycle rule
2. Name: `archive-tiering`
3. Scope → Limit by prefix → `archive/`
4. Actions:
   - **Transition current versions**: Standard-IA after 30 days
   - **Transition current versions**: Glacier Flexible Retrieval after 90 days
   - **Expire current versions**: 365 days
5. Create rule

**Через CLI (JSON-файл `lifecycle.json`):**
```json
{
  "Rules": [
    {
      "ID": "archive-tiering",
      "Status": "Enabled",
      "Filter": {"Prefix": "archive/"},
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"}
      ],
      "Expiration": {"Days": 365}
    }
  ]
}
```
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket alexanderd-data-lake-lab-2026 \
  --lifecycle-configuration file://lifecycle.json
```

**Deliverable:** скриншот Console со списком lifecycle rules.

---

## Что нужно сделать ОТДЕЛЬНО (не забыть)

### 1. Скриншоты (обязательны к сдаче)
- **Task 1:** Properties bucket-а с Versioning = Enabled
- **Task 2:** терминал с CLI-командами и выводом
- **Task 3:** вывод Python-скрипта (presigned URL + список объектов)
- **Task 4:** Console со списком lifecycle rules

### 2. Файлы к сдаче
- `s3_operations.py` — скрипт Task 3
- (опционально) `lifecycle.json` если делал через CLI
- Папка со скриншотами

### 3. Cleanup в КОНЦЕ (критично — иначе AWS списывает деньги)
```bash
# 1. Удалить все объекты (включая версии — versioning включён!)
aws s3 rm s3://alexanderd-data-lake-lab-2026 --recursive

# 2. Удалить все версии и delete markers
aws s3api delete-objects --bucket alexanderd-data-lake-lab-2026 \
  --delete "$(aws s3api list-object-versions \
    --bucket alexanderd-data-lake-lab-2026 \
    --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}')"

# 3. Удалить delete markers отдельно
aws s3api delete-objects --bucket alexanderd-data-lake-lab-2026 \
  --delete "$(aws s3api list-object-versions \
    --bucket alexanderd-data-lake-lab-2026 \
    --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}')"

# 4. Удалить bucket
aws s3api delete-bucket --bucket alexanderd-data-lake-lab-2026 --region eu-north-1
```

**Через Console проще:** Empty bucket → потом Delete bucket (введёшь имя для подтверждения).

**Почему с versioning нельзя просто `rm --recursive`:** удаление создаёт **delete marker**, но старые версии остаются и за них списывают. Нужно удалить **все версии**.

### 4. Безопасность
- Не коммитить `~/.aws/credentials`
- Не вставлять Access Key в код — используй `aws configure` или переменные окружения `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Bucket с `Block all public access` — не делать публичным
- Для проверки работы снаружи использовать **presigned URL**, а не public bucket

---

## Что могут спросить на уроке

**Q: Почему versioning?**
A: Защита от случайного удаления/перезаписи. Каждая версия хранится отдельно, можно откатиться. Минус — платишь за все версии.

**Q: Разница SSE-S3 vs SSE-KMS?**
A: SSE-S3 — AWS полностью управляет ключами, бесплатно. SSE-KMS — отдельный сервис KMS, можно свой ключ (CMK), аудит через CloudTrail, но платишь за KMS-запросы.

**Q: Что такое eventual consistency в S3?**
A: Раньше S3 был eventually consistent для PUT-после-PUT и DELETE. С декабря 2020 — **strong read-after-write consistency** для всех операций. Теперь сразу после PUT виден актуальный объект.

**Q: Зачем presigned URL, если bucket приватный?**
A: Выдать временный доступ третьей стороне (клиенту, браузеру) без раздачи AWS credentials. Типичный use-case: фронтенд загружает файл напрямую в S3, минуя бэкенд.

**Q: Что если key уже есть?**
A: С versioning — создаётся новая версия, старая остаётся. Без versioning — перезаписывается без предупреждения.

**Q: Максимальный размер объекта?**
A: 5 TB. Для файлов > 100 MB использовать **multipart upload** (boto3 делает автоматически через `upload_file`).

---

## Главная мысль

S3 — не файловая система, а **key-value object store**: bucket → key (строка вроде `data/test.txt`) → объект + metadata. "Папки" — фикция, просто префиксы в ключе. Всё остальное (versioning, lifecycle, encryption) — фичи поверх этой простой модели.
