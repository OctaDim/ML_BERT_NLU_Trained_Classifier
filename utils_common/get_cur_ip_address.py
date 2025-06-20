import socket


def get_cur_internal_ip(log_ip: bool = True) -> str:
    try:
        hostname = socket.gethostname()
        cur_internal_ip = socket.gethostbyname(hostname)
        if log_ip:
            print(f"Current INTERNAL IP: {cur_internal_ip}")
        return cur_internal_ip
    except Exception as error:
        return f"Getting internal IP [ERROR]: {error}"


def get_cur_external_ip_via_google_dns(log_ip: bool = True):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cur_socket:
            cur_socket.connect(("8.8.8.8", 80))
            cur_external_ip = cur_socket.getsockname()[0]
            # cur_socket.close()
            if log_ip:
                print(f"Current EXTERNAL IP: {cur_external_ip}")
            return cur_external_ip
    except Exception as error:
        return f"Getting external IP [ERROR]: {error}"
