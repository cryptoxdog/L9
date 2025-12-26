/opt/l9$ bash deploy/vps-mri.sh
╔════════════════════════════════════════════════════════════════╗
║           L9 VPS MRI - COMPLETE SYSTEM DIAGNOSTIC              ║
╚════════════════════════════════════════════════════════════════╝
Timestamp: 2025-12-21T05:39:10+00:00
Hostname:  L9
User:      admin


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A1. SYSTEM IDENTITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Linux L9 6.8.0-88-generic #89-Ubuntu SMP PREEMPT_DYNAMIC Sat Oct 11 01:02:46 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux
    inet 127.0.0.1/8 scope host lo
    inet 157.180.73.53/32 metric 100 scope global dynamic eth0
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A2. DISK SPACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/dev/sda1        38G   31G  5.1G  86% /
/dev/sda1        38G   31G  5.1G  86% /
/dev/sda1        38G   31G  5.1G  86% /


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A3. MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       909Mi       202Mi        26Mi       3.0Gi       2.8Gi
Swap:             0B          0B          0B


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A4. LOAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 05:39:10 up 6 days,  2:39,  2 users,  load average: 0.34, 0.28, 0.28


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B1. ALL LISTENING PORTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[sudo] password for admin: 
LISTEN 0      4096      127.0.0.54:53        0.0.0.0:*    users:(("systemd-resolve",pid=656,fd=17))
LISTEN 0      2048         0.0.0.0:8000      0.0.0.0:*    users:(("uvicorn",pid=99330,fd=11))      
LISTEN 0      200       172.17.0.1:5432      0.0.0.0:*    users:(("postgres",pid=84076,fd=8))      
LISTEN 0      4096       127.0.0.1:2019      0.0.0.0:*    users:(("caddy",pid=9230,fd=10))         
LISTEN 0      2048       127.0.0.1:8100      0.0.0.0:*    users:(("python",pid=362268,fd=13))      
LISTEN 0      128          0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=954,fd=3))            
LISTEN 0      4096   127.0.0.53%lo:53        0.0.0.0:*    users:(("systemd-resolve",pid=656,fd=15))
LISTEN 0      200        127.0.0.1:5432      0.0.0.0:*    users:(("postgres",pid=84076,fd=7))      
LISTEN 0      4096         0.0.0.0:631       0.0.0.0:*    users:(("cupsd",pid=1349,fd=9))          
LISTEN 0      4096               *:443             *:*    users:(("caddy",pid=9230,fd=7))          
LISTEN 0      128             [::]:22           [::]:*    users:(("sshd",pid=954,fd=4))            
LISTEN 0      4096               *:80              *:*    users:(("caddy",pid=9230,fd=11))         
LISTEN 0      200            [::1]:5432         [::]:*    users:(("postgres",pid=84076,fd=6))      
LISTEN 0      4096            [::]:631          [::]:*    users:(("cupsd",pid=1349,fd=10))         


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B2. CRITICAL PORTS CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Port 80 (HTTP):
LISTEN 0      4096               *:80              *:*    users:(("caddy",pid=9230,fd=11))         
Port 443 (HTTPS):
LISTEN 0      4096               *:443             *:*    users:(("caddy",pid=9230,fd=7))          
Port 5432 (PostgreSQL):
LISTEN 0      200       172.17.0.1:5432      0.0.0.0:*    users:(("postgres",pid=84076,fd=8))      
LISTEN 0      200        127.0.0.1:5432      0.0.0.0:*    users:(("postgres",pid=84076,fd=7))      
LISTEN 0      200            [::1]:5432         [::]:*    users:(("postgres",pid=84076,fd=6))      
Port 6379 (Redis):
  Not listening
Port 7687 (Neo4j Bolt):
  Not listening
Port 8000 (L9 API):
LISTEN 0      2048         0.0.0.0:8000      0.0.0.0:*    users:(("uvicorn",pid=99330,fd=11))      


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B3. FIREWALL (UFW)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] OpenSSH                    ALLOW IN    Anywhere                  
[ 2] 80/tcp                     ALLOW IN    Anywhere                  
[ 3] 22/tcp                     ALLOW IN    Anywhere                  
[ 4] 443/tcp                    ALLOW IN    Anywhere                  
[ 5] OpenSSH (v6)               ALLOW IN    Anywhere (v6)             
[ 6] 80/tcp (v6)                ALLOW IN    Anywhere (v6)             
[ 7] 22/tcp (v6)                ALLOW IN    Anywhere (v6)             
[ 8] 443/tcp (v6)               ALLOW IN    Anywhere (v6)             



━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
C1. CADDY STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Caddy is RUNNING
● caddy.service - Caddy
     Loaded: loaded (/usr/lib/systemd/system/caddy.service; enabled; preset: enabled)
    Drop-In: /etc/systemd/system/caddy.service.d
             └─network-access.conf
     Active: active (running) since Mon 2025-12-15 04:20:46 UTC; 6 days ago


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
C2. CADDYFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Caddyfile exists
l9.quantumaipartners.com {
	encode gzip

	# Core

	reverse_proxy /health 127.0.0.1:8000

	reverse_proxy /docs* 127.0.0.1:8000

	reverse_proxy /openapi.json 127.0.0.1:8000

	# L9 routes (keep even if not all exist yet)

	reverse_proxy /memory* 127.0.0.1:8000

	reverse_proxy /twilio* 127.0.0.1:8000

	reverse_proxy /waba* 127.0.0.1:8000
	reverse_proxy /slack/* 127.0.0.1:8000

	# Default

	reverse_proxy 127.0.0.1:8000
}


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
C3. NGINX STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nginx not running or not installed


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D1. DOCKER VERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Docker version 29.1.1, build 0aedba5
Docker Compose version v2.40.3


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D2. DOCKER SERVICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Docker daemon is RUNNING


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D3. RUNNING CONTAINERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NAMES     STATUS                  PORTS
l9-api    Up 5 days (healthy)     
l9_api    Exited (1) 5 days ago   


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D4. DOCKER IMAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPOSITORY          TAG              SIZE
docker-l9-api       latest           2.1GB
runtime-l9_api      latest           1.84GB
l9-runtime          latest           500MB
qdrant/qdrant       latest           276MB
pgvector/pgvector   pg16             723MB
redis               7-alpine         60.7MB
neo4j               5.14-community   797MB


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D5. DOCKER NETWORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NETWORK ID     NAME              DRIVER    SCOPE
76452e34c146   bridge            bridge    local
ecd2c8da6592   docker_default    bridge    local
6d99286f4924   host              host      local
9a38c0e6ab3a   none              null      local
697daec0a3ce   runtime_default   bridge    local
b85f05ad78cb   runtime_l9net     bridge    local


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
E1. L9 INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ /opt/l9 exists
total 388
drwxr-xr-x 41 admin admin  4096 Dec 21 05:26 .
drwxr-xr-x  6 root  root   4096 Dec 15 02:53 ..
-rw-rw-r--  1 admin admin    99 Dec 15 14:52 =0.104.0
-rw-rw-r--  1 admin admin     0 Dec 15 14:52 =0.24.0
drwxr-xr-x  2 admin admin  4096 Dec 21 05:26 agents
drwxr-xr-x  6 admin admin  4096 Dec 21 05:37 api
-rw-r--r--  1 admin admin   329 Dec 15 02:53 api_surfaces.txt
-rw-r--r--  1 admin admin  1518 Dec 15 02:53 architecture.txt
-rw-rw-r--  1 admin admin  3479 Dec 21 05:26 archive_perplexity_dryrun.sh
-rw-rw-r--  1 admin admin  3371 Dec 21 05:26 archive_perplexity.sh
drwxrwxr-x  2 admin admin  4096 Dec 21 05:26 ci
-rw-r--r--  1 admin admin 44922 Dec 15 02:53 class_definitions.txt
drwxr-xr-x  2 admin admin  4096 Dec 15 02:53 clients
drwxr-xr-x  2 admin admin  4096 Dec 15 02:53 collaborative_cells


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
E2. L9 SYSTEMD SERVICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ l9.service exists
● l9.service - L9 Phase 2 AI OS Kernel (Secure + Logging)
     Loaded: loaded (/etc/systemd/system/l9.service; disabled; preset: enabled)
    Drop-In: /etc/systemd/system/l9.service.d
             └─environment.conf, override.conf, relax-protect.conf, twilio.conf, waba.conf
     Active: activating (auto-restart) (Result: exit-code) since Sun 2025-12-21 05:39:16 UTC; 1s ago
    Process: 809754 ExecStart=/opt/l9/venv/bin/python -m uvicorn api.server_memory:app --host 127.0.0.1 --port 8000 (code=exited, status=1/FAILURE)
   Main PID: 809754 (code=exited, status=1/FAILURE)
        CPU: 1.550s