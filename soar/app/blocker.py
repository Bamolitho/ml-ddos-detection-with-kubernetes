import subprocess
import logging

def block_ip(ip):
    try:
        subprocess.run(
            ["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            check=True
        )
        logging.info(f"IP bloquée: {ip}")
        return True
    except Exception as e:
        logging.error(f"Erreur blocage {ip}: {e}")
        return False

