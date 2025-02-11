import subprocess


def convert_unit(size_in_bytes: int, unit):
    """Convert the size from bytes to 
    other units like KB, MB or GB
    """
    if unit == 'KB':
        return size_in_bytes/1024
    elif unit == 'MB':
        return size_in_bytes/(1024*1024)
    elif unit == 'GB':
        return size_in_bytes/(1024*1024*1024)
    else:
        return size_in_bytes


def call_with_output(command, cwd='/'):
    success = False
    print(command)
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, cwd=cwd).decode()
        success = True
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    except Exception as e:
        # check_call can raise other exceptions, such as FileNotFoundError
        output = str(e)
    print(output)
    return (success, output)
