from garminconnect import Garmin

def garmin_login(email, password):
    """
    Loggt sich bei Garmin Connect ein und gibt ein Garmin-Objekt zurück.
    """
    try:
        client = Garmin(email, password)
        client.login()
        return client
    except Exception as e:
        print("Fehler beim Garmin-Login:", e)
        return None
