from datetime import date, timedelta


# ========== НОМЕР ==========
class Room:
    def __init__(self, number, room_type, price):
        self.number = number
        self.room_type = room_type
        self.price = price
        self.is_free = True

    def info(self):
        return f"Номер {self.number} ({self.room_type}) — {self.price} руб/ночь"


# ========== ФАБРИКА ==========
class RoomFactory:
    @staticmethod
    def create(room_type):
        if room_type == "стандарт":
            return Room(101, "стандарт", 3000)
        elif room_type == "делюкс":
            return Room(201, "делюкс", 5500)
        elif room_type == "люкс":
            return Room(301, "люкс", 10000)
        else:
            print("Такого типа нет")
            return None


# ========== ОТЕЛЬ ==========
class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []

    def add_room(self, room_type):
        room = RoomFactory.create(room_type)
        if room:
            self.rooms.append(room)
            print(f"Добавлен: {room.info()}")

    def find_free_room(self, room_type):
        for room in self.rooms:
            if room.room_type == room_type and room.is_free:
                return room
        return None

    def book(self, room_type, guest, check_in, check_out):
        room = self.find_free_room(room_type)
        if not room:
            print(f"Нет свободных номеров «{room_type}»")
            return

        nights = (check_out - check_in).days
        total = room.price * nights
        room.is_free = False

        print(f"Бронь оформлена:")
        print(f"  Гость: {guest}")
        print(f"  {room.info()}")
        print(f"  С {check_in} по {check_out} ({nights} ночей)")
        print(f"  Итого: {total} руб.")
        return room


# ========== ДЕМОНСТРАЦИЯ ==========
if __name__ == "__main__":
    hotel = Hotel("Отель «Уют»")

    print("=== Создаём номера (Фабрика) ===")
    hotel.add_room("стандарт")
    hotel.add_room("делюкс")
    hotel.add_room("люкс")

    print("\n=== Бронируем ===")
    today = date.today()

    hotel.book("делюкс", "Иван Петров",
               today + timedelta(days=1),
               today + timedelta(days=4))

    print()
    hotel.book("стандарт", "Мария Сидорова",
               today,
               today + timedelta(days=2))