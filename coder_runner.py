import os
import tempfile
import docker

client = docker.from_env()

def run_code(code, language):
    # 定义各语言的文件名和运行命令
    language_config = {
        'python': {
            'filename': 'main.py',
            'command': 'timeout 10 python3 /code/main.py'
        },
        'javascript': {
            'filename': 'main.js',
            'command': 'timeout 10 node /code/main.js'
        },
        'java': {
            'filename': 'Main.java',
            'command': 'timeout 10 sh -c "javac -d /tmp /code/Main.java && java -cp /tmp Main"'
        },
        'golang': {
            'filename': 'main.go',
            'command': 'timeout 10 GO111MODULE=auto go run /code/main.go'
        },
        'c': {
            'filename': 'main.c',
            'command': 'timeout 10 sh -c "gcc /code/main.c -o /tmp/main && /tmp/main"'
        },
        'cpp': {
            'filename': 'main.cpp',
            'command': 'timeout 10 sh -c "g++ /code/main.cpp -o /tmp/main && /tmp/main"'
        }
    }

    # 检查语言是否支持
    if language not in language_config:
        return {'error': 'Unsupported language'}

    config = language_config[language]
    filename = config['filename']
    command = config['command']

    # 创建临时目录并写入代码文件
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w') as f:
            f.write(code)

        # 配置Docker卷
        volumes = {temp_dir: {'bind': '/code', 'mode': 'ro'}}

        try:
            # 运行Docker容器
            container_output = client.containers.run(
                image='code-runner',
                command=command,
                volumes=volumes,
                remove=True,
                stdout=True,
                stderr=True,
                mem_limit='100m',
                cpu_period=100000,
                cpu_quota=50000,
                detach=False
            )
            output = container_output.decode('utf-8').strip()
            return {'output': output}
        except docker.errors.ContainerError as e:
            error_msg = e.stderr.decode('utf-8').strip() if e.stderr else str(e)
            return {'error': error_msg}
        except Exception as e:
            return {'error': str(e)}

# 示例用法
if __name__ == "__main__":
    # 测试Python代码
    python_code = 'print("Hello from Python!")'
    result = run_code(python_code, 'python')
    print("Python Result:", result)

    # 测试Java代码
    java_code = '''
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello from Java!");
        }
    }
    '''
    result = run_code(java_code, 'java')
    print("Java Result:", result)
