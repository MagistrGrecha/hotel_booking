from datetime import date, timedelta
from abc import ABC, abstractmethod


# Блок Observer

class Observer(ABC):
    @abstractmethod
    def update(self, message: str):
        pass


class ConsoleObserver(Observer):
    def update(self, message: str):
        print(f"[Уведомление] {message}")


class LogObserver(Observer):
    def __init__(self, filename: str = "hotel.log"):
        self.filename = filename

    def update(self, message: str):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(message + "\n")
        print(f"[Лог] Записано в {self.filename}: {message}")


# Блок создния комнат

class Room:
    def __init__(self, number: int, room_type: str, price: int):
        self.number = number
        self.room_type = room_type
        self.price = price
        self.is_free = True

    def info(self) -> str:
        status = "свободен" if self.is_free else "занят"
        return f"Номер {self.number} ({self.room_type}) — {self.price} руб/ночь [{status}]"


# Блок Фабрик созданий комнат

class RoomFactory:
    _counters = {
        "стандарт": 100,
        "делюкс": 200,
        "люкс": 300,
    }

    @staticmethod
    def create(room_type: str) -> Room | None:
        room_type = room_type.lower()
        if room_type not in RoomFactory._counters:
            print(f"Такого типа номера нет: {room_type}")
            return None

        RoomFactory._counters[room_type] += 1
        number = RoomFactory._counters[room_type]

        prices = {
            "стандарт": 3000,
            "делюкс": 5500,
            "люкс": 10000,
        }
        return Room(number, room_type, prices[room_type])


# Блок бронирования комнат

class Booking:
    def __init__(self, room: Room, guest: str, check_in: date, check_out: date):
        if check_out <= check_in:
            raise ValueError("Дата выезда должна быть позже даты заезда")

        self.room = room
        self.guest = guest
        self.check_in = check_in
        self.check_out = check_out
        self.nights = (check_out - check_in).days
        self.total = room.price * self.nights

        room.is_free = False

    def info(self) -> str:
        return (
            f"Гость: {self.guest}\n"
            f"  {self.room.info()}\n"
            f"  С {self.check_in} по {self.check_out} ({self.nights} ночей)\n"
            f"  Итого: {self.total} руб."
        )


# Блок Отель основная структур

class Hotel:
    def __init__(self, name: str):
        self.name = name
        self.rooms: list[Room] = []
        self.bookings: list[Booking] = []
        self.observers: list[Observer] = []

    def add_observer(self, observer: Observer):
        self.observers.append(observer)

    def remove_observer(self, observer: Observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self, message: str):
        for obs in self.observers:
            obs.update(message)

    def add_room(self, room_type: str):
        room = RoomFactory.create(room_type)
        if room:
            self.rooms.append(room)
            print(f"Добавлен: {room.info()}")

    def find_free_room(self, room_type: str) -> Room | None:
        for room in self.rooms:
            if room.room_type == room_type and room.is_free:
                return room
        return None

    def book(self, room_type: str, guest: str, check_in: date, check_out: date) -> Booking | None:
        room = self.find_free_room(room_type)
        if room is None:
            print(f"Нет свободных номеров типа «{room_type}»")
            return None

        booking = Booking(room, guest, check_in, check_out)
        self.bookings.append(booking)
        self.notify(f"Новое бронирование: {guest} → {room.info()}")
        return booking

    def cancel_booking(self, room_number: int) -> bool:
        """Освобождает номер по его номеру и уведомляет наблюдателей."""
        for booking in self.bookings:
            if booking.room.number == room_number:
                booking.room.is_free = True
                self.bookings.remove(booking)
                self.notify(
                    f"Бронирование отменено. Номер {room_number} "
                    f"({booking.room.room_type}) снова свободен. "
                    f"Гость: {booking.guest}"
                )
                return True
        print(f"Бронирование для номера {room_number} не найдено")
        return False

    def show_free(self):
        print(f"\nСвободные номера в «{self.name}»:")
        free = [r for r in self.rooms if r.is_free]
        if not free:
            print("  Нет свободных")
        else:
            for r in free:
                print(f"  • {r.info()}")


# Блок Main

if __name__ == "__main__":
    hotel = Hotel("Отель «Уют»")

    # Подключаем наблюдателей
    console_obs = ConsoleObserver()
    log_obs = LogObserver()
    hotel.add_observer(console_obs)
    hotel.add_observer(log_obs)

    print("=== 1. Создаём 3 номера через фабрику ===")
    hotel.add_room("стандарт")
    hotel.add_room("делюкс")
    hotel.add_room("люкс")

    hotel.show_free()

    print("\n=== 2. Бронируем все 3 номера (мест больше нет) ===")
    today = date.today()

    b1 = hotel.book("стандарт", "Иван Петров",
                    today + timedelta(days=1),
                    today + timedelta(days=3))
    if b1:
        print(b1.info())

    print()
    b2 = hotel.book("делюкс", "Мария Иванова",
                    today,
                    today + timedelta(days=2))
    if b2:
        print(b2.info())

    print()
    b3 = hotel.book("люкс", "Алексей Сидоров",
                    today + timedelta(days=2),
                    today + timedelta(days=5))
    if b3:
        print(b3.info())

    hotel.show_free()   # должно показать "Нет свободных"

    print("\n=== 3. Освобождаем один номер (отмена бронирования) ===")

    # Освобождаем делюкс (номер 201)
    hotel.cancel_booking(201)

    hotel.show_free()

    print("\n=== 4. Бронируем освободившийся номер новым гостем ===")
    b4 = hotel.book("делюкс", "Ольга Кузнецова",
                    today + timedelta(days=1),
                    today + timedelta(days=4))
    if b4:
        print(b4.info())

    hotel.show_free()
