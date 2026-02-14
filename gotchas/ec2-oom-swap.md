# EC2 OOM Kill + Swap + MySQL 튜닝

> t3.small(2GB) 같은 소규모 EC2에서 서버가 갑자기 죽을 때.
> 실제로 겪고 해결한 사례 (2026.02).
> 원문: https://pearsoninsight.com/ec2-oom-kill-swap-mysql-tuning/

## 증상

- 사이트 접속 시 **"Error establishing a database connection"**
- Cloudflare에서 **522 에러**
- AWS 콘솔: 인스턴스 연결성 검사 **실패**
- SSH 접속 **불가** (메모리 바닥)

## 원인: OOM Kill

**OOM Kill** = Out of Memory Kill. Linux 커널이 메모리 부족 시 가장 많이 쓰는 프로세스를 강제 종료.

```
트래픽 증가 (또는 봇 공격)
→ Apache/PHP 프로세스 증가
→ 메모리 부족
→ 커널: "MySQL 너 나가"
→ DB 연결 실패
→ 사이트 전체 다운
```

t3.small (2GB RAM)에 Apache + PHP + MySQL + WordPress + 웹앱 3개 = 원룸에 5명.

## 진단

### MySQL 상태 확인

```bash
systemctl status mysql
```

```
mysql.service: A process has been killed by the OOM killer.
mysql.service: Failed with result 'oom-kill'.
mysql.service: Scheduled restart job, restart counter is at 3.
Memory: 495.7M
```

### 사망 기록 확인

```bash
journalctl -u mysql --since "today" | grep -i "start\|stop\|oom"
```

### SSH 안 될 때

AWS 콘솔 → EC2 → 인스턴스 → **"인스턴스 중지"** → 대기 → **"인스턴스 시작"**

> **주의**: "종료"가 아니라 "중지"! "종료"는 인스턴스 **삭제**됨.
> Elastic IP 없으면 재시작 시 IP 변경됨 → DNS A 레코드 수정 필요.

## 1차 대응: Swap 추가 (골든타임 30초)

서버 살아나면 **즉시** Swap부터 추가. MySQL이 메모리 다시 잡아먹기 전에.

### Swap이란

디스크의 일부를 RAM처럼 사용. 느리지만 OOM Kill 방지.

### Swap 2GB 한 줄 추가

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile && echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

| 명령어 | 설명 |
|--------|------|
| `fallocate -l 2G /swapfile` | 2GB 빈 파일 생성 |
| `chmod 600 /swapfile` | root만 접근 |
| `mkswap /swapfile` | Swap으로 포맷 |
| `swapon /swapfile` | Swap 켜기 |
| `echo ... >> /etc/fstab` | 재부팅 후에도 자동 적용 |

### 확인

```bash
free -m
```

Swap에 ~2048MB 표시되면 성공. 이제 2GB + 2GB = 4GB.

## 2차 대응: MySQL 다이어트

MySQL 기본 설정은 대규모 서비스 기준. 개인 블로그에는 과함.

### 설정 파일 수정

```bash
sudo tee -a /etc/mysql/mysql.conf.d/mysqld.cnf << 'EOF'

# === 메모리 절약 설정 ===
[mysqld]
innodb_buffer_pool_size = 128M
innodb_log_buffer_size = 8M
key_buffer_size = 16M
max_connections = 30
EOF
```

| 설정 | 값 | 설명 |
|------|-----|------|
| `innodb_buffer_pool_size` | 128M | DB 캐시. 블로그는 128MB 충분 |
| `innodb_log_buffer_size` | 8M | 로그 버퍼 |
| `key_buffer_size` | 16M | 인덱스 캐시 |
| `max_connections` | 30 | 동시 접속 제한 |

### 재시작

```bash
sudo systemctl restart mysql
```

## 결과

- MySQL 메모리: 500MB → **~200MB**
- **하루 2~3번 죽던 서버가 한 번도 다운 안 됨**

## t3.small 생존 체크리스트

| 항목 | 권장 |
|------|------|
| Swap | 최소 2GB 필수 |
| MySQL 메모리 | innodb_buffer_pool_size 128MB 이하 |
| 캐시 플러그인 | WP Super Cache / W3 Total Cache |
| 모니터링 | `free -m`, `systemctl status mysql` |
| Elastic IP | 할당해두면 재시작 시 IP 안 바뀜 |
