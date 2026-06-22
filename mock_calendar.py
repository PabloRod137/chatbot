import random
from datetime import datetime, timedelta

def check_availability(game_name: str, requested_date: str) -> str:
    """
    Mock que simula la disponibilidad de las salas o servicios.
    En una aplicación real, esto conectaría con la API del calendario de reservas (ej. Bookeo, TuCita, etc.).
    """
    # Lista de horas posibles para simular
    posibles_horas = ["10:00", "12:00", "16:00", "18:00", "20:00"]
    
    # Elegir aleatoriamente algunas horas disponibles
    horas_disponibles = random.sample(posibles_horas, k=random.randint(1, 3))
    
    if game_name and game_name != "consulta general":
        return f"Para '{game_name}' en la fecha {requested_date}, tenemos disponibilidad a las: {', '.join(horas_disponibles)}."
    else:
        return f"Para la fecha {requested_date}, tenemos disponibilidad general a las: {', '.join(horas_disponibles)}."
