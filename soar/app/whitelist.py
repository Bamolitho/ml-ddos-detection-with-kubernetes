def is_whitelisted(ip: str, whitelist: list):
    """
    Vérifie si une IP est whitelistée.
    Supporte les préfixes (ex: 192.168.1.)
    """
    if not ip:
        return False, None

    for rule in whitelist:
        if ip.startswith(rule):
            return True, rule

    return False, None
