import json
from collector import collect_metrics
from client import send_metrics
from config import settings
import time
import httpx

# print(json.dumps(collect_metrics(), indent=4, ensure_ascii=False))
def main():
    while True:
        try:
            metrics = collect_metrics(settings.service_names)
            send_metrics(metrics)
            print("Метрики отправлены")
        except httpx.HTTPStatusError as error:
            print(error.response.status_code)
        except httpx.RequestError:
            print("Мтерики не были отправлены")
        except OSError:
            print("Ошибка при сборе метрик")
        
        print(metrics)
        
        time.sleep(settings.send_interval_seconds)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Агент остановлен")