# subprocess là 1 module chuẩn được sử dụng để tạo và quản lý các tiến trình con
# Module này cung cấp cách tiện lợi tương tác với hệ điều hành và chạy các lệnh shell để giao tiếp với các tiến trình con thông qua các luồng dữ liệu
# Các hàm phổ biến của module
# subprocess.run(): thực thi 1 lệnh shell và đợi cho đến khi kết thúc
# subprocess.Popen(): Tạo 1 đối tượng Popen() để thực thi 1 lệnh và kiểm soát các tiến trình con trong nó
# subprocess.check_output(): Thực thi 1 lệnh và trả về kết quả lệnh đó
import subprocess
import time

# ELT: Extract, Load and Transform pipeline. Là 1 quá trình trong xử lý dữ liệu giúp ETL để chuẩn bị cho việc phân tích và báo cáo
# Extract (trích xuất): lấy data từ các data source khác nhau. Mỗi data source có thể có 1 format khác nhau
# Load (tải lên): Sau khi dữ liệu được trích xuất, cần tải nó vào 1 hệ thống lưu trữ như cơ sở dữ liệu hoặc data warehouse
# Transform (chuyển đổi): Sau khi data được load lên, cần transform data phù hợp với mục tiêu, yêu cầu (làm sạch, kết hợp data lại, tính toán thêm các chỉ số thông tin phân tích và nhiều hoạt động khác để chuẩn bị cho trích xuất và báo cáo)

# Double check source/dest database tồn tại
def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True
            )
            if "accepting connections" in result.stdout:
                print("Successfully connected to Postgres")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to Postgres: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds ... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)
    print("Max retires reached. Exiting")
    return False

if not wait_for_postgres(host="source_postgres"):
    exit(1)
    
print("Starting ELT script ...")

# Configuration for the source PostgreSQL database
source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'source_postgres'
}

# Configuration for the destination PostgreSQL database
destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'destination_postgres'
}

# Use pg_dump to dump the source database to a SQL file
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'  # Do not prompt for password
]

# Set the PGPASSWORD environment variable to avoid password prompt
subprocess_env = dict(PGPASSWORD=source_config['password'])

# Execute the dump command
subprocess.run(dump_command, env=subprocess_env, check=True)

# Use psql to load the dumped SQL file into the destination database
load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql'
]

# Set the PGPASSWORD environment variable for the destination database
subprocess_env = dict(PGPASSWORD=destination_config['password'])

# Execute the load command
subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ELT script...")